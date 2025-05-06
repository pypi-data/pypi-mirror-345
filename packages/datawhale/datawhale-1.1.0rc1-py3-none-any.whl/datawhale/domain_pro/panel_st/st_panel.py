#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ST股票面板数据处理模块

计算和存储ST股票面板数据的功能实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from tqdm import tqdm  # 导入tqdm进度条库

# 导入相关模块
from datawhale.domain_pro.info_st import query_st_info, ST_INFO_DATASET
from datawhale.domain_pro.info_trade_calendar import (
    get_trade_calendar_info,
    get_trading_days,
    TRADE_CALENDAR_DATASET,
)
from datawhale.domain_pro.field_standard import StandardFields
from datawhale.infrastructure_pro.storage import (
    dw_query,
    dw_exists,
    panel_create,
    panel_save,
    panel_query,
    panel_exists,
    panel_get_all_entities,
    dw_create_panel,
    dw_panel_save,
    dw_panel_query,
    dw_panel_exists,
    dw_panel_delete,
)

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)

# 定义面板数据名称
ST_PANEL_NAME = "panel_st"

# 定义ST状态值
ST_STATUS_NORMAL = 0  # 正常，非ST状态
ST_STATUS_ST = 1  # ST状态


def create_st_panel(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> bool:
    """
    创建并保存ST股票面板数据

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        bool: 创建是否成功
    """
    logger.info(f"开始创建ST股票面板数据: start_date={start_date}, end_date={end_date}")

    try:
        # 检查结束日期是否超过当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        if end_date is not None and end_date > current_date:
            logger.warning(
                f"结束日期({end_date})超过当前日期({current_date})，将使用当前日期作为结束日期"
            )
            end_date = current_date

        # 1. 加载交易日历
        logger.debug("加载交易日历数据")
        calendar_df = dw_query(TRADE_CALENDAR_DATASET)
        if calendar_df.empty:
            logger.error("交易日历数据为空，无法计算ST股票状态")
            return False

        # 过滤交易日
        calendar_df = calendar_df[calendar_df[StandardFields.IS_TRADING_DAY] == 1]

        # 如果未指定日期范围，使用交易日历中的最早和最晚日期
        if start_date is None:
            start_date = calendar_df[StandardFields.CALENDAR_DATE].min()
        if end_date is None:
            # 使用交易日历中的最晚日期，但不超过当前日期
            calendar_max_date = calendar_df[StandardFields.CALENDAR_DATE].max()
            end_date = min(calendar_max_date, current_date)

        # 过滤日期范围
        calendar_df = calendar_df[
            (calendar_df[StandardFields.CALENDAR_DATE] >= start_date)
            & (calendar_df[StandardFields.CALENDAR_DATE] <= end_date)
        ]

        if calendar_df.empty:
            logger.error(
                f"指定日期范围内没有交易日: start_date={start_date}, end_date={end_date}"
            )
            return False

        # 获取交易日列表
        trading_dates = calendar_df[StandardFields.CALENDAR_DATE].tolist()
        logger.info(f"日期范围内总交易日数量: {len(trading_dates)}")

        # 2. 加载ST股票信息
        logger.debug("加载ST股票信息数据")
        st_df = dw_query(ST_INFO_DATASET)
        if st_df.empty:
            logger.error("ST股票信息数据为空，无法计算ST股票状态")
            return False

        # 确保所有字段名大写并符合标准
        st_df.columns = [col.upper() for col in st_df.columns]

        # 确保日期格式正确
        for date_field in ["START_DATE", "END_DATE"]:
            if date_field in st_df.columns:
                # 标准化日期格式为YYYY-MM-DD
                st_df[date_field] = pd.to_datetime(st_df[date_field]).dt.strftime(
                    "%Y-%m-%d"
                )
                # 处理可能的NaT
                st_df[date_field] = st_df[date_field].fillna("")

        # 获取所有股票代码
        stock_codes = st_df["CODE"].unique().tolist()
        logger.info(f"ST股票代码数量: {len(stock_codes)}")

        # 如果面板数据不存在，则创建
        if not dw_panel_exists(ST_PANEL_NAME):
            panel = dw_create_panel(
                name=ST_PANEL_NAME,
                index_col=StandardFields.TRADE_DATE,
                entity_col_name="entity_id",
                value_dtype="int",  # 使用整数类型表示ST状态
                update_mode="update",  # 使用更新模式
            )
            logger.info(f"创建ST股票面板数据集: {ST_PANEL_NAME}")

        # 3. 计算ST股票状态
        logger.debug("开始计算ST股票状态")

        # 创建一个空的面板DataFrame，索引为交易日，列为股票代码
        panel_df = pd.DataFrame(
            index=trading_dates,
            columns=stock_codes,
            data=ST_STATUS_NORMAL,  # 默认为正常状态(0)
        )

        # 设置索引名称
        panel_df.index.name = StandardFields.TRADE_DATE

        # 遍历ST记录，将ST期间内的交易日标记为ST状态(1)
        for _, row in tqdm(st_df.iterrows(), desc="处理ST记录", total=len(st_df)):
            code = row["CODE"]
            start = row["START_DATE"]
            end = (
                row["END_DATE"]
                if row["END_DATE"] and row["END_DATE"] != "nan"
                else end_date
            )

            # 确保日期格式正确
            if pd.isna(start) or not start:
                continue

            # 获取此期间内的所有交易日
            period_dates = [date for date in trading_dates if start <= date <= end]

            # 标记这些日期为ST状态
            for date in period_dates:
                panel_df.loc[date, code] = ST_STATUS_ST

        # 4. 保存面板数据
        logger.debug("开始保存ST股票面板数据")

        # 重置索引以便将日期转为列
        panel_df = panel_df.reset_index()

        # 将数据从宽格式转为长格式
        panel_data = pd.melt(
            panel_df,
            id_vars=[StandardFields.TRADE_DATE],
            var_name="entity_id",
            value_name="value",
        )

        # 保存面板数据，根据interface.py中dw_panel_save的定义
        dw_panel_save(
            data=panel_data,
            panel_name=ST_PANEL_NAME,
            mode="overwrite",  # 使用覆盖模式，有效值为'overwrite'、'append'或'update'
        )

        logger.info(
            f"ST股票面板数据创建并保存成功: 日期范围={start_date}至{end_date}, 股票数量={len(stock_codes)}"
        )
        return True

    except Exception as e:
        logger.error(f"创建ST股票面板数据失败: {str(e)}")
        return False


def update_st_panel(days: int = 30) -> bool:
    """
    更新ST股票面板数据

    Args:
        days: 需要更新的最近天数，默认为30天

    Returns:
        bool: 更新是否成功
    """
    logger.info(f"开始更新ST股票面板数据: 最近{days}天")

    try:
        # 计算开始日期和结束日期
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 检查结束日期是否超过当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        if end_date > current_date:
            logger.warning(
                f"结束日期({end_date})超过当前日期({current_date})，将使用当前日期作为结束日期"
            )
            end_date = current_date

        # 1. 加载交易日历
        logger.debug("加载交易日历数据")
        calendar_df = dw_query(TRADE_CALENDAR_DATASET)
        if calendar_df.empty:
            logger.error("交易日历数据为空，无法计算ST股票状态")
            return False

        # 过滤交易日
        calendar_df = calendar_df[calendar_df[StandardFields.IS_TRADING_DAY] == 1]

        # 过滤日期范围
        calendar_df = calendar_df[
            (calendar_df[StandardFields.CALENDAR_DATE] >= start_date)
            & (calendar_df[StandardFields.CALENDAR_DATE] <= end_date)
        ]

        if calendar_df.empty:
            logger.error(
                f"指定日期范围内没有交易日: start_date={start_date}, end_date={end_date}"
            )
            return False

        # 获取交易日列表
        trading_dates = calendar_df[StandardFields.CALENDAR_DATE].tolist()
        logger.info(f"更新日期范围内总交易日数量: {len(trading_dates)}")

        # 2. 加载ST股票信息
        logger.debug("加载ST股票信息数据")
        st_df = dw_query(ST_INFO_DATASET)
        if st_df.empty:
            logger.error("ST股票信息数据为空，无法计算ST股票状态")
            return False

        # 确保所有字段名大写并符合标准
        st_df.columns = [col.upper() for col in st_df.columns]

        # 确保日期格式正确
        for date_field in ["START_DATE", "END_DATE"]:
            if date_field in st_df.columns:
                # 标准化日期格式为YYYY-MM-DD
                st_df[date_field] = pd.to_datetime(st_df[date_field]).dt.strftime(
                    "%Y-%m-%d"
                )
                # 处理可能的NaT
                st_df[date_field] = st_df[date_field].fillna("")

        # 获取所有股票代码
        stock_codes = st_df["CODE"].unique().tolist()
        logger.info(f"ST股票代码数量: {len(stock_codes)}")

        # 检查面板数据是否存在，不存在则先创建
        if not dw_panel_exists(ST_PANEL_NAME):
            logger.info(f"面板数据不存在，先创建面板数据集: {ST_PANEL_NAME}")
            panel = dw_create_panel(
                name=ST_PANEL_NAME,
                index_col=StandardFields.TRADE_DATE,
                entity_col_name="entity_id",
                value_dtype="int",  # 使用整数类型表示ST状态
                update_mode="update",  # 使用更新模式
            )
            logger.info(f"创建ST股票面板数据集: {ST_PANEL_NAME}")

            # 如果是新创建的面板，则需要使用create_st_panel初始化数据
            return create_st_panel(start_date=start_date, end_date=end_date)

        # 3. 计算ST股票状态
        logger.debug("开始计算更新期间内的ST股票状态")

        # 创建一个空的面板DataFrame，索引为交易日，列为股票代码
        panel_df = pd.DataFrame(
            index=trading_dates,
            columns=stock_codes,
            data=ST_STATUS_NORMAL,  # 默认为正常状态(0)
        )

        # 设置索引名称
        panel_df.index.name = StandardFields.TRADE_DATE

        # 遍历ST记录，将ST期间内的交易日标记为ST状态(1)
        for _, row in tqdm(st_df.iterrows(), desc="处理ST记录", total=len(st_df)):
            code = row["CODE"]
            start = row["START_DATE"]
            end = (
                row["END_DATE"]
                if row["END_DATE"] and row["END_DATE"] != "nan"
                else end_date
            )

            # 确保日期格式正确
            if pd.isna(start) or not start:
                continue

            # 获取此期间内的所有交易日
            period_dates = [date for date in trading_dates if start <= date <= end]

            # 标记这些日期为ST状态
            for date in period_dates:
                panel_df.loc[date, code] = ST_STATUS_ST

        # 4. 保存面板数据
        logger.debug("开始更新ST股票面板数据")

        # 重置索引以便将日期转为列
        panel_df = panel_df.reset_index()

        # 将数据从宽格式转为长格式
        panel_data = pd.melt(
            panel_df,
            id_vars=[StandardFields.TRADE_DATE],
            var_name="entity_id",
            value_name="value",
        )

        # 使用update模式保存面板数据，只更新指定日期范围内的数据
        dw_panel_save(
            data=panel_data,
            panel_name=ST_PANEL_NAME,
            mode="update",  # 使用更新模式，只更新或追加新数据
            update_key=StandardFields.TRADE_DATE,  # 使用交易日期作为更新键
        )

        logger.info(
            f"ST股票面板数据更新成功: 日期范围={start_date}至{end_date}, 股票数量={len(stock_codes)}"
        )
        return True

    except Exception as e:
        logger.error(f"更新ST股票面板数据失败: {str(e)}")
        return False


def get_st_status(date: str, codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    获取指定日期的股票ST状态

    Args:
        date: 日期，格式为YYYY-MM-DD
        codes: 股票代码列表，如果为None则获取所有股票

    Returns:
        pd.DataFrame: 包含股票ST状态的DataFrame，列为['code', 'is_st']
    """
    logger.info(f"获取日期{date}的ST股票状态")

    # 检查面板数据是否存在
    if not dw_panel_exists(ST_PANEL_NAME):
        logger.error(f"ST股票面板数据不存在")
        return pd.DataFrame()

    try:
        # 构建查询参数
        query_params = {
            "index_values": [date],
        }

        # 如果指定了股票代码，则只查询这些股票
        if codes:
            query_params["entity_ids"] = codes

        # 查询面板数据
        result = dw_panel_query(ST_PANEL_NAME, **query_params)

        if result.empty:
            logger.warning(f"日期{date}没有ST股票状态数据")
            return pd.DataFrame()

        # 整理结果为更友好的格式
        result = result.rename(
            columns={
                "entity_id": "code",
                "value": "is_st",
            }
        )

        return result[["code", "is_st"]]

    except Exception as e:
        logger.error(f"获取ST股票状态失败: {str(e)}")
        return pd.DataFrame()
