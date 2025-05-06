#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any, Union
import os
import yaml
import datetime
import pandas as pd
from pathlib import Path


class BaseMetaInfo:
    """元数据信息基类

    用于保存和管理数据存储的基本元数据信息，包括：
    - 基本信息（名称、格式、创建/更新时间）
    - 存储配置（层级结构、更新模式等）

    属性:
        name: 数据集名称
        format: 文件格式（csv、parquet等）
        dataset_level: 文件层级数
        structure_fields: 文件结构字段列表
        update_mode: 更新模式（append、overwrite等）
        created_at: 创建时间
        updated_at: 更新时间
    """

    # 元信息字典的关键字常量定义
    KEY_NAME = "name"
    KEY_FORMAT = "format"
    KEY_DATASET = "dataset"
    KEY_LEVEL = "level"
    KEY_STRUCTURE_FIELDS = "structure_fields"
    KEY_UPDATE_MODE = "update_mode"
    KEY_CREATED_AT = "created_at"
    KEY_UPDATED_AT = "updated_at"

    def __init__(
        self,
        name: str,
        format: str = None,
        structure_fields: List[str] = None,
        update_mode: str = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        """初始化元数据基本信息

        Args:
            name: 数据集名称
            format: 文件格式，默认为csv
            structure_fields: 文件结构字段列表，默认为None
            update_mode: 更新模式，默认为append
            created_at: 创建时间，如果为None则使用当前时间
            updated_at: 更新时间，如果为None则使用当前时间
        """
        self.name = name
        if format is None:
            format = "csv"
        self.format = format

        if structure_fields is None:
            structure_fields = []
        self.structure_fields = structure_fields

        # 从structure_fields推断dataset_level
        self.dataset_level = len(structure_fields) + 1

        if update_mode is None:
            update_mode = "append"
        self.update_mode = update_mode

        # 设置时间戳
        current_time = datetime.datetime.now().isoformat()
        self.created_at = created_at or current_time
        self.updated_at = updated_at or current_time

    @staticmethod
    def is_valid_base_dict(meta_dict: Dict[str, Any]) -> bool:
        """验证字典是否包含基本元数据信息所需的字段

        Args:
            meta_dict: 要验证的元数据字典

        Returns:
            bool: 如果字典包含基本元数据信息所需的字段，则返回True，否则返回False
        """
        # 检查必需的顶级键
        if BaseMetaInfo.KEY_NAME not in meta_dict:
            return False

        # dataset字段可以不存在或为None
        dataset_info = meta_dict.get(BaseMetaInfo.KEY_DATASET)

        # 如果dataset存在且不为None，检查它是否为字典
        if dataset_info is not None:
            if not isinstance(dataset_info, dict):
                return False

            # 如果dataset不为空字典，必须有structure_fields字段
            if dataset_info and BaseMetaInfo.KEY_STRUCTURE_FIELDS not in dataset_info:
                return False

        # 所有检查都通过
        return True

    @classmethod
    def from_dict(cls, meta_dict: Dict[str, Any]) -> "BaseMetaInfo":
        """从字典创建元数据信息基础对象

        Args:
            meta_dict: 元数据字典

        Returns:
            BaseMetaInfo: 创建的元数据信息基础对象

        Raises:
            ValueError: 当字典格式无效时抛出
        """
        # 验证字典格式
        if not cls.is_valid_base_dict(meta_dict):
            raise ValueError("无效的元数据基础字典格式")

        # 获取dataset信息
        dataset_info = meta_dict.get(cls.KEY_DATASET, {})

        return cls(
            name=meta_dict.get(cls.KEY_NAME),
            format=meta_dict.get(cls.KEY_FORMAT),
            structure_fields=dataset_info.get(cls.KEY_STRUCTURE_FIELDS),
            update_mode=meta_dict.get(cls.KEY_UPDATE_MODE),
            created_at=meta_dict.get(cls.KEY_CREATED_AT),
            updated_at=meta_dict.get(cls.KEY_UPDATED_AT),
        )

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> "BaseMetaInfo":
        """从YAML文件加载元数据基础信息

        Args:
            yaml_path: YAML文件路径

        Returns:
            BaseMetaInfo: 创建的元数据基础信息对象

        Raises:
            FileNotFoundError: 当YAML文件不存在时抛出
            yaml.YAMLError: 当YAML解析错误时抛出
            ValueError: 当YAML内容格式无效时抛出
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            meta_dict = yaml.safe_load(f)
        return cls.from_dict(meta_dict)

    def to_dict(self) -> Dict[str, Any]:
        """将元数据基础信息转换为字典

        Returns:
            Dict: 元数据基础字典
        """
        return {
            self.KEY_NAME: self.name,
            self.KEY_FORMAT: self.format,
            self.KEY_CREATED_AT: self.created_at,
            self.KEY_UPDATED_AT: self.updated_at,
            self.KEY_DATASET: {
                self.KEY_LEVEL: self.dataset_level,
                self.KEY_STRUCTURE_FIELDS: self.structure_fields,
            },
            self.KEY_UPDATE_MODE: self.update_mode,
        }

    def to_yaml(self, output_dir: Union[str, Path]) -> str:
        """将元数据基础信息保存为YAML文件

        Args:
            output_dir: 输出目录路径

        Returns:
            str: 保存的文件完整路径

        Raises:
            yaml.YAMLError: 当YAML序列化错误时抛出
        """
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 构建文件路径
        yaml_path = os.path.join(output_dir, f"{self.name}.yaml")

        # 更新时间戳
        self.updated_at = datetime.datetime.now().isoformat()

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

        return yaml_path

    def __str__(self) -> str:
        """返回元数据基础信息的字符串表示

        Returns:
            str: 元数据基础信息的字符串表示
        """
        return (
            f"BaseMetaInfo(name={self.name}, format={self.format}, "
            f"level={self.dataset_level}, update_mode={self.update_mode})"
        )
