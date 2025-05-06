#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ST股票信息模块

提供获取和更新ST股票信息的功能
"""

import pandas as pd
from typing import Optional, Dict
from datetime import datetime, timedelta
import math

from datawhale.domain_pro.tushare_config import get_pro_api
from datawhale.domain_pro.field_standard import StandardFields, get_fields_type
from datawhale.domain_pro import standardize_dataframe
from datawhale.domain_pro.datetime_standard import to_standard_date
from datawhale.infrastructure_pro.storage import (
    dw_create_dataset,
    dw_save,
    dw_exists,
    dw_query,
)
from datawhale.infrastructure_pro.logging import get_user_logger

# 获取用户日志记录器
logger = get_user_logger(__name__)

# TuShare数据源名称
TUSHARE_SOURCE = "tushare"

# ST股票信息数据集名称
ST_INFO_DATASET = "st_info"

# 需要保留的标准字段列表
REQUIRED_COLUMNS = [
    StandardFields.CODE,  # 证券代码
    StandardFields.NAME,  # 证券名称
    StandardFields.START_DATE,  # 变更开始日期
    StandardFields.END_DATE,  # 变更结束日期
    StandardFields.CHANGE_REASON,  # 变更原因
    StandardFields.IS_ST,  # 是否ST
]

# 日期字段列表
DATE_COLUMNS = [StandardFields.START_DATE, StandardFields.END_DATE]


def fetch_st_info(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取指定日期范围内的ST股票信息

    Args:
        start_date: 开始日期，格式为YYYYMMDD或YYYY-MM-DD
        end_date: 结束日期，格式为YYYYMMDD或YYYY-MM-DD

    Returns:
        pd.DataFrame: 包含ST股票信息的DataFrame
    """
    try:
        # 参数处理
        if start_date and "-" in start_date:
            start_date = start_date.replace("-", "")

        if end_date and "-" in end_date:
            end_date = end_date.replace("-", "")

        logger.info(f"开始获取ST股票信息: start_date={start_date}, end_date={end_date}")

        # 获取tushare pro API对象
        pro = get_pro_api()
        if pro is None:
            logger.error("获取TuShare Pro API失败")
            return pd.DataFrame()

        # 调用namechange接口获取ST股票信息
        # 根据参数构建查询条件
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        # 查询数据
        df = pro.namechange(**params)

        # 记录结果信息
        if df is not None and not df.empty:
            # 添加is_st列，根据name中是否包含ST来设置
            df["is_st"] = df["name"].str.contains("ST", na=False).astype(int)

            # 筛选ST股票
            st_df = df[df["is_st"] == 1]

            # 保存原始的ann_date列
            ann_date = None
            if "ann_date" in st_df.columns:
                ann_date = st_df["ann_date"].copy()

            # 使用合并后的标准化方法处理数据
            st_df = standardize_dataframe(
                df=st_df,
                source=TUSHARE_SOURCE,
                code_field="ts_code",  # TuShare原始代码字段名
                date_fields=DATE_COLUMNS,
                required_columns=REQUIRED_COLUMNS,
                sort_by=[
                    StandardFields.CODE,
                    StandardFields.START_DATE,
                ],  # 按照证券代码和开始日期排序
            )

            # 如果有ann_date列，添加回标准化后的DataFrame
            if ann_date is not None and len(ann_date) == len(st_df):
                st_df["ann_date"] = ann_date

            logger.info(
                f"成功获取ST股票信息，原始数据{len(df)}条，ST股票{len(st_df)}条"
            )
            return st_df
        else:
            logger.warning("获取ST股票信息为空")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"获取ST股票信息失败: {str(e)}")
        return pd.DataFrame()


def save_st_info(data: pd.DataFrame, data_name: str = ST_INFO_DATASET) -> bool:
    """
    保存ST股票信息到数据集

    Args:
        data: ST股票信息DataFrame
        data_name: 数据集名称，默认为st_info

    Returns:
        bool: 保存是否成功
    """
    if data is None or data.empty:
        logger.warning("无ST股票数据需要保存")
        return False

    logger.info(f"开始保存ST股票信息: 共{len(data)}条记录")

    try:
        # 检查数据集是否存在，不存在则创建
        if not dw_exists(data_name):
            # 获取字段类型信息
            dtypes = get_fields_type(data.columns)

            # 创建数据集
            dw_create_dataset(
                name=data_name,
                dtypes=dtypes,
                update_mode="append",  # 采用追加模式
            )
            logger.info(f"创建ST股票信息数据集: {data_name}")

        # 保存数据，不做额外的列名转换
        data_to_save = data.copy()

        # 保存数据
        dw_save(
            data=data_to_save,
            data_name=data_name,
            mode="append",  # 使用追加模式
        )

        logger.info(f"保存ST股票信息成功: 共{len(data)}条记录")
        return True
    except Exception as e:
        logger.error(f"保存ST股票信息失败: {str(e)}")
        return False


def download_st_info_by_period(
    start_date: str, end_date: str, data_name: str = ST_INFO_DATASET
) -> bool:
    """
    按周期下载ST股票信息

    如果日期范围超过一年，将按年进行分段下载

    Args:
        start_date: 开始日期，格式为YYYYMMDD或YYYY-MM-DD
        end_date: 结束日期，格式为YYYYMMDD或YYYY-MM-DD
        data_name: 数据集名称，默认为st_info

    Returns:
        bool: 下载是否成功
    """
    # 标准化日期格式
    if "-" in start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_date_obj = datetime.strptime(start_date, "%Y%m%d")

    if "-" in end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_date_obj = datetime.strptime(end_date, "%Y%m%d")

    # 计算日期范围的天数
    days_diff = (end_date_obj - start_date_obj).days

    # 如果日期范围小于等于一年，直接下载
    if days_diff <= 365:
        df = fetch_st_info(start_date=start_date, end_date=end_date)
        if df.empty:
            logger.warning(f"未获取到日期范围为{start_date}至{end_date}的ST股票信息")
            return False
        return save_st_info(df, data_name)

    # 如果日期范围超过一年，按年分段下载
    logger.info(
        f"日期范围超过一年，将按年分段下载ST股票信息: 从{start_date}到{end_date}"
    )

    # 计算需要分多少段
    years_span = math.ceil(days_diff / 365)
    success_count = 0

    for i in range(years_span):
        period_start_date = (start_date_obj + timedelta(days=i * 365)).strftime(
            "%Y%m%d"
        )

        # 计算该段的结束日期
        if i == years_span - 1:
            # 最后一段使用指定的结束日期
            period_end_date = end_date_obj.strftime("%Y%m%d")
        else:
            # 中间段落的结束日期为当前起始日期加364天
            period_end_date = (
                datetime.strptime(period_start_date, "%Y%m%d") + timedelta(days=364)
            ).strftime("%Y%m%d")

        logger.info(
            f"下载第{i+1}/{years_span}段ST股票信息: 从{period_start_date}到{period_end_date}"
        )

        # 获取并保存该段数据
        df = fetch_st_info(start_date=period_start_date, end_date=period_end_date)
        if not df.empty:
            if save_st_info(df, data_name):
                success_count += 1
        else:
            logger.warning(
                f"未获取到日期范围为{period_start_date}至{period_end_date}的ST股票信息"
            )

    logger.info(f"ST股票信息下载完成: 总共{years_span}段，成功{success_count}段")
    return success_count > 0


def query_st_info(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ts_code: Optional[str] = None,
    is_st: Optional[int] = 1,  # 默认只查询ST股票
    data_name: str = ST_INFO_DATASET,
) -> pd.DataFrame:
    """
    查询ST股票信息

    Args:
        start_date: 开始日期，格式为YYYYMMDD或YYYY-MM-DD
        end_date: 结束日期，格式为YYYYMMDD或YYYY-MM-DD
        ts_code: 股票代码，用于在本地数据中筛选特定股票
        is_st: 是否为ST股票，1表示是，0表示否，默认为1只返回ST股票
        data_name: 数据集名称，默认为st_info

    Returns:
        pd.DataFrame: 包含ST股票信息的DataFrame
    """
    logger.info(
        f"开始查询ST股票信息: start_date={start_date}, end_date={end_date}, ts_code={ts_code}, is_st={is_st}"
    )

    try:
        # 检查数据集是否存在
        if not dw_exists(data_name):
            logger.warning(f"数据集{data_name}不存在，将从远程获取数据")
            return fetch_st_info(start_date=start_date, end_date=end_date)

        # 查询本地数据
        df = dw_query(data_name)

        if df is None or df.empty:
            logger.warning(f"本地数据集{data_name}为空，将从远程获取数据")
            return fetch_st_info(start_date=start_date, end_date=end_date)

        # 筛选数据
        filtered_df = df.copy()

        # 标准化日期格式
        if start_date:
            if "-" in start_date:
                start_date = start_date.replace("-", "")
            filtered_df = filtered_df[
                filtered_df[StandardFields.START_DATE] >= start_date
            ]

        if end_date:
            if "-" in end_date:
                end_date = end_date.replace("-", "")
            # 对于end_date为None的记录，我们认为它们仍然有效
            filtered_df = filtered_df[
                (filtered_df[StandardFields.END_DATE] >= end_date)
                | (filtered_df[StandardFields.END_DATE].isna())
            ]

        if ts_code:
            filtered_df = filtered_df[filtered_df[StandardFields.CODE] == ts_code]

        # 根据is_st参数筛选
        if is_st is not None:
            filtered_df = filtered_df[filtered_df[StandardFields.IS_ST] == is_st]

        logger.info(f"查询ST股票信息完成: 共{len(filtered_df)}条记录")
        return filtered_df
    except Exception as e:
        logger.error(f"查询ST股票信息失败: {str(e)}")
        return pd.DataFrame()


def update_st_info(days: int = 365) -> bool:
    """
    更新ST股票信息

    获取最近指定天数内的ST股票信息并更新到存储系统

    Args:
        days: 更新的天数范围，默认为365天

    Returns:
        bool: 更新是否成功
    """
    try:
        # 计算日期范围
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

        logger.info(f"开始更新ST股票信息: 日期范围从{start_date}到{end_date}")

        # 获取并保存数据
        df = fetch_st_info(start_date=start_date, end_date=end_date)

        if not df.empty:
            return save_st_info(df)
        else:
            logger.warning(
                f"未获取到日期范围为{start_date}至{end_date}的ST股票信息，无数据更新"
            )
            return False
    except Exception as e:
        logger.error(f"更新ST股票信息失败: {str(e)}")
        return False
