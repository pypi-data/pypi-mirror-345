#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""证券代码标准化模块

提供证券代码的标准化和转换功能，支持不同数据源格式的证券代码统一处理和转换。
支持通过装饰器自动标准化函数参数和返回值中的证券代码。
"""

from .standardizer import StockCodeStandardizer
from .interface import (
    standardize_code,
    to_tushare_code,
    to_baostock_code,
    to_akshare_code,
    to_joinquant_code,
    to_rqdata_code,
    to_source_code,
    standardize_batch_codes,
    convert_batch_codes,
    get_standard_code_supported_sources,
    get_standard_exchange,
)
from .decorators import (
    # 标准化装饰器
    standardize_stock_codes,
    standardize_param_stock_code,
    standardize_param_stock_codes,
    standardize_result_stock_code,
    standardize_param_dataframe_stock_codes,
    standardize_result_dataframe_stock_codes,
)

__all__ = [
    # 类
    "StockCodeStandardizer",
    # 单个代码处理
    "standardize_code",
    "to_tushare_code",
    "to_baostock_code",
    "to_akshare_code",
    "to_joinquant_code",
    "to_rqdata_code",
    "to_source_code",
    # 批量代码处理
    "standardize_batch_codes",
    "convert_batch_codes",
    # 工具函数
    "get_standard_code_supported_sources",
    "get_standard_exchange",
    # 标准化装饰器
    "standardize_stock_codes",
    "standardize_param_stock_code",
    "standardize_param_stock_codes",
    "standardize_result_stock_code",
    "standardize_param_dataframe_stock_codes",
    "standardize_result_dataframe_stock_codes",
]
