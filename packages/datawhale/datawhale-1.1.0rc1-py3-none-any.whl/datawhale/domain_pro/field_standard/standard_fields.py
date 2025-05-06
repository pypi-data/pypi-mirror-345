#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""标准字段定义

定义系统中使用的标准字段常量，作为字段名称的唯一真实来源。
遵循领域驱动设计原则，将字段定义放在领域层。
"""

from typing import List, Dict, Any
from ...infrastructure_pro.logging import get_system_logger
from .fields import Fields
from .field_manager import FieldManager

# 获取系统日志记录器
logger = get_system_logger(__name__)


class _StandardFields:
    """标准字段定义类

    定义了系统中使用的所有标准字段名称，作为常量使用。
    其他模块应该引用这个类中的常量，而不是直接使用字符串。
    """

    def __init__(self):
        self._fields_instance = FieldManager()
        logger.info("标准字段定义类初始化完成")

    def __getattr__(self, name: str) -> Any:
        """获取属性值

        Args:
            name: 属性名称

        Returns:
            Any: 属性值

        Raises:
            AttributeError: 当属性不存在时抛出
        """
        if (
            not hasattr(self._fields_instance, "_fields")
            or self._fields_instance._fields is None
        ):
            logger.error(f"字段管理器未初始化，无法获取字段: {name}")
            raise AttributeError(f"字段不存在: {name}")

        # 尝试直接匹配
        field = self._fields_instance._fields.get(name)
        if field is None:
            # 尝试大写匹配
            field = self._fields_instance._fields.get(name.upper())

        if field is None:
            logger.warning(f"尝试访问不存在的字段: {name}")
            raise AttributeError(f"字段不存在: {name}")

        return field.name


# 创建单例实例
StandardFields = _StandardFields()
