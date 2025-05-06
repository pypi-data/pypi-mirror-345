#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
参数验证模块

提供函数参数的验证功能
"""

import re
from typing import Any, Dict, List, Optional, Union, Tuple

from .parameter import Parameter, ParameterType


def validate_param(param: Parameter, value: Any) -> Any:
    """
    验证单个参数

    Args:
        param: 参数定义
        value: 参数值

    Returns:
        验证后的参数值

    Raises:
        ValueError: 如果参数验证失败
    """
    # 检查必需参数
    if value is None:
        if param.is_required:
            raise ValueError(f"参数 '{param.name}' 是必需的")
        return param.default_value

    # 根据类型验证
    param_type = param.param_type

    if param_type == ParameterType.STRING:
        return validate_string_param(param, value)
    elif param_type == ParameterType.INTEGER:
        return validate_integer_param(param, value)
    elif param_type == ParameterType.FLOAT:
        return validate_float_param(param, value)
    elif param_type == ParameterType.BOOLEAN:
        return validate_boolean_param(param, value)
    elif param_type == ParameterType.ARRAY:
        return validate_array_param(param, value)
    elif param_type == ParameterType.OBJECT:
        return validate_object_param(param, value)
    else:
        # 对于ANY类型，直接返回值
        return value


def validate_string_param(param: Parameter, value: Any) -> str:
    """验证字符串参数"""
    # 尝试转换为字符串
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception as e:
            raise ValueError(f"参数 '{param.name}' 无法转换为字符串: {str(e)}")

    # 验证规则
    rules = param.validation_rules

    # 长度验证
    min_length = rules.get("min_length")
    if min_length is not None and len(value) < min_length:
        raise ValueError(f"参数 '{param.name}' 长度至少为 {min_length}")

    max_length = rules.get("max_length")
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"参数 '{param.name}' 长度不能超过 {max_length}")

    # 模式验证
    pattern = rules.get("pattern")
    if pattern is not None and not re.match(pattern, value):
        raise ValueError(f"参数 '{param.name}' 不匹配模式 '{pattern}'")

    # 枚举验证
    enum = rules.get("enum")
    if enum is not None and value not in enum:
        raise ValueError(f"参数 '{param.name}' 必须是以下值之一: {', '.join(enum)}")

    return value


def validate_integer_param(param: Parameter, value: Any) -> int:
    """验证整数参数"""
    # 尝试转换为整数
    if isinstance(value, bool):
        raise ValueError(f"参数 '{param.name}' 必须是整数，不能是布尔值")

    if not isinstance(value, int):
        try:
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            else:
                value = int(value)
        except Exception as e:
            raise ValueError(f"参数 '{param.name}' 无法转换为整数: {str(e)}")

    # 验证规则
    rules = param.validation_rules

    # 范围验证
    min_value = rules.get("min_value")
    if min_value is not None and value < min_value:
        raise ValueError(f"参数 '{param.name}' 不能小于 {min_value}")

    max_value = rules.get("max_value")
    if max_value is not None and value > max_value:
        raise ValueError(f"参数 '{param.name}' 不能大于 {max_value}")

    # 枚举验证
    enum = rules.get("enum")
    if enum is not None and value not in enum:
        raise ValueError(
            f"参数 '{param.name}' 必须是以下值之一: {', '.join(map(str, enum))}"
        )

    return value


def validate_float_param(param: Parameter, value: Any) -> float:
    """验证浮点数参数"""
    # 尝试转换为浮点数
    if isinstance(value, bool):
        raise ValueError(f"参数 '{param.name}' 必须是数字，不能是布尔值")

    if not isinstance(value, (int, float)):
        try:
            value = float(value)
        except Exception as e:
            raise ValueError(f"参数 '{param.name}' 无法转换为浮点数: {str(e)}")
    else:
        value = float(value)

    # 验证规则
    rules = param.validation_rules

    # 范围验证
    min_value = rules.get("min_value")
    if min_value is not None and value < min_value:
        raise ValueError(f"参数 '{param.name}' 不能小于 {min_value}")

    max_value = rules.get("max_value")
    if max_value is not None and value > max_value:
        raise ValueError(f"参数 '{param.name}' 不能大于 {max_value}")

    return value


def validate_boolean_param(param: Parameter, value: Any) -> bool:
    """验证布尔参数"""
    # 尝试转换为布尔值
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        # 只允许0和1转换为布尔值
        if value == 0:
            return False
        elif value == 1:
            return True
        else:
            raise ValueError(f"参数 '{param.name}' 无法转换为布尔值：只接受0和1")

    if isinstance(value, str):
        # 字符串转布尔值
        value_lower = value.lower()
        if value_lower in ("true", "yes", "y", "1"):
            return True
        elif value_lower in ("false", "no", "n", "0"):
            return False

    raise ValueError(f"参数 '{param.name}' 无法转换为布尔值")


def validate_array_param(param: Parameter, value: Any) -> List:
    """验证数组参数"""
    # 尝试转换为数组
    if not isinstance(value, (list, tuple)):
        try:
            # 尝试转换字符串为JSON数组
            if isinstance(value, str):
                import json

                value = json.loads(value)
                if not isinstance(value, list):
                    raise ValueError("JSON解析结果不是数组")
            else:
                raise ValueError("不是有效的数组类型")
        except Exception as e:
            raise ValueError(f"参数 '{param.name}' 无法转换为数组: {str(e)}")

    # 确保结果是列表
    if isinstance(value, tuple):
        value = list(value)

    # 验证规则
    rules = param.validation_rules

    # 长度验证
    min_length = rules.get("min_length")
    if min_length is not None and len(value) < min_length:
        raise ValueError(f"参数 '{param.name}' 至少需要 {min_length} 个元素")

    max_length = rules.get("max_length")
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"参数 '{param.name}' 最多允许 {max_length} 个元素")

    return value


def validate_object_param(param: Parameter, value: Any) -> Dict:
    """验证对象参数"""
    # 尝试转换为对象
    if not isinstance(value, dict):
        try:
            # 尝试转换字符串为JSON对象
            if isinstance(value, str):
                import json

                value = json.loads(value)
                if not isinstance(value, dict):
                    raise ValueError("JSON解析结果不是对象")
            else:
                raise ValueError("不是有效的对象类型")
        except Exception as e:
            raise ValueError(f"参数 '{param.name}' 无法转换为对象: {str(e)}")

    return value


def validate_params(
    params: Dict[str, Any], param_defs: List[Parameter]
) -> Dict[str, Any]:
    """
    验证参数字典中所有参数

    Args:
        params: 待验证的参数字典
        param_defs: 参数定义列表

    Returns:
        验证后的参数字典

    Raises:
        ValueError: 如果任何参数验证失败
    """
    validated = {}
    errors = []

    # 验证所有已提供的参数
    param_dict = {p.name: p for p in param_defs}

    # 验证提供的参数
    for name, value in params.items():
        if name in param_dict:
            try:
                validated[name] = validate_param(param_dict[name], value)
            except ValueError as e:
                errors.append(str(e))
        else:
            # 未知参数
            validated[name] = value

    # 检查必需参数是否都已提供
    for param in param_defs:
        if param.is_required and param.name not in params:
            errors.append(f"缺少必需参数 '{param.name}'")
        elif param.name not in params and param.has_default():
            # 使用默认值
            validated[param.name] = param.default_value

    # 如果有错误，抛出异常
    if errors:
        raise ValueError("; ".join(errors))

    return validated
