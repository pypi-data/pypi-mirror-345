#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
次新股面板数据处理模块

计算和存储次新股面板数据的功能实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from tqdm import tqdm  # 导入tqdm进度条库
import os

# 导入相关模块
from datawhale.domain_pro.info_listing_and_delisting import (
    LISTING_DELISTING_DATASET,
)
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
NEW_STOCK_PANEL_NAME = "panel_new_stock"

# 定义次新股状态值
NEW_STOCK_STATUS_NORMAL = 0  # 正常，非次新股状态
NEW_STOCK_STATUS_NEW = 1  # 次新股状态


def create_new_stock_panel(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> bool:
    """
    创建并保存次新股面板数据

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        bool: 创建是否成功
    """
    logger.info(f"开始创建次新股面板数据: start_date={start_date}, end_date={end_date}")

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
            logger.error("交易日历数据为空，无法计算次新股状态")
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

        # 2. 加载上市退市信息
        logger.debug("加载上市退市信息数据")
        # 查询上市退市信息，只获取股票类型的数据
        listing_df = dw_query(
            LISTING_DELISTING_DATASET, field_values={"security_type": "STOCK"}
        )
        if listing_df.empty:
            logger.error("上市退市信息数据为空，无法计算次新股状态")
            return False

        # 确保所有字段名符合标准
        if StandardFields.NEW_STOCK_CUTOFF_DATE not in listing_df.columns:
            logger.error(
                f"上市退市信息数据中缺少次新股截止日期字段: {StandardFields.NEW_STOCK_CUTOFF_DATE}"
            )
            return False

        # 过滤出有效的上市信息（有上市日期和次新股截止日期的记录）
        listing_df = listing_df[
            (listing_df[StandardFields.LISTING_DATE].notna())
            & (listing_df[StandardFields.NEW_STOCK_CUTOFF_DATE].notna())
        ]

        if listing_df.empty:
            logger.error("过滤后的上市退市信息数据为空，无法计算次新股状态")
            return False

        # 获取所有股票代码
        stock_codes = listing_df[StandardFields.CODE].unique().tolist()
        logger.info(f"股票代码数量: {len(stock_codes)}")

        # 如果面板数据不存在，则创建
        if not dw_panel_exists(NEW_STOCK_PANEL_NAME):
            panel = dw_create_panel(
                name=NEW_STOCK_PANEL_NAME,
                index_col=StandardFields.TRADE_DATE,
                value_dtype="float",  # 使用float类型兼容性更好
                entity_col_name="entity_id",
                structure_fields=["year"],
                update_mode="overwrite",
            )
            logger.info(f"创建次新股面板数据集: {NEW_STOCK_PANEL_NAME}")

        # 3. 按年分组处理交易日
        years = list(set([date[:4] for date in trading_dates]))
        years.sort()
        logger.info(f"需要处理的年份: {years}")

        # 创建空的结果DataFrames字典，每年一个DataFrame
        result_dfs = {}

        # 遍历每年
        for year in tqdm(years, desc="按年处理交易日"):
            year_dates = [date for date in trading_dates if date.startswith(year)]
            logger.debug(f"处理{year}年, 交易日数量: {len(year_dates)}")

            # 预先创建一个存储所有次新股状态的列表
            new_stock_data = []

            # 处理当年的每个交易日
            for date in tqdm(year_dates, desc=f"处理{year}年交易日", leave=False):
                # 筛选出在当前交易日是次新股的股票
                new_stocks = listing_df[
                    (listing_df[StandardFields.LISTING_DATE] <= date)
                    & (listing_df[StandardFields.NEW_STOCK_CUTOFF_DATE] >= date)
                ]

                if not new_stocks.empty:
                    # 对于每个次新股，记录日期和股票代码
                    for _, row in new_stocks.iterrows():
                        new_stock_data.append(
                            {
                                "trade_date": date,
                                "stock_code": row[StandardFields.CODE],
                                "value": NEW_STOCK_STATUS_NEW,
                            }
                        )

            # 创建DataFrame
            if new_stock_data:
                year_df = pd.DataFrame(new_stock_data)
                # 转换为宽格式
                year_df = year_df.pivot(
                    index="trade_date", columns="stock_code", values="value"
                )
                year_df = year_df.fillna(NEW_STOCK_STATUS_NORMAL)  # 默认为非次新股状态
                year_df.index.name = StandardFields.TRADE_DATE

                # 保存当年的结果
                result_dfs[year] = year_df
                logger.info(
                    f"{year}年次新股数据处理完成，共有{len(year_df.columns)}只次新股"
                )
            else:
                # 如果没有次新股，创建一个空的DataFrame
                year_df = pd.DataFrame(index=year_dates)
                year_df.index.name = StandardFields.TRADE_DATE
                result_dfs[year] = year_df
                logger.info(f"{year}年没有次新股数据")

        # 4. 准备保存面板数据
        logger.debug("开始保存次新股面板数据")

        # 按年份分别保存数据
        for year, year_df in result_dfs.items():
            # 不需要将宽格式转为长格式，直接保存宽格式数据
            if not year_df.empty and len(year_df.columns) > 0:
                # 确保trade_date在列中而非索引
                df = year_df.reset_index()

                # 直接保存宽格式数据
                logger.info(
                    f"保存{year}年次新股面板数据，共{len(df)}行，{len(df.columns)}列"
                )
                dw_panel_save(
                    data=df,
                    panel_name=NEW_STOCK_PANEL_NAME,
                    field_values={"year": year},
                    mode="overwrite",  # 使用覆盖模式
                )

        logger.info(f"次新股面板数据创建并保存成功: 日期范围={start_date}至{end_date}")
        return True

    except Exception as e:
        logger.error(f"创建次新股面板数据失败: {str(e)}")
        return False


def update_new_stock_panel(days: int = 30) -> bool:
    """
    更新次新股面板数据

    Args:
        days: 需要更新的最近天数，默认为30天

    Returns:
        bool: 更新是否成功
    """
    logger.info(f"开始更新次新股面板数据: 最近{days}天")

    try:
        # 计算开始日期和结束日期
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 直接调用创建函数，指定日期范围
        return create_new_stock_panel(start_date=start_date, end_date=end_date)

    except Exception as e:
        logger.error(f"更新次新股面板数据失败: {str(e)}")
        return False


def get_new_stock_status(date: str, codes: Optional[List[str]] = None) -> pd.DataFrame:
    """
    获取指定日期的次新股状态

    Args:
        date: 日期，格式为YYYY-MM-DD
        codes: 股票代码列表，如果为None则获取所有股票

    Returns:
        pd.DataFrame: 包含股票代码和次新股状态的DataFrame
    """
    logger.info(f"获取次新股状态: date={date}, codes={codes}")

    try:
        # 检查面板数据是否存在
        if not dw_panel_exists(NEW_STOCK_PANEL_NAME):
            logger.error(f"次新股面板数据不存在: {NEW_STOCK_PANEL_NAME}")
            return pd.DataFrame()

        # 从日期中获取年份
        year = date.split("-")[0]

        # 构建年份对应的CSV文件路径
        csv_path = f"/Users/hanswang/Desktop/long_road/DataWhale/cache/panel/{NEW_STOCK_PANEL_NAME}/{year}.csv"

        # 检查年份文件是否存在
        if not os.path.exists(csv_path):
            logger.warning(f"年份文件不存在: {csv_path}")
            return pd.DataFrame()

        try:
            # 读取面板数据（宽格式，行为日期，列为股票代码）
            panel_data = pd.read_csv(csv_path, index_col=0)

            if panel_data.empty:
                logger.warning(f"面板数据为空: {csv_path}")
                return pd.DataFrame()

            # 检查日期是否在面板数据中
            if date not in panel_data.index:
                logger.warning(f"日期不在面板数据中: {date}")
                return pd.DataFrame()

            # 获取指定日期的次新股状态
            status_data = panel_data.loc[date]

            # 如果指定了股票代码，则进行过滤
            if codes is not None:
                # 找出在状态数据中存在的股票代码
                valid_codes = [code for code in codes if code in status_data.index]
                if not valid_codes:
                    logger.warning(f"指定的股票代码不在面板数据中: {codes}")
                    return pd.DataFrame()

                # 获取指定股票的状态
                status_data = status_data[valid_codes]

            # 转换为DataFrame
            result = pd.DataFrame(status_data).reset_index()
            result.columns = ["entity_id", "is_new_stock"]

            # 过滤掉状态为0或NaN的记录
            result = result[result["is_new_stock"] == 1]

            return result

        except Exception as e:
            logger.error(f"读取面板数据失败: {e}")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"获取次新股状态失败: {e}")
        return pd.DataFrame()
