#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""字段基础定义模块

定义基础的字段类，封装字段的基本属性和方法。
"""

import datetime
from typing import Dict, Optional


class Fields:
    """字段基础类

    定义字段的基本属性和方法，作为系统中所有字段的基类。
    字段设计遵循DDD原则，将字段视为领域对象，而非数据结构。
    """

    def __init__(
        self,
        key: str,
        name: str,
        description: str,
        field_type: str,
        add_date: Optional[str] = None,
        data_source_mappings: Optional[Dict[str, str]] = None,
        value_map: Optional[Dict] = None,
    ):
        """初始化字段

        Args:
            key: 字段键名，唯一标识符
            name: 字段显示名称
            description: 字段描述
            field_type: 字段类型，如string、float、datetime等
            add_date: 添加日期，格式：YYYY-MM-DD，不提供则使用当前日期
            data_source_mappings: 数据源映射字典，key格式为from_{source_name}
            value_map: 字段值映射，用于将原始值映射为标准值，如{'1': True, '0': False}
        """
        self.key = key.upper()  # 字段键名统一使用大写
        self.name = name
        self.description = description
        self.field_type = field_type
        self.add_date = add_date or datetime.datetime.now().strftime("%Y-%m-%d")
        self.data_source_mappings = data_source_mappings or {}
        self.value_map = value_map or {}

    def set_source_field(self, source: str, field_name: str) -> None:
        """设置数据源字段映射

        Args:
            source: 数据源名称
            field_name: 字段在数据源中的名称
        """
        self.data_source_mappings[f"from_{source}"] = field_name
