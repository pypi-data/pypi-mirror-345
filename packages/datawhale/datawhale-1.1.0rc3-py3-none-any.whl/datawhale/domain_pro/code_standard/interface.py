#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""证券代码标准化接口模块

为用户提供简单易用的证券代码标准化接口，封装StockCodeStandardizer的功能。
提供证券代码的标准化、格式转换等常用操作。
本模块使用函数式接口，方便用户直接调用。
"""

from typing import List, Optional, Union
from .standardizer import StockCodeStandardizer


def standardize_code(code: str, source: Optional[str] = None) -> str:
    """标准化证券代码

    将不同格式的证券代码统一转换为标准格式（如：600000.SH）

    Args:
        code: 原始证券代码
        source: 数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata
               如果提供此参数，将按照指定数据源的格式解析代码

    Returns:
        str: 标准化后的证券代码，格式为[数字代码].[交易所代码]，如600000.SH

    Raises:
        ValueError: 当代码格式无效或无法判断交易所时抛出

    Examples:
        >>> standardize_code("600000.XSHG")
        '600000.SH'
        >>> standardize_code("sh.600000")
        '600000.SH'
        >>> standardize_code("000001", source="akshare")
        '000001.SZ'
    """
    return StockCodeStandardizer.standardize(code, source)


def to_tushare_code(code: str) -> str:
    """将证券代码转换为Tushare格式

    Args:
        code: 任意格式的证券代码

    Returns:
        str: Tushare格式的证券代码（如：600000.SH）

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    return StockCodeStandardizer.to_source_format(code, "tushare")


def to_baostock_code(code: str) -> str:
    """将证券代码转换为Baostock格式

    Args:
        code: 任意格式的证券代码

    Returns:
        str: Baostock格式的证券代码（如：sh.600000）

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    return StockCodeStandardizer.to_source_format(code, "baostock")


def to_akshare_code(code: str) -> str:
    """将证券代码转换为Akshare格式

    Args:
        code: 任意格式的证券代码

    Returns:
        str: Akshare格式的证券代码（如：600000）

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    return StockCodeStandardizer.to_source_format(code, "akshare")


def to_joinquant_code(code: str) -> str:
    """将证券代码转换为聚宽格式

    Args:
        code: 任意格式的证券代码

    Returns:
        str: 聚宽格式的证券代码（如：600000.XSHG）

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    return StockCodeStandardizer.to_source_format(code, "joinquant")


def to_rqdata_code(code: str) -> str:
    """将证券代码转换为米筐格式

    Args:
        code: 任意格式的证券代码

    Returns:
        str: 米筐格式的证券代码（如：600000.XSHG）

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    return StockCodeStandardizer.to_source_format(code, "rqdata")


def to_source_code(code: str, target_source: str) -> str:
    """将证券代码转换为指定数据源的格式

    Args:
        code: 任意格式的证券代码
        target_source: 目标数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata

    Returns:
        str: 目标数据源格式的证券代码

    Raises:
        ValueError: 当代码格式无效或数据源名称无效时抛出
    """
    return StockCodeStandardizer.to_source_format(code, target_source)


def standardize_batch_codes(
    codes: List[str], source: Optional[str] = None
) -> List[str]:
    """批量标准化证券代码

    Args:
        codes: 原始证券代码列表
        source: 数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata

    Returns:
        List[str]: 标准化后的证券代码列表

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    return [StockCodeStandardizer.standardize(code, source) for code in codes]


def convert_batch_codes(codes: List[str], target_source: str) -> List[str]:
    """批量将证券代码转换为指定数据源的格式

    Args:
        codes: 原始证券代码列表
        target_source: 目标数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata

    Returns:
        List[str]: 目标数据源格式的证券代码列表

    Raises:
        ValueError: 当代码格式无效或数据源名称无效时抛出
    """
    return [
        StockCodeStandardizer.to_source_format(code, target_source) for code in codes
    ]


def get_standard_code_supported_sources() -> List[str]:
    """获取所有支持的数据源

    Returns:
        List[str]: 所有支持的数据源名称列表
    """
    return list(StockCodeStandardizer.SOURCE_FORMATS.keys())


def get_standard_exchange(code: str, source: Optional[str] = None) -> str:
    """获取证券代码对应的交易所代码

    Args:
        code: 证券代码
        source: 数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata

    Returns:
        str: 交易所代码，如SH, SZ, BJ, HK, OF

    Raises:
        ValueError: 当代码格式无效或无法判断交易所时抛出
    """
    std_code = StockCodeStandardizer.standardize(code, source)
    return std_code.split(".")[-1]
