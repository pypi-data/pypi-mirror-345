#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""字段管理类

负责管理标准字段的配置和动态生成，包括：
1. 读取字段映射配置文件
2. 动态生成StandardFields类的属性
3. 提供字段的添加、删除等管理功能
"""

import os
import json
from typing import Dict, Any, Optional, List, Set
from ...infrastructure_pro.logging import get_system_logger
from .fields import Fields
from collections import OrderedDict

# 获取系统日志记录器
logger = get_system_logger(__name__)


class FieldManager:
    """字段管理类

    负责管理标准字段的配置和动态生成。
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化字段管理器"""
        if self._initialized:
            return

        self._initialized = True
        self._config_path = os.path.join(
            os.path.dirname(__file__),
            "field_mapping.json",
        )
        # 在初始化时加载配置并保存为实例属性
        self._fields = self._load_config()

    @classmethod
    def reset(cls):
        """重置字段管理器实例，用于测试环境"""
        cls._instance = None
        cls._initialized = False

    def _load_config(self) -> Dict[str, Fields]:
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                fields_data = config.get("fields", {})
                fields_dict = OrderedDict()
                for key, data in fields_data.items():
                    try:
                        key = key.upper()
                        # 提取数据源映射
                        data_source_mappings = {}
                        value_map = None
                        for field_key, field_value in data.items():
                            if field_key.startswith("from_"):
                                data_source_mappings[field_key] = field_value
                            elif field_key == "value_map":
                                value_map = field_value

                        field = Fields(
                            key=key,
                            name=str(data["name"]),
                            description=str(data["description"]),
                            field_type=str(data["type"]),
                            add_date=data.get("add_date"),
                            data_source_mappings=data_source_mappings,
                            value_map=value_map,
                        )
                        fields_dict[key] = field
                    except (KeyError, TypeError, ValueError) as e:
                        logger.error(f"字段数据格式错误: {key}, {str(e)}")
                        continue
                return fields_dict
        except Exception as e:
            logger.error(f"加载字段映射配置失败: {str(e)}")
            raise

    def save_config(self, fields: Dict[str, Fields]) -> None:
        """保存字段映射配置"""
        try:
            fields_dict = {}
            for field in fields.values():
                field_data = {
                    "name": field.name,
                    "description": field.description,
                    "type": field.field_type,
                    "add_date": field.add_date,
                }
                # 添加数据源映射
                for src_key, src_value in field.data_source_mappings.items():
                    field_data[src_key] = src_value

                # 添加值映射
                if field.value_map:
                    field_data["value_map"] = field.value_map

                fields_dict[field.key] = field_data
            config = {"fields": dict(fields_dict)}
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存字段映射配置失败: {str(e)}")
            raise

    def add_field(self, field: Fields) -> None:
        field.key = field.key.upper()
        if field.key in self._fields:
            raise ValueError(f"字段已存在: {field.key}")

        # 创建新的OrderedDict并将新字段放在最前面
        new_fields = OrderedDict()
        new_fields[field.key] = field
        new_fields.update(self._fields)
        self._fields = new_fields
        self.save_config(self._fields)

    def remove_field(self, field_key: str) -> None:
        field_key = field_key.upper()
        if field_key not in self._fields:
            raise ValueError(f"字段不存在: {field_key}")

        del self._fields[field_key]
        self.save_config(self._fields)

    def get_field(self, field_key: str) -> Optional[Fields]:
        """获取字段，支持忽略大小写

        Args:
            field_key: 字段键名

        Returns:
            Optional[Fields]: 字段对象，如果不存在则返回None
        """
        field_key = field_key.upper()
        return self._fields.get(field_key)

    def get_all_fields(self) -> List[Fields]:
        """获取所有字段信息

        Returns:
            List[Fields]: 所有字段数据对象
        """
        return list(self._fields.values())

    def update_field(self, field: Fields) -> None:
        field.key = field.key.upper()
        if field.key not in self._fields:
            raise ValueError(f"字段不存在: {field.key}")

        self._fields[field.key] = field
        self.save_config(self._fields)

    def reload(self) -> None:
        """重新加载字段映射配置"""
        try:
            self._fields = self._load_config()
        except Exception as e:
            logger.error(f"重新加载字段映射配置失败: {str(e)}")
            raise

    def get_field_by_source(
        self, source: str, source_field_name: str
    ) -> Optional[Fields]:
        """根据数据源和字段名获取标准字段

        Args:
            source: 数据源名称，如'baostock', 'tushare'等
            source_field_name: 数据源中的字段名称

        Returns:
            Optional[Fields]: 匹配的标准字段对象，如果不存在则返回None
        """
        source_key = f"from_{source}"
        for field in self._fields.values():
            if field.data_source_mappings.get(source_key) == source_field_name:
                return field
        return None

    def set_field_source_mapping(
        self, field_key: str, source: str, source_field_name: str
    ) -> None:
        """设置字段的数据源映射

        Args:
            field_key: 标准字段键名
            source: 数据源名称，如'baostock', 'tushare'等
            source_field_name: 数据源中的字段名称

        Raises:
            ValueError: 字段不存在时抛出异常
        """
        field_key = field_key.upper()
        field = self.get_field(field_key)
        if field is None:
            raise ValueError(f"字段不存在: {field_key}")

        field.set_source_field(source, source_field_name)
        self.update_field(field)

    def remove_field_source_mapping(self, field_key: str, source: str) -> None:
        """移除字段的数据源映射

        Args:
            field_key: 标准字段键名
            source: 数据源名称，如'baostock', 'tushare'等

        Raises:
            ValueError: 字段不存在时抛出异常
        """
        field_key = field_key.upper()
        field = self.get_field(field_key)
        if field is None:
            raise ValueError(f"字段不存在: {field_key}")

        source_key = f"from_{source}"
        if source_key in field.data_source_mappings:
            del field.data_source_mappings[source_key]
            self.update_field(field)

    def get_all_data_sources(self) -> Set[str]:
        """获取所有已配置的数据源

        Returns:
            Set[str]: 所有数据源名称集合
        """
        sources = set()
        for field in self._fields.values():
            for source_key in field.data_source_mappings.keys():
                if source_key.startswith("from_"):
                    sources.add(source_key[5:])  # 去掉"from_"前缀
        return sources
