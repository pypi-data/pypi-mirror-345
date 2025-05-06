#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DataWhale函数模块

提供函数封装、参数定义和验证功能
"""

from .parameter import ParameterType, Parameter
from .function import Function, wrap_function
from .validation import (
    validate_param,
    validate_params,
    validate_string_param,
    validate_integer_param,
    validate_float_param,
    validate_boolean_param,
    validate_array_param,
    validate_object_param,
)

# 简化的装饰器接口
function = wrap_function

__all__ = [
    "ParameterType",
    "Parameter",
    "Function",
    "wrap_function",
    "function",
    "validate_param",
    "validate_params",
    "validate_string_param",
    "validate_integer_param",
    "validate_float_param",
    "validate_boolean_param",
    "validate_array_param",
    "validate_object_param",
]

__version__ = "0.1.0"
