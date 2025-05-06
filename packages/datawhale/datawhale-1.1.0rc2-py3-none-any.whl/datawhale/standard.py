#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
标准化接口模块

提供字段标准化、证券代码标准化和日期时间标准化等功能
"""

# 从fields模块导入
from datawhale.domain_pro.field_standard import (
    get_field,
    get_all_fields,
    add_field,
    update_field,
    remove_field,
    set_source_mapping,
    remove_source_mapping,
    get_field_by_source,
    get_all_data_sources,
    get_field_source_mapping,
    search_fields,
    reload,
    standardize_field,
    standardize_fields,
    convert_field,
    get_field_type,
    get_fields_type,
    get_field_value_map,
    convert_dataframe_types,
    # 字段标准化装饰器
    standardize_field_values,
    standardize_param_field,
    standardize_param_fields,
    standardize_result_field,
    standardize_param_dataframe_columns,
    standardize_result_dataframe_columns,
)

# 从证券代码标准化模块导入
from datawhale.domain_pro.code_standard import (
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
    # 证券代码标准化装饰器
    standardize_stock_codes,
    standardize_param_stock_code,
    standardize_param_stock_codes,
    standardize_result_stock_code,
    standardize_param_dataframe_stock_codes,
    standardize_result_dataframe_stock_codes,
)

# 从datetime_standard模块导入
from datawhale.domain_pro.datetime_standard import (
    parse_datetime,
    to_standard_date,
    to_standard_datetime,
    to_standard_datetime_ns,
    standard_datetime,
)

__all__ = [
    # fields模块
    "get_field",
    "get_all_fields",
    "add_field",
    "update_field",
    "remove_field",
    "set_source_mapping",
    "remove_source_mapping",
    "get_field_by_source",
    "get_all_data_sources",
    "get_field_source_mapping",
    "search_fields",
    "reload",
    "standardize_field",
    "standardize_fields",
    "convert_field",
    "get_field_type",
    "get_fields_type",
    "get_field_value_map",
    "convert_dataframe_types",
    # 字段标准化装饰器
    "standardize_field_values",
    "standardize_param_field",
    "standardize_param_fields",
    "standardize_result_field",
    "standardize_param_dataframe_columns",
    "standardize_result_dataframe_columns",
    # 证券代码标准化模块
    "standardize_code",
    "to_tushare_code",
    "to_baostock_code",
    "to_akshare_code",
    "to_joinquant_code",
    "to_rqdata_code",
    "to_source_code",
    "standardize_batch_codes",
    "convert_batch_codes",
    "get_standard_code_supported_sources",
    "get_standard_exchange",
    # 证券代码标准化装饰器
    "standardize_stock_codes",
    "standardize_param_stock_code",
    "standardize_param_stock_codes",
    "standardize_result_stock_code",
    "standardize_param_dataframe_stock_codes",
    "standardize_result_dataframe_stock_codes",
    # datetime_standard模块
    "parse_datetime",
    "to_standard_date",
    "to_standard_datetime",
    "to_standard_datetime_ns",
    "standard_datetime",
]
