#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票交易状态标记模块

根据上市退市信息、停牌信息和交易日历，标记单只股票的交易状态（未上市、上市、停牌、退市）

注：
- 当股票suspend_type为S且停牌时间为空时，标记为停牌(SUSPENDED)
- 当股票suspend_type为S但停牌时间不为空时，标记为正常交易(TRADING)
- 当股票suspend_type为R时，标记为正常交易(TRADING)而非停牌
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta

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
from datawhale.local import (
    dw_query,
    dw_exists,
    dw_panel_save,
    dw_panel_query,
    dw_panel_exists,
)

# 从交易状态面板模块导入常量
from datawhale.domain_pro.panel_trading_status import (
    TRADING_STATUS_NOT_LISTED,
    TRADING_STATUS_TRADING,
    TRADING_STATUS_SUSPENDED,
    TRADING_STATUS_DELISTED,
    SECURITY_TYPE_STOCK,
    SECURITY_TYPE_INDEX,
    SECURITY_TYPE_CONVERTIBLE_BOND,
)

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)


def standardize_columns(
    df: pd.DataFrame, mapping: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    标准化DataFrame的列名

    Args:
        df: 需要标准化列名的DataFrame
        mapping: 列名映射字典，键为原列名，值为标准列名。如果为None，则使用默认映射。

    Returns:
        pd.DataFrame: 列名标准化后的DataFrame
    """
    if df.empty:
        return df

    if mapping is None:
        mapping = {
            "code": StandardFields.STOCK_CODE,
            # 可以添加其他字段映射...
        }

    for old_col, new_col in mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]

    return df


def get_stock_trading_status(
    stock_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取指定股票在日期范围内的交易状态

    Args:
        stock_code: 股票代码
        start_date: 开始日期，格式为YYYY-MM-DD，如果为None则使用最早的交易日期
        end_date: 结束日期，格式为YYYY-MM-DD，如果为None则使用最新的交易日期

    Returns:
        pd.DataFrame: 包含日期和交易状态的DataFrame
                     列: [date, trading_status]
    """
    logger.info(
        f"开始计算股票 {stock_code} 的交易状态: start_date={start_date}, end_date={end_date}"
    )

    # 1. 加载交易日历
    logger.debug("加载交易日历数据")
    if not dw_exists(TRADE_CALENDAR_DATASET):
        logger.error("交易日历数据不存在，无法计算交易状态")
        return pd.DataFrame()

    calendar_df = dw_query(TRADE_CALENDAR_DATASET)
    if calendar_df.empty:
        logger.error("交易日历数据为空，无法计算交易状态")
        return pd.DataFrame()

    # 过滤交易日
    calendar_df = calendar_df[calendar_df[StandardFields.IS_TRADING_DAY] == 1]

    # 如果未指定日期范围，使用交易日历中的最早和最晚日期
    if start_date is None:
        start_date = calendar_df[StandardFields.CALENDAR_DATE].min()
    if end_date is None:
        end_date = calendar_df[StandardFields.CALENDAR_DATE].max()

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

    # 获取日期范围内的所有交易日
    trade_dates = calendar_df[StandardFields.CALENDAR_DATE].tolist()

    # 2. 获取该股票的上市退市信息
    logger.debug(f"获取股票 {stock_code} 的上市退市信息")
    if not dw_exists(LISTING_DELISTING_DATASET):
        logger.error("上市退市信息数据不存在，无法计算交易状态")
        return pd.DataFrame()

    listing_df = dw_query(LISTING_DELISTING_DATASET)
    if listing_df.empty:
        logger.error("上市退市信息数据为空，无法计算交易状态")
        return pd.DataFrame()

    # 筛选出该股票的上市退市信息
    stock_listing_info = listing_df[listing_df[StandardFields.CODE] == stock_code]

    if stock_listing_info.empty:
        logger.error(f"未找到股票 {stock_code} 的上市退市信息")
        return pd.DataFrame()

    # 3. 获取该股票的停牌信息
    logger.debug(f"获取股票 {stock_code} 的停牌信息")
    if not dw_exists(SUSPEND_INFO_DATASET):
        logger.warning("停牌信息数据不存在，将按照上市退市信息计算交易状态")
        suspend_df = pd.DataFrame()
    else:
        suspend_df = dw_query(SUSPEND_INFO_DATASET)

        if not suspend_df.empty:
            # 标准化列名
            suspend_df = standardize_columns(suspend_df)

            # 筛选出该股票在指定日期范围内的停牌记录
            suspend_df = suspend_df[
                (suspend_df[StandardFields.STOCK_CODE] == stock_code)
                & (suspend_df[StandardFields.TRADE_DATE] >= start_date)
                & (suspend_df[StandardFields.TRADE_DATE] <= end_date)
            ]

    # 4. 计算交易状态
    logger.info(f"计算股票 {stock_code} 的交易状态")

    # 获取上市日期和退市日期并转换为datetime对象
    listing_date = pd.to_datetime(
        stock_listing_info[StandardFields.LISTING_DATE].iloc[0]
    )
    delisting_date = stock_listing_info[StandardFields.DELISTING_DATE].iloc[0]

    # 处理缺失的退市日期
    if pd.isna(delisting_date) or delisting_date == "":
        delisting_date = None
    else:
        delisting_date = pd.to_datetime(delisting_date)

    # 创建结果DataFrame
    result_df = pd.DataFrame({"date": trade_dates, "trading_status": None})

    # 标记停牌日期
    if not suspend_df.empty:
        # 检查停牌记录中是否存在重复日期并发出警告
        date_counts = suspend_df[StandardFields.TRADE_DATE].value_counts()
        duplicate_dates = date_counts[date_counts > 1].index.tolist()
        if duplicate_dates:
            logger.warning(f"停牌记录中存在重复日期: {duplicate_dates}")

        # 创建日期到停牌信息的映射
        date_to_suspend_info = {}

        # 处理所有停牌记录
        for _, row in suspend_df.iterrows():
            date = row[StandardFields.TRADE_DATE]
            suspend_type = row.get("suspend_type", "S")  # 默认为S
            suspend_timing = row.get("suspend_timing", None)  # 停牌时间

            if date not in date_to_suspend_info:
                date_to_suspend_info[date] = []

            date_to_suspend_info[date].append(
                {"type": suspend_type, "timing": suspend_timing}
            )

        # 计算应该标记为停牌的日期
        suspend_dates = set()
        for date, infos in date_to_suspend_info.items():
            # 检查是否应该标记为停牌
            # 优先考虑非R类型且停牌时间为空的记录
            should_suspend = False
            for info in infos:
                # 如果有任何一条记录是非R类型且停牌时间为空，则标记为停牌
                if info["type"] != "R" and (
                    info["timing"] is None or pd.isna(info["timing"])
                ):
                    should_suspend = True
                    break

            if should_suspend:
                suspend_dates.add(date)

        # 使用向量化操作标记停牌状态
        result_df["trading_status"] = result_df["date"].apply(
            lambda date: TRADING_STATUS_SUSPENDED if date in suspend_dates else None
        )

    # 标记未上市、正常交易和退市状态
    for i, row in result_df.iterrows():
        date = row["date"]
        date_dt = pd.to_datetime(date)

        # 如果已经标记为停牌，则跳过
        if row["trading_status"] == TRADING_STATUS_SUSPENDED:
            continue

        # 未上市
        if date_dt < listing_date:
            result_df.at[i, "trading_status"] = TRADING_STATUS_NOT_LISTED
        # 已退市
        elif delisting_date is not None and date_dt > delisting_date:
            result_df.at[i, "trading_status"] = TRADING_STATUS_DELISTED
        # 正常交易
        else:
            result_df.at[i, "trading_status"] = TRADING_STATUS_TRADING

    # 验证交易状态数据的完整性
    # 检查是否所有交易日历中的日期都有对应的交易状态
    status_dates = set(result_df["date"])
    calendar_dates = set(trade_dates)
    if status_dates != calendar_dates:
        missing_dates = calendar_dates - status_dates
        if missing_dates:
            logger.warning(f"部分交易日没有对应的交易状态: {missing_dates}")

    logger.info(f"股票 {stock_code} 交易状态计算完成")
    return result_df


def get_stock_trading_status_on_date(stock_code: str, date: str) -> str:
    """
    获取指定股票在特定日期的交易状态

    Args:
        stock_code: 股票代码
        date: 日期，格式为YYYY-MM-DD

    Returns:
        str: 交易状态，可能的值为：
             TRADING_STATUS_NOT_LISTED (未上市)
             TRADING_STATUS_TRADING (正常交易)
             TRADING_STATUS_SUSPENDED (停牌)
             TRADING_STATUS_DELISTED (退市)
             None: 如果发生错误
    """
    # 检查日期是否为交易日
    calendar_df = dw_query(TRADE_CALENDAR_DATASET)
    if calendar_df.empty:
        logger.error("交易日历数据为空，无法确定交易状态")
        return None

    date_info = calendar_df[calendar_df[StandardFields.CALENDAR_DATE] == date]

    if date_info.empty:
        logger.error(f"未找到日期 {date} 的交易日历信息")
        return None

    if date_info[StandardFields.IS_TRADING_DAY].iloc[0] != 1:
        logger.warning(f"日期 {date} 不是交易日")

    # 获取该股票的上市退市信息
    listing_df = dw_query(LISTING_DELISTING_DATASET)
    if listing_df.empty:
        logger.error("上市退市信息数据为空，无法确定交易状态")
        return None

    stock_listing_info = listing_df[listing_df[StandardFields.CODE] == stock_code]

    if stock_listing_info.empty:
        logger.error(f"未找到股票 {stock_code} 的上市退市信息")
        return None

    # 获取上市日期和退市日期并转换为datetime对象
    listing_date = pd.to_datetime(
        stock_listing_info[StandardFields.LISTING_DATE].iloc[0]
    )
    delisting_date = stock_listing_info[StandardFields.DELISTING_DATE].iloc[0]

    # 处理缺失的退市日期
    if pd.isna(delisting_date) or delisting_date == "":
        delisting_date = None
    else:
        delisting_date = pd.to_datetime(delisting_date)

    # 将查询日期转换为datetime对象
    date_dt = pd.to_datetime(date)

    # 检查是否停牌
    suspend_df = dw_query(SUSPEND_INFO_DATASET)

    if not suspend_df.empty:
        # 标准化列名
        suspend_df = standardize_columns(suspend_df)

        # 筛选当天该股票的记录
        day_suspend = suspend_df[
            (suspend_df[StandardFields.STOCK_CODE] == stock_code)
            & (suspend_df[StandardFields.TRADE_DATE] == date)
        ]

        # 检查是否有需要标记为停牌的记录
        if not day_suspend.empty:
            # 检查停牌记录中是否存在重复日期并发出警告
            if len(day_suspend) > 1:
                logger.warning(f"日期 {date} 存在多条停牌记录: {len(day_suspend)}条")

            # 优先考虑非R类型且停牌时间为空的记录
            should_suspend = False

            for _, row in day_suspend.iterrows():
                suspend_type = row.get("suspend_type", "S")
                suspend_timing = row.get("suspend_timing", None)

                # 只有非R类型且停牌时间为空的记录才会标记为停牌
                if suspend_type != "R" and (
                    suspend_timing is None or pd.isna(suspend_timing)
                ):
                    should_suspend = True
                    break

            if should_suspend:
                return TRADING_STATUS_SUSPENDED

    # 未上市
    if date_dt < listing_date:
        return TRADING_STATUS_NOT_LISTED
    # 已退市
    elif delisting_date is not None and date_dt > delisting_date:
        return TRADING_STATUS_DELISTED
    # 正常交易
    else:
        return TRADING_STATUS_TRADING


def print_stock_trading_history(stock_code: str) -> None:
    """
    打印股票的交易状态历史

    Args:
        stock_code: 股票代码
    """
    # 获取上市退市信息
    listing_df = dw_query(LISTING_DELISTING_DATASET)
    stock_info = listing_df[listing_df[StandardFields.CODE] == stock_code]

    if stock_info.empty:
        print(f"未找到股票 {stock_code} 的信息")
        return

    stock_name = stock_info[StandardFields.NAME].iloc[0]
    listing_date = stock_info[StandardFields.LISTING_DATE].iloc[0]
    delisting_date = stock_info[StandardFields.DELISTING_DATE].iloc[0]

    print(f"股票代码: {stock_code}")
    print(f"股票名称: {stock_name}")
    print(f"上市日期: {listing_date}")

    if pd.isna(delisting_date) or delisting_date == "":
        print("退市日期: 未退市")
    else:
        print(f"退市日期: {delisting_date}")

    # 获取停牌信息
    suspend_df = dw_query(SUSPEND_INFO_DATASET)

    if not suspend_df.empty:
        # 标准化列名
        suspend_df = standardize_columns(suspend_df)

        # 获取该股票的停牌记录
        stock_suspend = suspend_df[suspend_df[StandardFields.STOCK_CODE] == stock_code]

        if not stock_suspend.empty:
            # 按日期排序
            stock_suspend = stock_suspend.sort_values(by=StandardFields.TRADE_DATE)

            print("\n停牌记录:")
            print("注：suspend_type为R的记录会被视为正常交易而非停牌")
            print("注：suspend_type为S但停牌时间不为空的记录会被视为正常交易而非停牌")
            for _, row in stock_suspend.iterrows():
                suspend_date = row[StandardFields.TRADE_DATE]
                suspend_type = row.get("suspend_type", "")
                suspend_timing = row.get("suspend_timing", None)

                # 决定交易状态
                if suspend_type == "R" or (
                    suspend_type == "S"
                    and suspend_timing is not None
                    and pd.notna(suspend_timing)
                ):
                    status = "正常交易"
                else:
                    status = "停牌"

                timing_info = (
                    f", 停牌时间: {suspend_timing}"
                    if suspend_timing is not None and pd.notna(suspend_timing)
                    else ""
                )
                print(f"  {suspend_date}: {suspend_type}{timing_info} ({status})")
        else:
            print("\n无停牌记录")
    else:
        print("\n无法获取停牌信息")


def visualize_stock_trading_status(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> None:
    """
    可视化股票交易状态

    Args:
        stock_code: 股票代码
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        logger.error("缺少绘图库 matplotlib 和/或 seaborn，无法进行可视化")
        print("请安装 matplotlib 和 seaborn 以启用可视化功能")
        return

    # 获取股票交易状态
    status_df = get_stock_trading_status(stock_code, start_date, end_date)

    if status_df.empty:
        logger.error("无法获取股票交易状态数据")
        return

    # 获取股票名称
    listing_df = dw_query(LISTING_DELISTING_DATASET)
    stock_info = listing_df[listing_df[StandardFields.CODE] == stock_code]

    if not stock_info.empty:
        stock_name = stock_info[StandardFields.NAME].iloc[0]
    else:
        stock_name = stock_code

    # 创建映射，将状态码映射为文字说明
    status_map = {
        TRADING_STATUS_NOT_LISTED: "未上市",
        TRADING_STATUS_TRADING: "正常交易",
        TRADING_STATUS_SUSPENDED: "停牌",
        TRADING_STATUS_DELISTED: "退市",
    }

    # 将状态码映射为数值，便于绘图
    status_value_map = {
        TRADING_STATUS_NOT_LISTED: 0,
        TRADING_STATUS_TRADING: 1,
        TRADING_STATUS_SUSPENDED: 2,
        TRADING_STATUS_DELISTED: 3,
    }

    # 添加数值列
    status_df["status_value"] = status_df["trading_status"].map(status_value_map)

    # 设置绘图样式
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))

    # 将日期转换为datetime类型
    status_df["date"] = pd.to_datetime(status_df["date"])

    # 绘制状态变化折线图
    plt.plot(
        status_df["date"],
        status_df["status_value"],
        marker="o",
        linestyle="-",
        markersize=4,
    )

    # 设置y轴刻度和标签
    plt.yticks(
        list(status_value_map.values()),
        [status_map[k] for k in status_value_map.keys()],
    )

    # 设置标题和标签
    plt.title(f"{stock_name}({stock_code}) 交易状态变化")
    plt.xlabel("日期")
    plt.ylabel("交易状态")

    # 自动调整日期标签
    plt.gcf().autofmt_xdate()

    # 添加网格线
    plt.grid(True, linestyle="--", alpha=0.7)

    # 显示图表
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # 示例用法
    stock_code = "600000.SH"  # 浦发银行

    # 打印股票交易历史
    print_stock_trading_history(stock_code)

    # 获取特定日期的交易状态
    status = get_stock_trading_status_on_date(stock_code, "2023-01-03")
    print(f"\n2023-01-03 交易状态: {status}")

    # 可视化股票交易状态
    # visualize_stock_trading_status(stock_code, "2022-01-01", "2023-12-31")
