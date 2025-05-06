#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""字段相关模块

包含字段定义、管理和标准化相关的代码。
"""

from .fields import Fields
from .field_manager import FieldManager
from .standard_fields import StandardFields
from .interface import (
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
)
from .decorators import (
    # 新命名的装饰器
    standardize_field_values,
    standardize_param_field,
    standardize_param_fields,
    standardize_result_field,
    standardize_param_dataframe_columns,
    standardize_result_dataframe_columns,
)

__all__ = [
    "Fields",
    "FieldManager",
    "StandardFields",
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
    # 新的标准化装饰器
    "standardize_field_values",
    "standardize_param_field",
    "standardize_param_fields",
    "standardize_result_field",
    "standardize_param_dataframe_columns",
    "standardize_result_dataframe_columns",
]
