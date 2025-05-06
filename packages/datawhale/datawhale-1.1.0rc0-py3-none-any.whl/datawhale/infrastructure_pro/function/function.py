#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
函数封装模块

提供函数封装功能，包含函数本身、参数定义和元数据
"""

import inspect
import logging
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    Set,
    Tuple,
    Type,
    get_type_hints,
)

from .parameter import Parameter, ParameterType


class Function:
    """
    函数封装类

    封装一个可调用对象，提供参数定义和元数据
    """

    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: str = "",
        parameters: Optional[List[Parameter]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        初始化函数

        Args:
            func: 要封装的函数
            name: 函数名称，默认使用函数的__name__
            description: 函数描述
            parameters: 参数定义列表，如果未提供则从函数签名推断
            metadata: 元数据
            logger: 日志记录器，如果未提供则创建一个新的
        """
        self.func = func
        self.name = name or getattr(func, "__name__", "unknown_function")
        self.description = description
        self._parameters = parameters or self._infer_parameters(func)
        self.metadata = metadata or {}
        self.logger = logger or logging.getLogger(__name__)

    def _infer_parameters(self, func: Callable) -> List[Parameter]:
        """
        从函数签名推断参数定义

        Args:
            func: 要分析的函数

        Returns:
            参数定义列表
        """
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        parameters = []

        for name, param in sig.parameters.items():
            # 跳过self参数
            if name == "self" and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                continue

            # 确定参数类型
            python_type = type_hints.get(name, Any)
            param_type = ParameterType.from_python_type(python_type)

            # 确定是否是必需的
            is_required = param.default == inspect.Parameter.empty
            default_value = None if is_required else param.default

            # 从文档字符串中提取描述
            description = ""
            if func.__doc__:
                for line in func.__doc__.splitlines():
                    line = line.strip()
                    if line.startswith(f"{name}:") or line.startswith(f"{name} :"):
                        description = line.split(":", 1)[1].strip()
                        break

            # 创建参数定义
            parameters.append(
                Parameter(
                    name=name,
                    description=description,
                    param_type=param_type,
                    is_required=is_required,
                    default_value=default_value,
                )
            )

        return parameters

    def get_parameters(self) -> List[Parameter]:
        """获取参数定义列表"""
        return self._parameters

    def get_parameter(self, name: str) -> Optional[Parameter]:
        """
        获取参数定义

        Args:
            name: 参数名

        Returns:
            参数定义，如果未找到则返回None
        """
        for param in self._parameters:
            if param.name == name:
                return param
        return None

    def validate_params(
        self, params: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        验证参数

        Args:
            params: 参数字典

        Returns:
            (是否有效, 错误消息, 验证后的参数)
        """
        validated_params = {}
        errors = []

        # 检查必需参数
        for param in self._parameters:
            if param.name in params:
                value = params[param.name]
                is_valid, error_msg = param.validate(value)
                if not is_valid:
                    errors.append(error_msg)
                else:
                    validated_params[param.name] = value
            elif not param.has_default():
                errors.append(f"缺少必需参数 '{param.name}'")
            else:
                validated_params[param.name] = param.default_value

        # 检查未知参数
        param_names = {param.name for param in self._parameters}
        unknown_params = set(params.keys()) - param_names
        for name in unknown_params:
            self.logger.warning(f"未知参数 '{name}'")

        return len(errors) == 0, "; ".join(errors), validated_params

    def __call__(self, *args, **kwargs) -> Any:
        """
        调用封装的函数

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值
        """
        # 如果只有关键字参数，进行验证
        if not args and kwargs:
            is_valid, error_msg, validated_params = self.validate_params(kwargs)
            if not is_valid:
                raise ValueError(f"参数验证失败: {error_msg}")
            return self.func(**validated_params)

        # 否则直接调用
        return self.func(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [param.to_dict() for param in self._parameters],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], func: Callable) -> "Function":
        """
        从字典创建

        Args:
            data: 函数数据字典
            func: 要封装的函数

        Returns:
            Function对象
        """
        return cls(
            func=func,
            name=data.get("name", func.__name__),
            description=data.get("description", ""),
            parameters=[Parameter.from_dict(p) for p in data.get("parameters", [])],
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_callable(
        cls,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Function":
        """
        从可调用对象创建

        Args:
            func: 要封装的函数
            name: 函数名称
            description: 函数描述

        Returns:
            Function对象
        """
        # 如果函数已经是Function，直接返回
        if isinstance(func, cls):
            if name:
                func.name = name
            if description:
                func.description = description
            return func

        # 否则创建新的Function
        return cls(func=func, name=name, description=description)


def wrap_function(
    func: Callable, name: Optional[str] = None, description: Optional[str] = None
) -> Function:
    """
    包装函数为Function对象

    Args:
        func: 要包装的函数
        name: 函数名称
        description: 函数描述

    Returns:
        Function对象
    """
    return Function.from_callable(func, name, description)
