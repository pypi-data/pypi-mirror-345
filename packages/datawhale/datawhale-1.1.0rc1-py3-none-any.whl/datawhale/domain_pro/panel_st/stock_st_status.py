#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单只股票ST状态处理模块

提供获取单只股票的ST状态历史记录功能
"""

import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

from datawhale.domain_pro.info_st import query_st_info, ST_INFO_DATASET
from datawhale.domain_pro.info_trade_calendar import (
    get_trade_calendar_info,
    get_trading_days,
    TRADE_CALENDAR_DATASET,
)
from datawhale.domain_pro.field_standard import StandardFields
from datawhale.infrastructure_pro.storage import dw_query
from datawhale.infrastructure_pro.logging import get_user_logger

# 导入ST状态常量
from .st_panel import ST_STATUS_NORMAL, ST_STATUS_ST

logger = get_user_logger(__name__)


def get_stock_st_history(
    stock_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取单只股票的ST状态历史

    Args:
        stock_code: 股票代码，如'000001.SZ'
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        pd.DataFrame: 包含交易日和ST状态的DataFrame，列为['trade_date', 'stock_code', 'is_st']
    """
    logger.info(
        f"获取股票{stock_code}的ST状态历史: start_date={start_date}, end_date={end_date}"
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
            logger.error("交易日历数据为空，无法计算ST股票状态")
            return pd.DataFrame()

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
            return pd.DataFrame()

        # 获取交易日列表
        trading_dates = calendar_df[StandardFields.CALENDAR_DATE].tolist()
        logger.info(f"日期范围内总交易日数量: {len(trading_dates)}")

        # 2. 查询指定股票的ST信息
        logger.debug(f"查询股票{stock_code}的ST信息")
        st_df = query_st_info(ts_code=stock_code)

        if st_df.empty:
            logger.warning(f"股票{stock_code}没有ST记录，将返回全部为非ST状态的历史")
            # 创建一个全部为非ST状态的DataFrame
            result_df = pd.DataFrame(
                {
                    "trade_date": trading_dates,
                    "stock_code": stock_code,
                    "is_st": ST_STATUS_NORMAL,
                }
            )
            return result_df

        # 确保日期格式正确
        for date_field in [StandardFields.START_DATE, StandardFields.END_DATE]:
            if date_field in st_df.columns:
                # 标准化日期格式为YYYY-MM-DD
                st_df[date_field] = pd.to_datetime(st_df[date_field]).dt.strftime(
                    "%Y-%m-%d"
                )
                # 处理可能的NaT
                st_df[date_field] = st_df[date_field].fillna("")

        # 3. 创建股票的ST状态历史DataFrame
        # 初始化所有日期为非ST状态
        result_df = pd.DataFrame(
            {
                "trade_date": trading_dates,
                "stock_code": stock_code,
                "is_st": ST_STATUS_NORMAL,
            }
        )

        # 遍历ST记录，将ST期间内的交易日标记为ST状态
        for _, row in st_df.iterrows():
            start = row[StandardFields.START_DATE]
            end = (
                row[StandardFields.END_DATE]
                if row[StandardFields.END_DATE]
                and row[StandardFields.END_DATE] != "nan"
                else end_date
            )

            # 确保日期格式正确
            if pd.isna(start) or not start:
                continue

            # 标记这些日期为ST状态
            result_df.loc[
                (result_df["trade_date"] >= start) & (result_df["trade_date"] <= end),
                "is_st",
            ] = ST_STATUS_ST

        logger.info(f"成功生成股票{stock_code}的ST状态历史: 共{len(result_df)}条记录")
        return result_df

    except Exception as e:
        logger.error(f"获取股票ST状态历史失败: {str(e)}")
        return pd.DataFrame()


def get_stocks_st_history(
    stock_codes: list, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取多只股票的ST状态历史

    Args:
        stock_codes: 股票代码列表，如['000001.SZ', '600000.SH']
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        pd.DataFrame: 包含交易日和ST状态的DataFrame，列为['trade_date', 'stock_code', 'is_st']
    """
    logger.info(
        f"获取多只股票的ST状态历史: 股票数量={len(stock_codes)}, start_date={start_date}, end_date={end_date}"
    )

    try:
        # 初始化结果DataFrame
        result_df = pd.DataFrame()

        # 遍历每只股票，获取其ST状态历史
        for stock_code in stock_codes:
            stock_df = get_stock_st_history(stock_code, start_date, end_date)
            # 将单只股票的结果追加到总结果中
            result_df = pd.concat([result_df, stock_df], ignore_index=True)

        logger.info(
            f"成功生成{len(stock_codes)}只股票的ST状态历史: 共{len(result_df)}条记录"
        )
        return result_df

    except Exception as e:
        logger.error(f"获取多只股票ST状态历史失败: {str(e)}")
        return pd.DataFrame()
