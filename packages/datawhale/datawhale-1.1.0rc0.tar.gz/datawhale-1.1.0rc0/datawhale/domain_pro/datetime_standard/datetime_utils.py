#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""日期时间工具模块

提供日期时间解析和标准化的工具函数。
"""

import re
import pandas as pd
import warnings
from typing import Union, Optional, Any
from datetime import datetime, date


def parse_datetime(dt_value: Any) -> Optional[datetime]:
    """解析各种格式的日期时间字符串或对象为datetime对象

    支持解析:
    - 字符串日期时间 (多种格式)
    - datetime对象
    - pandas Timestamp对象
    - 日期对象
    - 数值时间戳 (秒/毫秒/微秒/纳秒级)

    Args:
        dt_value: 要解析的日期时间值

    Returns:
        datetime: 解析后的datetime对象，无法解析则返回None
    """
    if dt_value is None:
        return None

    # 已经是datetime对象
    if isinstance(dt_value, datetime):
        return dt_value

    # pandas Timestamp
    if isinstance(dt_value, pd.Timestamp):
        # 使用datetime构造函数创建新对象而不是to_pydatetime()，避免纳秒警告
        return datetime(
            year=dt_value.year,
            month=dt_value.month,
            day=dt_value.day,
            hour=dt_value.hour,
            minute=dt_value.minute,
            second=dt_value.second,
            microsecond=dt_value.microsecond,
        )

    # date对象
    if isinstance(dt_value, date) and not isinstance(dt_value, datetime):
        return datetime(dt_value.year, dt_value.month, dt_value.day)

    # 处理字符串
    if isinstance(dt_value, str):
        # 移除字符串前后的空白字符
        dt_value = dt_value.strip()

        if not dt_value:
            return None

        # 尝试使用pandas解析（支持多种格式）
        try:
            # 对于中文日期格式的特殊处理
            if re.search(r"[年月日]", dt_value):
                dt_value = (
                    dt_value.replace("年", "-").replace("月", "-").replace("日", "")
                )

            # 检测欧洲日期格式（日-月-年）
            # 例如：19-10-2023 或 19/10/2023
            is_european_format = bool(
                re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$", dt_value)
            )

            # 临时禁用警告
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # 根据格式传递正确的参数
                if is_european_format:
                    ts = pd.to_datetime(dt_value, errors="coerce", dayfirst=True)
                else:
                    ts = pd.to_datetime(dt_value, errors="coerce")

                if pd.isna(ts):
                    return None

                # 使用构造函数创建新的datetime对象，避免纳秒警告
                return datetime(
                    year=ts.year,
                    month=ts.month,
                    day=ts.day,
                    hour=ts.hour,
                    minute=ts.minute,
                    second=ts.second,
                    microsecond=ts.microsecond,
                )
        except Exception:
            return None

    # 处理数值时间戳
    if isinstance(dt_value, (int, float)):
        try:
            # 根据位数判断时间戳精度
            timestamp = float(dt_value)

            # 处理秒级时间戳 (10位)
            if timestamp < 1e12:
                return datetime.fromtimestamp(timestamp)

            # 处理毫秒级时间戳 (13位)
            elif timestamp < 1e15:
                return datetime.fromtimestamp(timestamp / 1000)

            # 处理微秒级时间戳 (16位)
            elif timestamp < 1e18:
                return datetime.fromtimestamp(timestamp / 1000000)

            # 处理纳秒级时间戳 (19位)
            else:
                return datetime.fromtimestamp(timestamp / 1000000000)
        except Exception:
            return None

    # 不支持的类型
    return None


def to_standard_date(dt_value: Any) -> str:
    """转换为标准日期格式 (YYYY-MM-DD)

    Args:
        dt_value: 要转换的日期时间值

    Returns:
        str: 标准日期格式的字符串，无法解析则返回空字符串
    """
    dt = parse_datetime(dt_value)
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d")


def to_standard_datetime(dt_value: Any) -> str:
    """转换为标准日期时间格式精确到秒 (YYYY-MM-DD HH:MM:SS)

    Args:
        dt_value: 要转换的日期时间值

    Returns:
        str: 标准日期时间格式的字符串，无法解析则返回空字符串
    """
    dt = parse_datetime(dt_value)
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def to_standard_datetime_ns(dt_value: Any) -> str:
    """转换为标准日期时间格式精确到纳秒 (YYYY-MM-DD HH:MM:SS.ns)

    Args:
        dt_value: 要转换的日期时间值

    Returns:
        str: 标准日期时间格式的字符串，无法解析则返回空字符串
    """
    dt = parse_datetime(dt_value)
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def is_valid_datetime(dt_value: Any) -> bool:
    """检查值是否可以转换为有效的日期时间

    Args:
        dt_value: 要检查的值

    Returns:
        bool: 是否为有效日期时间
    """
    return parse_datetime(dt_value) is not None
