#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
证券上市退市信息模块

提供获取和更新证券上市退市信息的功能
"""

import pandas as pd
import baostock as bs
from typing import Optional
import datetime
from pandas.tseries.offsets import DateOffset

from datawhale.domain_pro.field_standard import StandardFields, get_fields_type
from datawhale.domain_pro import standardize_dataframe
from datawhale.domain_pro.code_standard import (
    standardize_code,
    to_baostock_code,
    standardize_param_stock_code,
)
from datawhale.domain_pro.datetime_standard import to_standard_date
from datawhale.infrastructure_pro.storage import dw_create_dataset, dw_save, dw_exists

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)

# BaoStock数据源名称
BAOSTOCK_SOURCE = "baostock"

# 股票上市退市信息数据集名称
LISTING_DELISTING_DATASET = "listing_delisting_info"

# 需要保留的标准字段列表
REQUIRED_COLUMNS = [
    StandardFields.CODE,  # 证券代码
    StandardFields.NAME,  # 证券名称
    StandardFields.LISTING_DATE,  # 上市日期
    StandardFields.DELISTING_DATE,  # 退市日期
    StandardFields.SECURITY_TYPE,  # 证券类型
    StandardFields.LISTING_STATUS,  # 上市状态
    StandardFields.NEW_STOCK_CUTOFF_DATE,  # 次新股截止日期
]

# 日期字段列表
DATE_COLUMNS = [StandardFields.LISTING_DATE, StandardFields.DELISTING_DATE]

# 需要进行值映射的字段
VALUE_MAPPING_FIELDS = [StandardFields.LISTING_STATUS, StandardFields.SECURITY_TYPE]


@standardize_param_stock_code(param_name="code")
def fetch_listing_delisting_info(code: Optional[str] = None) -> pd.DataFrame:
    """
    获取单个证券的上市退市信息

    Args:
        code: 证券代码，支持标准化格式，如果为None则获取全市场证券信息

    Returns:
        pd.DataFrame: 包含证券上市退市信息的DataFrame
    """
    logger.info(f"开始获取证券上市退市信息: code={code}")

    # 登录BaoStock
    lg = bs.login()
    if lg.error_code != "0":
        logger.error(f"登录BaoStock失败: {lg.error_code} - {lg.error_msg}")
        raise ConnectionError(f"登录BaoStock失败: {lg.error_code} - {lg.error_msg}")

    try:
        # 转换为BaoStock格式的代码
        baostock_code = to_baostock_code(code) if code else None

        # 查询证券上市退市资料
        if baostock_code:
            logger.debug(f"查询单个证券上市退市资料: {baostock_code}")
            rs = bs.query_stock_basic(code=baostock_code)
        else:
            logger.debug("查询全市场证券上市退市资料")
            rs = bs.query_stock_basic()

        if rs.error_code != "0":
            logger.error(f"查询证券上市退市资料失败: {rs.error_code} - {rs.error_msg}")
            raise Exception(
                f"查询证券上市退市资料失败: {rs.error_code} - {rs.error_msg}"
            )

        # 将查询结果转换为DataFrame
        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            logger.warning(f"未查询到证券上市退市资料: code={code}")
            return pd.DataFrame()

        # 创建DataFrame
        result = pd.DataFrame(data_list, columns=rs.fields)

        # 使用合并后的标准化方法处理数据
        result = standardize_dataframe(
            df=result,
            source=BAOSTOCK_SOURCE,
            code_field="code",  # BaoStock原始代码字段名
            date_fields=DATE_COLUMNS,
            required_columns=REQUIRED_COLUMNS,
            value_mapping_fields=VALUE_MAPPING_FIELDS,
        )

        # 添加次新股截止日期字段（上市日期加一年）
        if StandardFields.LISTING_DATE in result.columns and not result.empty:
            # 将上市日期转换为datetime类型
            result[StandardFields.NEW_STOCK_CUTOFF_DATE] = pd.to_datetime(
                result[StandardFields.LISTING_DATE]
            )
            # 加一年
            result[StandardFields.NEW_STOCK_CUTOFF_DATE] = result[
                StandardFields.NEW_STOCK_CUTOFF_DATE
            ] + DateOffset(years=1)
            # 转回字符串格式 YYYY-MM-DD
            result[StandardFields.NEW_STOCK_CUTOFF_DATE] = result[
                StandardFields.NEW_STOCK_CUTOFF_DATE
            ].dt.strftime("%Y-%m-%d")
            logger.info(
                f"已添加次新股截止日期字段: {StandardFields.NEW_STOCK_CUTOFF_DATE}"
            )

        logger.info(f"获取证券上市退市信息完成: 共{len(result)}条记录")
        return result

    finally:
        # 登出BaoStock
        bs.logout()


def fetch_all_listing_delisting_info() -> pd.DataFrame:
    """
    获取全市场证券上市退市信息

    Returns:
        pd.DataFrame: 包含全市场证券上市退市信息的DataFrame
    """
    return fetch_listing_delisting_info(code=None)


def save_listing_delisting_info(data: pd.DataFrame) -> bool:
    """
    保存证券上市退市信息到数据集，按证券类型分开保存

    Args:
        data: 证券上市退市信息DataFrame

    Returns:
        bool: 保存是否成功
    """
    logger.info(f"开始保存证券上市退市信息: 共{len(data)}条记录")

    # 检查数据集是否存在，不存在则创建
    if not dw_exists(LISTING_DELISTING_DATASET):
        # 获取字段类型信息
        dtypes = get_fields_type(list(data.columns))

        # 创建数据集，使用security_type作为结构字段
        dw_create_dataset(
            name=LISTING_DELISTING_DATASET,
            dtypes=dtypes,
            update_mode="overwrite",  # 每次更新全量覆盖
            structure_fields=[StandardFields.SECURITY_TYPE],  # 按证券类型分组保存
        )
        logger.info(
            f"创建证券上市退市信息数据集: {LISTING_DELISTING_DATASET}, 按证券类型分组"
        )

    try:
        # 确保security_type列存在
        if StandardFields.SECURITY_TYPE not in data.columns:
            logger.error(
                f"数据中缺少证券类型字段({StandardFields.SECURITY_TYPE})，无法按类型保存"
            )
            return False

        # 按证券类型分组
        security_types = data[StandardFields.SECURITY_TYPE].unique()
        logger.info(f"数据包含 {len(security_types)} 种证券类型: {security_types}")

        # 分组保存
        success = True
        for sec_type in security_types:
            # 过滤出当前证券类型的数据
            type_data = data[data[StandardFields.SECURITY_TYPE] == sec_type]

            if not type_data.empty:
                # 保存当前证券类型的数据
                try:
                    dw_save(
                        data=type_data,
                        data_name=LISTING_DELISTING_DATASET,
                        mode="overwrite",
                        field_values={
                            StandardFields.SECURITY_TYPE: sec_type
                        },  # 使用field_values指定结构字段的值
                    )
                    logger.info(
                        f"保存证券类型 {sec_type} 的上市退市信息成功: {len(type_data)}条记录"
                    )
                except Exception as e:
                    logger.error(
                        f"保存证券类型 {sec_type} 的上市退市信息失败: {str(e)}"
                    )
                    success = False

        return success
    except Exception as e:
        logger.error(f"保存证券上市退市信息失败: {str(e)}")
        return False


def update_listing_delisting_info() -> bool:
    """
    更新全市场证券上市退市信息

    获取最新的全市场证券上市退市信息并更新到存储系统

    Returns:
        bool: 更新是否成功
    """
    try:
        # 获取全市场证券上市退市信息
        df = fetch_all_listing_delisting_info()

        # 保存到存储系统
        if not df.empty:
            return save_listing_delisting_info(df)
        else:
            logger.warning("未获取到证券上市退市信息，无数据更新")
            return False

    except Exception as e:
        logger.error(f"更新证券上市退市信息失败: {str(e)}")
        return False
