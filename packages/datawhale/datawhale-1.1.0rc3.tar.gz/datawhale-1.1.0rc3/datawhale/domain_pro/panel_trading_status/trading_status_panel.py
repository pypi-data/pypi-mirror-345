#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票交易状态面板数据处理模块

计算和存储交易状态面板数据的功能实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from tqdm import tqdm  # 导入tqdm进度条库

# 导入相关模块
from datawhale.domain_pro.info_listing_and_delisting import (
    fetch_all_listing_delisting_info,
    LISTING_DELISTING_DATASET,
)
from datawhale.domain_pro.info_trade_calendar import (
    get_trade_calendar_info,
    get_trading_days,
    TRADE_CALENDAR_DATASET,
)
from datawhale.domain_pro.info_suspend import (
    fetch_suspend_info,
    get_suspend_stocks,
    SUSPEND_INFO_DATASET,
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
TRADING_STATUS_PANEL_NAME = "panel_trading_status"

# 定义交易状态值
TRADING_STATUS_NOT_LISTED = "U"  # 未上市
TRADING_STATUS_TRADING = "T"  # 正常交易
TRADING_STATUS_SUSPENDED = "S"  # 停牌
TRADING_STATUS_DELISTED = "D"  # 退市

# 添加证券类型常量
SECURITY_TYPE_STOCK = "STOCK"  # 股票
SECURITY_TYPE_INDEX = "INDEX"  # 指数
SECURITY_TYPE_CONVERTIBLE_BOND = "CONVERTIBLE_BOND"  # 可转债


def compute_trading_status_by_month(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    按月计算指定日期区间内的股票交易状态

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        Dict[str, Dict[str, pd.DataFrame]]: 按证券类型和年月分组的交易状态面板数据
                                           外层键为证券类型，内层键为年月字符串(YYYY-MM)，值为对应的DataFrame
    """
    logger.info(
        f"开始按月计算交易状态面板数据: start_date={start_date}, end_date={end_date}"
    )

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
        logger.error("交易日历数据为空，无法计算交易状态")
        return {}

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
        return {}

    # 转换日期为datetime类型
    calendar_df[StandardFields.CALENDAR_DATE] = pd.to_datetime(
        calendar_df[StandardFields.CALENDAR_DATE]
    )

    # 添加年月字段，使用向量化操作
    calendar_df["year_month"] = calendar_df[StandardFields.CALENDAR_DATE].dt.strftime(
        "%Y-%m"
    )

    # 按年月分组，使用向量化操作获取每月的交易日
    month_trade_dates = {}
    for year_month, group in calendar_df.groupby("year_month"):
        # 一次性转换整个数组，而不是循环转换
        month_trade_dates[year_month] = (
            group[StandardFields.CALENDAR_DATE].dt.strftime("%Y-%m-%d").to_numpy()
        )

    logger.info(
        f"日期范围内总交易日数量: {len(calendar_df)}, 分为 {len(month_trade_dates)} 个月"
    )

    # 2. 加载上市退市信息
    logger.debug("加载上市退市信息数据")
    listing_df = dw_query(LISTING_DELISTING_DATASET)
    if listing_df.empty:
        logger.error("上市退市信息数据为空，无法计算交易状态")
        return {}

    # 清理上市退市信息中的NA值
    listing_df = listing_df.fillna(
        {StandardFields.LISTING_DATE: "", StandardFields.DELISTING_DATE: ""}
    )

    # 检查security_type列是否存在
    if StandardFields.SECURITY_TYPE not in listing_df.columns:
        logger.error(
            f"上市退市信息中缺少证券类型字段({StandardFields.SECURITY_TYPE})，无法按证券类型处理"
        )
        return {}

    # 获取所有证券类型
    security_types = listing_df[StandardFields.SECURITY_TYPE].unique()
    logger.info(f"上市退市信息中的证券类型: {security_types}")

    # 预先按证券类型分组，避免在循环中重复筛选
    type_listings = {
        sec_type: listing_df[listing_df[StandardFields.SECURITY_TYPE] == sec_type]
        for sec_type in security_types
    }

    # 创建证券类型到代码的映射
    security_type_codes = {}
    for sec_type, type_df in type_listings.items():
        # 获取该类型的所有代码
        type_codes = type_df[StandardFields.CODE].unique()
        security_type_codes[sec_type] = type_codes
        logger.info(f"{sec_type}类型的证券数量: {len(type_codes)}")

    # 3. 加载停牌信息
    logger.debug("加载停牌信息数据")
    suspend_df = dw_query(SUSPEND_INFO_DATASET)

    if not suspend_df.empty:
        # 检查并映射字段名
        if (
            "code" in suspend_df.columns
            and StandardFields.STOCK_CODE not in suspend_df.columns
        ):
            # 将'code'字段映射为标准字段名
            suspend_df[StandardFields.STOCK_CODE] = suspend_df["code"]

        # 筛选日期范围内的停牌记录，使用向量化操作
        suspend_df = suspend_df[
            (suspend_df[StandardFields.TRADE_DATE] >= start_date)
            & (suspend_df[StandardFields.TRADE_DATE] <= end_date)
        ]

        # 过滤掉suspend_type为R的记录，因为它们应该被标记为正常交易而非停牌
        if "suspend_type" in suspend_df.columns:
            suspend_df_filtered = suspend_df[
                (suspend_df["suspend_type"] != "R")
                & (
                    (suspend_df["suspend_timing"].isna())
                    | (suspend_df["suspend_timing"] == "")
                )
            ]
        else:
            suspend_df_filtered = suspend_df

        # 预计算停牌信息的日期和股票代码映射，加速后续处理
        suspend_date_code_pairs = set(
            zip(
                suspend_df_filtered[StandardFields.TRADE_DATE],
                suspend_df_filtered[StandardFields.STOCK_CODE],
            )
        )

    # 用于存储结果：先按证券类型分组，再按月份分组
    type_month_panels = {}

    # 4. 首先按证券类型循环，然后按月处理
    for security_type, codes in tqdm(
        security_type_codes.items(), desc="按证券类型处理"
    ):
        logger.info(f"开始处理 {security_type} 类型的证券")

        # 获取该类型的上市退市信息
        type_listing_df = type_listings[security_type]

        # 初始化该证券类型的月度面板字典
        type_month_panels[security_type] = {}

        # 按月处理
        for year_month, dates in tqdm(
            month_trade_dates.items(), desc=f"{security_type}按月计算"
        ):
            # 应用上市退市信息
            logger.debug(f"处理 {security_type} - {year_month} 的上市退市信息")

            # 将日期数组和代码数组预先转换为numpy数组
            date_array = np.array(dates)
            code_array = np.array(codes)

            # 创建状态矩阵，使用numpy高效初始化
            status_matrix = np.full(
                (len(date_array), len(code_array)), TRADING_STATUS_NOT_LISTED
            )

            # 获取有效的上市记录（上市日期不为空）
            valid_listings = type_listing_df[
                type_listing_df[StandardFields.LISTING_DATE] != ""
            ]

            # 如果有有效记录，则进行批处理
            if not valid_listings.empty:
                # 构建股票代码到列索引的映射
                code_to_idx = {code: i for i, code in enumerate(code_array)}

                # 一次性转换上市日期为datetime数组，避免在循环中重复转换
                listing_dates = pd.to_datetime(
                    valid_listings[StandardFields.LISTING_DATE]
                ).values
                # 一次性提取有效股票代码
                valid_codes = valid_listings[StandardFields.CODE].values
                # 创建代码到上市日期的映射
                code_to_listing_date = {
                    code: date for code, date in zip(valid_codes, listing_dates)
                }

                # 提取退市日期信息
                has_delisting = valid_listings[StandardFields.DELISTING_DATE] != ""
                delisted_stocks = valid_listings[has_delisting]
                if not delisted_stocks.empty:
                    delisting_dates = pd.to_datetime(
                        delisted_stocks[StandardFields.DELISTING_DATE]
                    ).values
                    delisted_codes = delisted_stocks[StandardFields.CODE].values
                    # 创建代码到退市日期的映射
                    code_to_delisting_date = {
                        code: date
                        for code, date in zip(delisted_codes, delisting_dates)
                    }

                # 使用完全向量化的方法处理上市和退市状态
                for i, date in enumerate(pd.to_datetime(date_array)):
                    # 更新正常交易状态
                    for j, code in enumerate(code_array):
                        if (
                            code in code_to_listing_date
                            and date >= code_to_listing_date[code]
                        ):
                            # 检查是否已退市
                            if (
                                code in code_to_delisting_date
                                and date > code_to_delisting_date[code]
                            ):
                                status_matrix[i, j] = TRADING_STATUS_DELISTED
                            else:
                                status_matrix[i, j] = TRADING_STATUS_TRADING

            # 应用停牌信息 (只对该类型的证券应用)
            if not suspend_df.empty and hasattr(locals(), "suspend_date_code_pairs"):
                logger.debug(f"处理 {security_type} - {year_month} 的停牌信息")

                # 直接使用预计算的停牌对，避免重复筛选
                for i, date in enumerate(date_array):
                    for j, code in enumerate(code_array):
                        # 只处理正常交易状态的股票
                        if (
                            status_matrix[i, j] == TRADING_STATUS_TRADING
                            and (date, code) in suspend_date_code_pairs
                        ):
                            status_matrix[i, j] = TRADING_STATUS_SUSPENDED

            # 将状态矩阵转换为DataFrame（这里是缺失的代码）
            month_panel = pd.DataFrame(
                status_matrix, index=date_array, columns=code_array
            )
            month_panel.index.name = StandardFields.TRADE_DATE

            # 保存当月结果
            type_month_panels[security_type][year_month] = month_panel
            logger.info(
                f"完成 {security_type} - {year_month} 月交易状态计算: shape={month_panel.shape}"
            )

    logger.info(
        f"所有证券类型和月份的交易状态面板数据计算完成: 总证券类型={len(type_month_panels)}"
    )
    return type_month_panels


def _add_yearmonth_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    添加年月格式的结构字段到数据框

    Args:
        df: 含有交易日期的数据框

    Returns:
        pd.DataFrame: 添加了年月列的数据框
    """
    # 确保日期格式正确
    if StandardFields.TRADE_DATE in df.columns:
        # 确保日期列是日期类型
        if not pd.api.types.is_datetime64_any_dtype(df[StandardFields.TRADE_DATE]):
            df[StandardFields.TRADE_DATE] = pd.to_datetime(
                df[StandardFields.TRADE_DATE]
            )

        # 添加年月字段，格式为YYYY-MM
        df["year_month"] = df[StandardFields.TRADE_DATE].dt.strftime("%Y-%m")

    return df


def create_trading_status_panel(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> bool:
    """
    创建并保存交易状态面板数据

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        bool: 创建是否成功
    """
    logger.info(
        f"开始创建交易状态面板数据: start_date={start_date}, end_date={end_date}"
    )

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
            logger.error("交易日历数据为空，无法计算交易状态")
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

        # 转换日期为datetime类型
        calendar_df[StandardFields.CALENDAR_DATE] = pd.to_datetime(
            calendar_df[StandardFields.CALENDAR_DATE]
        )

        # 添加年月字段，按年月分组
        calendar_df["year_month"] = calendar_df[
            StandardFields.CALENDAR_DATE
        ].dt.strftime("%Y-%m")

        # 按年月分组，获取每月的交易日
        month_trade_dates = {}
        for year_month, group in calendar_df.groupby("year_month"):
            month_trade_dates[year_month] = (
                group[StandardFields.CALENDAR_DATE].dt.strftime("%Y-%m-%d").tolist()
            )

        logger.info(
            f"日期范围内总交易日数量: {len(calendar_df)}, 分为 {len(month_trade_dates)} 个月"
        )

        # 2. 加载上市退市信息
        logger.debug("加载上市退市信息数据")
        listing_df = dw_query(LISTING_DELISTING_DATASET)
        if listing_df.empty:
            logger.error("上市退市信息数据为空，无法计算交易状态")
            return False

        # 清理上市退市信息中的NA值
        listing_df = listing_df.fillna(
            {StandardFields.LISTING_DATE: "", StandardFields.DELISTING_DATE: ""}
        )

        # 检查security_type列是否存在
        if StandardFields.SECURITY_TYPE not in listing_df.columns:
            logger.error(
                f"上市退市信息中缺少证券类型字段({StandardFields.SECURITY_TYPE})，无法按证券类型保存"
            )
            return False

        # 获取所有证券类型
        security_types = listing_df[StandardFields.SECURITY_TYPE].unique().tolist()
        logger.info(f"上市退市信息中的证券类型: {security_types}")

        # 创建证券类型到代码的映射
        security_type_codes = {}
        for sec_type in security_types:
            # 获取该类型的所有代码
            type_codes = (
                listing_df[listing_df[StandardFields.SECURITY_TYPE] == sec_type][
                    StandardFields.CODE
                ]
                .unique()
                .tolist()
            )
            security_type_codes[sec_type] = type_codes
            logger.info(f"{sec_type}类型的证券数量: {len(type_codes)}")

        # 3. 加载停牌信息
        logger.debug("加载停牌信息数据")
        suspend_df = dw_query(SUSPEND_INFO_DATASET)

        if not suspend_df.empty:
            # 检查并映射字段名
            if (
                "code" in suspend_df.columns
                and StandardFields.STOCK_CODE not in suspend_df.columns
            ):
                # 将'code'字段映射为标准字段名
                suspend_df[StandardFields.STOCK_CODE] = suspend_df["code"]

            # 筛选日期范围内的停牌记录
            suspend_df = suspend_df[
                (suspend_df[StandardFields.TRADE_DATE] >= start_date)
                & (suspend_df[StandardFields.TRADE_DATE] <= end_date)
            ]

        # 如果面板数据不存在，则创建
        if not dw_panel_exists(TRADING_STATUS_PANEL_NAME):
            panel = dw_create_panel(
                name=TRADING_STATUS_PANEL_NAME,
                index_col=StandardFields.TRADE_DATE,
                entity_col_name="entity_id",
                value_dtype="str",  # 修改为字符串类型
                update_mode="update",  # 使用更新模式
                structure_fields=[
                    StandardFields.SECURITY_TYPE,
                    "year_month",
                ],  # 使用证券类型和年月作为结构字段
            )
            logger.info(f"创建交易状态面板数据集: {TRADING_STATUS_PANEL_NAME}")

        # 总记录数计数
        total_records = 0

        # 4. 首先按证券类型循环，然后按年月处理
        for security_type, codes in tqdm(
            security_type_codes.items(), desc="按证券类型处理"
        ):
            logger.info(f"开始处理 {security_type} 类型的证券")

            # 获取该类型的上市退市信息
            type_listing_df = listing_df[
                listing_df[StandardFields.SECURITY_TYPE] == security_type
            ]

            # 按月处理和保存数据
            for year_month, dates in tqdm(
                month_trade_dates.items(), desc=f"{security_type}按月计算和保存"
            ):
                # 应用上市退市信息
                logger.debug(f"处理 {security_type} - {year_month} 的上市退市信息")

                # 将日期转换为numpy数组，以便于向量操作
                date_array = np.array(dates)

                # 创建一个日期矩阵(dates × codes)，所有元素初始化为未上市状态
                status_matrix = np.full(
                    (len(dates), len(codes)), TRADING_STATUS_NOT_LISTED
                )

                # 获取有效的上市记录（上市日期不为空）
                valid_listings = type_listing_df[
                    type_listing_df[StandardFields.LISTING_DATE] != ""
                ]

                # 如果有有效记录，则进行批处理
                if not valid_listings.empty:
                    # 构建股票代码到列索引的映射
                    code_to_idx = {code: i for i, code in enumerate(codes)}

                    # 向量化处理：创建日期和上市日期的关系矩阵
                    dates_df = pd.DataFrame(dates, columns=["date"])
                    # 将日期转换为numpy数组形式，便于比较
                    date_values = pd.to_datetime(dates_df["date"]).values

                    # 获取每个股票的上市和退市日期
                    valid_listings_dates = pd.to_datetime(
                        valid_listings[StandardFields.LISTING_DATE]
                    ).values

                    # 过滤出有效股票代码
                    valid_codes = [
                        code
                        for code in valid_listings[StandardFields.CODE].tolist()
                        if code in code_to_idx
                    ]
                    code_indices = np.array([code_to_idx[code] for code in valid_codes])

                    # 向量化：为每个日期和每个股票创建交易状态
                    for i, date in enumerate(date_values):
                        # 创建上市和未退市的掩码
                        is_listed = date >= valid_listings_dates

                        # 获取上市股票的代码索引
                        listed_indices = code_indices[is_listed[: len(code_indices)]]

                        # 应用正常交易状态
                        if len(listed_indices) > 0:
                            status_matrix[i, listed_indices] = TRADING_STATUS_TRADING

                    # 处理退市状态 - 向量化实现
                    has_delisting = valid_listings[StandardFields.DELISTING_DATE] != ""
                    if has_delisting.any():
                        delisted_stocks = valid_listings[has_delisting]
                        delisted_dates = pd.to_datetime(
                            delisted_stocks[StandardFields.DELISTING_DATE]
                        ).values
                        delisted_codes = [
                            code
                            for code in delisted_stocks[StandardFields.CODE].tolist()
                            if code in code_to_idx
                        ]
                        delisted_indices = np.array(
                            [code_to_idx[code] for code in delisted_codes]
                        )

                        for i, date in enumerate(date_values):
                            # 创建已退市的掩码
                            is_delisted = date > delisted_dates

                            # 获取已退市股票的代码索引
                            if len(is_delisted) > 0:
                                delisted_code_indices = delisted_indices[
                                    is_delisted[: len(delisted_indices)]
                                ]

                                # 应用退市状态
                                if len(delisted_code_indices) > 0:
                                    status_matrix[i, delisted_code_indices] = (
                                        TRADING_STATUS_DELISTED
                                    )

                # 应用停牌信息 (只对该类型的证券应用)
                if not suspend_df.empty:
                    logger.debug(f"处理 {security_type} - {year_month} 的停牌信息")
                    # 筛选当月停牌记录和当前证券类型
                    month_suspend_df = suspend_df[
                        suspend_df[StandardFields.TRADE_DATE].isin(dates)
                        & suspend_df[StandardFields.STOCK_CODE].isin(codes)
                    ]

                    # 过滤掉suspend_type为R的记录，因为它们应该被标记为正常交易而非停牌
                    if (
                        not month_suspend_df.empty
                        and "suspend_type" in month_suspend_df.columns
                    ):
                        month_suspend_df = month_suspend_df[
                            (month_suspend_df["suspend_type"] != "R")
                            & (
                                (month_suspend_df["suspend_timing"].isna())
                                | (month_suspend_df["suspend_timing"] == "")
                            )
                        ]

                    # 如果有停牌记录，使用NumPy完全向量化应用停牌状态
                    if not month_suspend_df.empty:
                        # 将日期和代码转换为NumPy数组，以便于向量化处理
                        date_array = np.array(dates)
                        code_array = np.array(codes)

                        # 创建映射字典，用于快速查找索引
                        date_to_idx = {date: idx for idx, date in enumerate(date_array)}
                        code_to_idx = {code: idx for idx, code in enumerate(code_array)}

                        # 获取停牌记录的日期和代码索引
                        suspend_date_indices = np.array(
                            [
                                date_to_idx.get(date, -1)
                                for date in month_suspend_df[StandardFields.TRADE_DATE]
                            ]
                        )
                        suspend_code_indices = np.array(
                            [
                                code_to_idx.get(code, -1)
                                for code in month_suspend_df[StandardFields.STOCK_CODE]
                            ]
                        )

                        # 过滤有效索引
                        valid_indices = (suspend_date_indices >= 0) & (
                            suspend_code_indices >= 0
                        )
                        valid_date_indices = suspend_date_indices[valid_indices]
                        valid_code_indices = suspend_code_indices[valid_indices]

                        # 仅更新状态为TRADING_STATUS_TRADING的股票状态
                        for date_idx, code_idx in zip(
                            valid_date_indices, valid_code_indices
                        ):
                            if (
                                status_matrix[date_idx, code_idx]
                                == TRADING_STATUS_TRADING
                            ):
                                status_matrix[date_idx, code_idx] = (
                                    TRADING_STATUS_SUSPENDED
                                )

                # 将状态矩阵转换为DataFrame（这里是缺失的代码）
                month_panel = pd.DataFrame(status_matrix, index=dates, columns=codes)
                month_panel.index.name = StandardFields.TRADE_DATE

                # 将当月数据转换为长格式并立即保存，然后释放内存
                logger.debug(
                    f"将 {security_type} - {year_month} 月的数据转换为长格式并保存"
                )

                # 转换为长格式
                long_format_df = month_panel.reset_index()  # 重置索引，使日期成为普通列
                long_format_df = _add_yearmonth_column(long_format_df)

                # 添加证券类型字段
                long_format_df[StandardFields.SECURITY_TYPE] = security_type

                # 保存当月数据
                dw_panel_save(
                    data=long_format_df,
                    panel_name=TRADING_STATUS_PANEL_NAME,
                    field_values={
                        StandardFields.SECURITY_TYPE: security_type,
                        "year_month": year_month,
                    },  # 使用证券类型和年月组合作为结构字段值
                    mode="overwrite",  # 首次创建使用覆盖模式
                )

                # 记录当月数据量
                month_records = len(long_format_df)
                total_records += month_records
                logger.info(
                    f"交易状态面板数据 {security_type} - {year_month} 计算和保存成功: 记录数={month_records}"
                )

                # 主动释放内存
                del month_panel, long_format_df
                if not suspend_df.empty and "month_suspend_df" in locals():
                    del month_suspend_df

        logger.info(f"交易状态面板数据保存成功: 总记录数={total_records}")
        return True

    except Exception as e:
        logger.error(f"创建交易状态面板数据失败: {str(e)}")
        return False


def update_trading_status_panel(days: int = 30) -> bool:
    """
    更新交易状态面板数据

    仅更新指定天数内的数据，提高效率

    Args:
        days: 要更新的最近天数，默认为30天

    Returns:
        bool: 更新是否成功
    """
    logger.info(f"开始更新交易状态面板数据: days={days}")

    try:
        # 计算开始日期（当前日期往前推days天）
        current_date = datetime.now()
        end_date = current_date.strftime("%Y-%m-%d")
        start_date = (current_date - timedelta(days=days)).strftime("%Y-%m-%d")

        # 调用创建函数进行更新，逻辑保持一致，避免代码重复
        # 如果面板不存在则会自动创建
        success = create_trading_status_panel(start_date, end_date)

        if success:
            logger.info(f"交易状态面板数据更新成功: 时间范围={start_date}至{end_date}")
        else:
            logger.error("交易状态面板数据更新失败")

        return success

    except Exception as e:
        logger.error(f"更新交易状态面板数据失败: {str(e)}")
        return False


def get_trading_status(date, codes=None, security_type=None):
    """
    获取指定日期和证券类型的交易状态

    Args:
        date: 交易日期，格式为YYYY-MM-DD
        codes: 股票代码列表，如果为None则返回所有股票
        security_type: 证券类型，如STOCK、INDEX等，如果为None则查询失败

    Returns:
        pd.DataFrame: 包含指定日期股票交易状态的DataFrame
    """
    from datawhale.standard import to_standard_date, standardize_batch_codes

    # 参数标准化
    date = to_standard_date(date)
    if codes is not None:
        if not isinstance(codes, list):
            codes = [codes]
        codes = standardize_batch_codes(codes)

    logger.info(
        f"获取日期 {date} 的交易状态数据: security_type={security_type}, codes={codes}"
    )

    try:
        # 检查必要参数
        if security_type is None:
            logger.error("未指定证券类型，查询失败")
            return pd.DataFrame()

        # 验证日期格式
        date_obj = pd.to_datetime(date)

        # 计算年月值，用于结构化查询
        year_month = date_obj.strftime("%Y-%m")

        # 检查面板是否存在
        if not dw_panel_exists(TRADING_STATUS_PANEL_NAME):
            logger.error(f"交易状态面板 {TRADING_STATUS_PANEL_NAME} 不存在")
            return pd.DataFrame()

        # 准备查询参数
        query_params = {
            "panel_name": TRADING_STATUS_PANEL_NAME,
            "field_values": {
                StandardFields.SECURITY_TYPE: security_type,
                "year_month": year_month,
            },
            "sort_by": StandardFields.TRADE_DATE,  # 按日期排序
        }

        # 如果指定了股票代码，添加到columns参数中
        if codes is not None and len(codes) > 0:
            # 由于面板格式为日期索引+股票代码列，只需要将日期列和需要的股票代码列包含在查询中
            query_params["columns"] = [StandardFields.TRADE_DATE] + codes

        # 执行查询
        result_df = dw_panel_query(**query_params)

        # 如果没有找到任何数据，返回空DataFrame
        if result_df is None or result_df.empty:
            logger.warning(f"未找到日期 {date} 证券类型 {security_type} 的交易状态数据")
            return pd.DataFrame()

        # 筛选指定日期的数据
        result_df = result_df[result_df[StandardFields.TRADE_DATE] == date]

        # 如果筛选后没有数据，返回空DataFrame
        if result_df.empty:
            logger.warning(
                f"日期 {date} 证券类型 {security_type} 没有匹配的交易状态数据"
            )
            return pd.DataFrame()

        # 丢弃不需要的列(证券类型和年月)
        result_df = result_df.drop(
            columns=[StandardFields.SECURITY_TYPE, "year_month"], errors="ignore"
        )

        # 直接返回原始查询结果，不做任何格式转换
        logger.info(
            f"成功获取日期 {date} 证券类型 {security_type} 的交易状态数据: 列数={len(result_df.columns)}"
        )
        return result_df

    except Exception as e:
        logger.error(f"获取交易状态数据失败: {str(e)}")
        return pd.DataFrame()
