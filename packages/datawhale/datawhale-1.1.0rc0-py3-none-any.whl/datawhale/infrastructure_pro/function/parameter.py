#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
参数定义模块

提供函数参数的类型定义和验证功能
"""

import logging
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum


class ParameterType(str, Enum):
    """参数类型枚举"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ANY = "any"

    @classmethod
    def from_python_type(cls, python_type: Type) -> "ParameterType":
        """从Python类型推断参数类型"""
        if python_type == str:
            return cls.STRING
        elif python_type == int:
            return cls.INTEGER
        elif python_type == float:
            return cls.FLOAT
        elif python_type == bool:
            return cls.BOOLEAN
        elif (
            python_type == list
            or python_type == tuple
            or getattr(python_type, "__origin__", None) in (list, tuple)
        ):
            return cls.ARRAY
        elif python_type == dict or getattr(python_type, "__origin__", None) == dict:
            return cls.OBJECT
        else:
            return cls.ANY

    @classmethod
    def from_str(cls, type_str: str) -> "ParameterType":
        """从字符串创建参数类型"""
        try:
            return cls(type_str.lower())
        except ValueError:
            return cls.ANY


@dataclass
class Parameter:
    """函数参数定义"""

    name: str
    description: str = ""
    param_type: Union[ParameterType, str] = ParameterType.ANY
    is_required: bool = True
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.param_type, str):
            self.param_type = ParameterType.from_str(self.param_type)

    def has_default(self) -> bool:
        """是否有默认值"""
        return not self.is_required or self.default_value is not None

    def validate(self, value: Any) -> tuple[bool, str]:
        """
        验证参数值是否有效

        Args:
            value: 要验证的值

        Returns:
            (是否有效, 错误消息)
        """
        if value is None:
            if self.is_required:
                return False, f"参数 '{self.name}' 是必需的"
            return True, ""

        # 类型检查
        if self.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                return False, f"参数 '{self.name}' 必须是字符串"
        elif self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                return False, f"参数 '{self.name}' 必须是整数"
        elif self.param_type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False, f"参数 '{self.name}' 必须是数字"
        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"参数 '{self.name}' 必须是布尔值"
        elif self.param_type == ParameterType.ARRAY:
            if not isinstance(value, (list, tuple)):
                return False, f"参数 '{self.name}' 必须是数组"
        elif self.param_type == ParameterType.OBJECT:
            if not isinstance(value, dict):
                return False, f"参数 '{self.name}' 必须是对象"

        # 其他验证规则
        for rule, rule_value in self.validation_rules.items():
            if (
                rule == "min_length"
                and isinstance(value, (str, list, tuple))
                and len(value) < rule_value
            ):
                return False, f"参数 '{self.name}' 长度必须至少为 {rule_value}"
            elif (
                rule == "max_length"
                and isinstance(value, (str, list, tuple))
                and len(value) > rule_value
            ):
                return False, f"参数 '{self.name}' 长度不能超过 {rule_value}"
            elif (
                rule == "min_value"
                and isinstance(value, (int, float))
                and value < rule_value
            ):
                return False, f"参数 '{self.name}' 必须至少为 {rule_value}"
            elif (
                rule == "max_value"
                and isinstance(value, (int, float))
                and value > rule_value
            ):
                return False, f"参数 '{self.name}' 不能超过 {rule_value}"
            elif rule == "enum" and value not in rule_value:
                return (
                    False,
                    f"参数 '{self.name}' 必须是以下值之一: {', '.join(map(str, rule_value))}",
                )

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "param_type": self.param_type.value,
            "is_required": self.is_required,
            "default_value": self.default_value,
            "validation_rules": self.validation_rules,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parameter":
        """从字典创建"""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            param_type=data.get("param_type", ParameterType.ANY),
            is_required=data.get("is_required", True),
            default_value=data.get("default_value"),
            validation_rules=data.get("validation_rules", {}),
        )


def create_string_param(
    name: str,
    description: str = "",
    required: bool = True,
    default: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    enum: Optional[List[str]] = None,
) -> Parameter:
    """创建字符串参数"""
    validation_rules = {}
    if min_length is not None:
        validation_rules["min_length"] = min_length
    if max_length is not None:
        validation_rules["max_length"] = max_length
    if pattern is not None:
        validation_rules["pattern"] = pattern
    if enum is not None:
        validation_rules["enum"] = enum

    return Parameter(
        name=name,
        description=description,
        param_type=ParameterType.STRING,
        is_required=required,
        default_value=default,
        validation_rules=validation_rules,
    )


def create_integer_param(
    name: str,
    description: str = "",
    required: bool = True,
    default: Optional[int] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    enum: Optional[List[int]] = None,
) -> Parameter:
    """创建整数参数"""
    validation_rules = {}
    if min_value is not None:
        validation_rules["min_value"] = min_value
    if max_value is not None:
        validation_rules["max_value"] = max_value
    if enum is not None:
        validation_rules["enum"] = enum

    return Parameter(
        name=name,
        description=description,
        param_type=ParameterType.INTEGER,
        is_required=required,
        default_value=default,
        validation_rules=validation_rules,
    )


def create_float_param(
    name: str,
    description: str = "",
    required: bool = True,
    default: Optional[float] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
) -> Parameter:
    """创建浮点数参数"""
    validation_rules = {}
    if min_value is not None:
        validation_rules["min_value"] = min_value
    if max_value is not None:
        validation_rules["max_value"] = max_value

    return Parameter(
        name=name,
        description=description,
        param_type=ParameterType.FLOAT,
        is_required=required,
        default_value=default,
        validation_rules=validation_rules,
    )


def create_boolean_param(
    name: str,
    description: str = "",
    required: bool = True,
    default: Optional[bool] = None,
) -> Parameter:
    """创建布尔参数"""
    return Parameter(
        name=name,
        description=description,
        param_type=ParameterType.BOOLEAN,
        is_required=required,
        default_value=default,
    )


def create_array_param(
    name: str,
    description: str = "",
    required: bool = True,
    default: Optional[List] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> Parameter:
    """创建数组参数"""
    validation_rules = {}
    if min_length is not None:
        validation_rules["min_length"] = min_length
    if max_length is not None:
        validation_rules["max_length"] = max_length

    return Parameter(
        name=name,
        description=description,
        param_type=ParameterType.ARRAY,
        is_required=required,
        default_value=default,
        validation_rules=validation_rules,
    )


def create_object_param(
    name: str,
    description: str = "",
    required: bool = True,
    default: Optional[Dict] = None,
) -> Parameter:
    """创建对象参数"""
    return Parameter(
        name=name,
        description=description,
        param_type=ParameterType.OBJECT,
        is_required=required,
        default_value=default,
    )
