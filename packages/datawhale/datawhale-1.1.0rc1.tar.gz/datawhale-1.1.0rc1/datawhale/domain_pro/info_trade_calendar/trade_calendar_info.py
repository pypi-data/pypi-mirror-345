#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
交易日历信息模块

提供获取和更新交易日历信息的功能
"""

import pandas as pd
import baostock as bs
from typing import Optional
from datetime import datetime, timedelta
import os

from datawhale.domain_pro.field_standard import StandardFields, get_fields_type
from datawhale.domain_pro import standardize_dataframe
from datawhale.domain_pro.datetime_standard import to_standard_date
from datawhale.infrastructure_pro.storage import (
    dw_create_dataset,
    dw_save,
    dw_exists,
    dw_query,
    dw_query_last_line,
)

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)

# BaoStock数据源名称
BAOSTOCK_SOURCE = "baostock"

# 交易日历信息数据集名称
TRADE_CALENDAR_DATASET = "trade_calendar_info"

# 需要保留的标准字段列表
REQUIRED_COLUMNS = [
    StandardFields.CALENDAR_DATE,  # 日期
    StandardFields.IS_TRADING_DAY,  # 是否交易日
]

# 日期字段列表
DATE_COLUMNS = [StandardFields.CALENDAR_DATE]

# 排序字段
SORT_BY_FIELD = StandardFields.CALENDAR_DATE  # 按日期字段排序


def fetch_trade_calendar(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    从远程数据源获取交易日历信息

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD

    Returns:
        pd.DataFrame: 包含交易日历信息的DataFrame
    """
    # 如果未指定日期，则默认获取近一年的数据
    if not start_date or not end_date:
        today = datetime.now()
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        if not start_date:
            # 默认获取一年的数据
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")

    # 标准化日期
    start_date = to_standard_date(start_date)
    end_date = to_standard_date(end_date)
    if not start_date or not end_date:
        logger.error(f"日期格式无效: start_date={start_date}, end_date={end_date}")
        return pd.DataFrame()

    logger.info(
        f"开始从远程接口获取交易日历信息: start_date={start_date}, end_date={end_date}"
    )

    # 直接从远程接口获取
    return _fetch_trade_calendar_from_remote(start_date, end_date)


def _fetch_trade_calendar_from_remote(start_date: str, end_date: str) -> pd.DataFrame:
    """
    从远程接口获取交易日历信息

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD

    Returns:
        pd.DataFrame: 包含交易日历信息的DataFrame
    """
    logger.info(
        f"从远程接口获取交易日历信息: start_date={start_date}, end_date={end_date}"
    )

    # 登录BaoStock
    lg = bs.login()
    if lg.error_code != "0":
        logger.error(f"登录BaoStock失败: {lg.error_code} - {lg.error_msg}")
        raise ConnectionError(f"登录BaoStock失败: {lg.error_code} - {lg.error_msg}")

    try:
        # 查询交易日信息
        rs = bs.query_trade_dates(start_date=start_date, end_date=end_date)

        if rs.error_code != "0":
            logger.error(f"查询交易日历信息失败: {rs.error_code} - {rs.error_msg}")
            raise Exception(f"查询交易日历信息失败: {rs.error_code} - {rs.error_msg}")

        # 将查询结果转换为DataFrame
        data_list = []
        while (rs.error_code == "0") & rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            logger.warning(
                f"未查询到交易日历信息: start_date={start_date}, end_date={end_date}"
            )
            return pd.DataFrame()

        # 创建DataFrame
        result = pd.DataFrame(data_list, columns=rs.fields)

        # 标准化处理
        result = standardize_dataframe(
            df=result,
            source=BAOSTOCK_SOURCE,
            code_field=None,  # 不需要标准化证券代码
            date_fields=DATE_COLUMNS,
            required_columns=REQUIRED_COLUMNS,
            sort_by=SORT_BY_FIELD,  # 使用标准化后的字段名
            ascending=True,  # 升序排序
        )

        logger.info(f"从远程接口获取交易日历信息完成: 共{len(result)}条记录")

        # 保存到本地存储以便下次使用
        try:
            save_trade_calendar_info(result)
        except Exception as e:
            logger.warning(f"保存交易日历信息到本地存储失败: {str(e)}")

        return result

    finally:
        # 登出BaoStock
        bs.logout()


def save_trade_calendar_info(data: pd.DataFrame) -> bool:
    """
    保存交易日历信息到数据集

    Args:
        data: 交易日历信息DataFrame

    Returns:
        bool: 保存是否成功
    """
    logger.info(f"开始保存交易日历信息: 共{len(data)}条记录")

    # 检查数据集是否存在，不存在则创建
    if not dw_exists(TRADE_CALENDAR_DATASET):
        # 获取字段类型信息
        dtypes = get_fields_type(list(data.columns))

        # 创建数据集
        dw_create_dataset(
            name=TRADE_CALENDAR_DATASET,
            dtypes=dtypes,
            update_mode="update",  # 采用更新模式，以便智能更新
        )
        logger.info(f"创建交易日历信息数据集: {TRADE_CALENDAR_DATASET}")

    try:
        # 保存整个数据集
        dw_save(
            data=data,
            data_name=TRADE_CALENDAR_DATASET,
            mode="update",  # 使用更新模式
            update_key=StandardFields.CALENDAR_DATE,  # 使用日历日期作为更新键
        )
        logger.info(f"保存交易日历信息成功")
        return True
    except Exception as e:
        logger.error(f"保存交易日历信息失败: {str(e)}")
        return False


def update_trade_calendar_info(days: int = 365) -> bool:
    """
    更新交易日历信息

    Args:
        days: 更新的天数，默认为一年，当无法获取最近记录时使用此参数向前推算

    Returns:
        bool: 更新是否成功
    """
    # 获取最后一条记录的日期作为起始日期
    from datawhale.infrastructure_pro.storage import dw_query_last_line

    # 设置默认的开始日期（如果无法获取最后一条记录）
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # 如果数据集存在，尝试获取最后一条记录
    if dw_exists(TRADE_CALENDAR_DATASET):
        try:
            # 读取最后一行数据
            last_row = dw_query_last_line(TRADE_CALENDAR_DATASET)
            if last_row is not None and not last_row.empty:
                # 使用最后一行的日历日期作为开始日期
                last_date = last_row[SORT_BY_FIELD].iloc[0]
                # 获取后一天作为开始日期（避免重复获取最后一天的数据）
                start_date_obj = datetime.strptime(last_date, "%Y-%m-%d") + timedelta(
                    days=1
                )
                start_date = start_date_obj.strftime("%Y-%m-%d")
                logger.info(f"根据最后一条记录设置开始日期: {start_date}")
        except Exception as e:
            logger.warning(f"获取最后一条记录失败，使用默认开始日期: {str(e)}")

    logger.info(f"开始更新交易日历信息: start_date={start_date}, end_date={end_date}")

    # 从远程接口获取数据
    data = fetch_trade_calendar(start_date, end_date)

    if data.empty:
        logger.warning("未获取到交易日历信息，更新失败")
        return False

    # 保存到本地存储
    try:
        result = save_trade_calendar_info(data)
        logger.info(f"更新交易日历信息完成: 共{len(data)}条记录")
        return result
    except Exception as e:
        logger.error(f"更新交易日历信息失败: {str(e)}")
        return False


def is_trading_day(date: str) -> bool:
    """
    判断指定日期是否为交易日

    Args:
        date: 日期，格式为YYYY-MM-DD

    Returns:
        bool: 是否为交易日
    """
    # 标准化日期
    std_date = to_standard_date(date)
    if not std_date:
        return False

    # 获取该日期的交易日历信息
    df = fetch_trade_calendar(start_date=std_date, end_date=std_date)

    if df.empty:
        return False

    # 判断是否为交易日
    return df.iloc[0][StandardFields.IS_TRADING_DAY] == 1


def get_prev_trading_day(date: str, n: int = 1) -> str:
    """
    获取指定日期前n个交易日的日期

    Args:
        date: 日期，格式为YYYY-MM-DD
        n: 前n个交易日，默认为1

    Returns:
        str: 前n个交易日的日期，格式为YYYY-MM-DD
    """
    if n <= 0:
        return date

    # 标准化日期
    std_date = to_standard_date(date)
    if not std_date:
        return ""

    # 为了确保能获取到前n个交易日，向前推30*n天
    date_obj = datetime.strptime(std_date, "%Y-%m-%d")
    start_date = (date_obj - timedelta(days=30 * n)).strftime("%Y-%m-%d")

    # 获取交易日历信息
    df = fetch_trade_calendar(start_date=start_date, end_date=std_date)

    if df.empty:
        return ""

    # 筛选交易日
    trading_days = df[df[StandardFields.IS_TRADING_DAY] == 1][
        StandardFields.CALENDAR_DATE
    ].tolist()
    trading_days.sort()

    # 找到当前日期在交易日列表中的位置
    try:
        curr_index = trading_days.index(std_date)
    except ValueError:
        # 如果当前日期不是交易日，找到下一个交易日的位置
        for i, day in enumerate(trading_days):
            if day > std_date:
                curr_index = i
                break
        else:
            # 如果没有找到，返回空
            return ""

    # 获取前n个交易日
    if curr_index >= n:
        return trading_days[curr_index - n]
    else:
        # 如果交易日不足n个，返回第一个交易日
        return trading_days[0] if trading_days else ""


def get_next_trading_day(date: str, n: int = 1) -> str:
    """
    获取指定日期后n个交易日的日期

    Args:
        date: 日期，格式为YYYY-MM-DD
        n: 后n个交易日，默认为1

    Returns:
        str: 后n个交易日的日期，格式为YYYY-MM-DD
    """
    if n <= 0:
        return date

    # 标准化日期
    std_date = to_standard_date(date)
    if not std_date:
        return ""

    # 为了确保能获取到后n个交易日，向后推30*n天
    date_obj = datetime.strptime(std_date, "%Y-%m-%d")
    end_date = (date_obj + timedelta(days=30 * n)).strftime("%Y-%m-%d")

    # 获取交易日历信息
    df = fetch_trade_calendar(start_date=std_date, end_date=end_date)

    if df.empty:
        return ""

    # 筛选交易日
    trading_days = df[df[StandardFields.IS_TRADING_DAY] == 1][
        StandardFields.CALENDAR_DATE
    ].tolist()
    trading_days.sort()

    # 找到当前日期在交易日列表中的位置
    try:
        curr_index = trading_days.index(std_date)
    except ValueError:
        # 如果当前日期不是交易日，找到下一个交易日的位置
        for i, day in enumerate(trading_days):
            if day > std_date:
                curr_index = i - 1  # 用前一个位置表示，方便后续计算
                break
        else:
            # 如果没有找到，返回空
            return ""

    # 获取后n个交易日
    if curr_index + n < len(trading_days):
        return trading_days[curr_index + n]
    else:
        # 如果交易日不足n个，返回最后一个交易日
        return trading_days[-1] if trading_days else ""


def get_trading_days(start_date: str, end_date: str) -> list:
    """
    获取指定日期范围内的所有交易日

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD

    Returns:
        list: 交易日列表，格式为['YYYY-MM-DD', 'YYYY-MM-DD', ...]
    """
    # 标准化日期
    start_date = to_standard_date(start_date)
    end_date = to_standard_date(end_date)

    if not start_date or not end_date:
        logger.error(f"日期格式无效: start_date={start_date}, end_date={end_date}")
        return []

    logger.info(f"开始获取交易日列表: start_date={start_date}, end_date={end_date}")

    # 检查数据集是否存在
    if not dw_exists(TRADE_CALENDAR_DATASET):
        logger.warning(f"本地存储中不存在交易日历数据集，将从远程接口获取")
        # 从远程获取数据
        df = _fetch_trade_calendar_from_remote(start_date, end_date)
    else:
        try:
            # 使用dw_query查询数据
            # 正确使用dw_query，通过field_values参数传递日期范围条件
            # 由于没有简单的区间查询方式，我们需要获取所有数据然后在内存中过滤
            df = dw_query(TRADE_CALENDAR_DATASET)

            if df is not None and not df.empty:
                # 在内存中筛选日期范围
                mask = (df[StandardFields.CALENDAR_DATE] >= start_date) & (
                    df[StandardFields.CALENDAR_DATE] <= end_date
                )
                df = df[mask]

            if df is None or df.empty:
                logger.warning(
                    f"本地存储中未找到指定日期范围的交易日历数据，将从远程接口获取"
                )
                # 如果没有查询到数据，从远程获取
                df = _fetch_trade_calendar_from_remote(start_date, end_date)
        except Exception as e:
            logger.error(f"查询交易日历数据失败: {str(e)}")
            # 出错时从远程获取
            df = _fetch_trade_calendar_from_remote(start_date, end_date)

    if df is None or df.empty:
        logger.warning(f"未获取到交易日历数据")
        return []

    # 筛选交易日（is_trading_day为1的记录）
    trading_days_df = df[df[StandardFields.IS_TRADING_DAY] == 1]

    # 提取交易日期并排序
    trading_days = sorted(trading_days_df[StandardFields.CALENDAR_DATE].tolist())

    logger.info(f"获取交易日列表完成: 共{len(trading_days)}个交易日")

    return trading_days


def get_trade_calendar_info(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取交易日历信息

    首先尝试从本地存储读取数据，如果本地没有数据再调用远程接口

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD

    Returns:
        pd.DataFrame: 包含交易日历信息的DataFrame
    """
    # 如果未指定日期，则默认获取近一年的数据
    if not start_date or not end_date:
        today = datetime.now()
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        if not start_date:
            # 默认获取一年的数据
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")

    # 标准化日期
    start_date = to_standard_date(start_date)
    end_date = to_standard_date(end_date)
    if not start_date or not end_date:
        logger.error(f"日期格式无效: start_date={start_date}, end_date={end_date}")
        return pd.DataFrame()

    logger.info(f"开始获取交易日历信息: start_date={start_date}, end_date={end_date}")

    # 先尝试从本地存储读取数据
    if dw_exists(TRADE_CALENDAR_DATASET):
        logger.info(f"尝试从本地存储读取交易日历数据")
        try:
            # 直接读取CSV文件，而不是使用dw_query
            csv_path = os.path.join(
                os.environ.get(
                    "DW_DATA_DIR",
                    "/Users/hanswang/Desktop/long_road/DataWhale/cache/data",
                ),
                TRADE_CALENDAR_DATASET,
                "data.csv",
            )

            if os.path.exists(csv_path):
                # 读取CSV文件
                local_data = pd.read_csv(csv_path)

                # 筛选日期范围内的数据
                if "calendar_date" in local_data.columns:
                    mask = (local_data["calendar_date"] >= start_date) & (
                        local_data["calendar_date"] <= end_date
                    )
                    local_data = local_data[mask]

                if not local_data.empty:
                    logger.info(
                        f"成功从本地存储读取交易日历数据: 共{len(local_data)}条记录"
                    )

                    # 结果列名标准化 - 确保calendar_date符合标准
                    if (
                        "calendar_date" in local_data.columns
                        and StandardFields.CALENDAR_DATE not in local_data.columns
                    ):
                        local_data = local_data.rename(
                            columns={"calendar_date": StandardFields.CALENDAR_DATE}
                        )

                    # 按日期升序排序
                    local_data = local_data.sort_values(
                        by=SORT_BY_FIELD, ascending=True
                    )

                    return local_data

            logger.warning(f"本地存储中未找到交易日历数据或数据为空，将从远程接口获取")
        except Exception as e:
            logger.error(f"从本地存储读取交易日历数据失败: {str(e)}")
    else:
        logger.warning(f"本地存储中不存在交易日历数据集，将从远程接口获取")

    # 如果本地没有数据，则从远程接口获取
    return fetch_trade_calendar(start_date, end_date)
