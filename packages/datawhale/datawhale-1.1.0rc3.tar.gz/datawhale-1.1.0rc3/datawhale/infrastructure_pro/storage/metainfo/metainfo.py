#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any, Union
import os
import yaml
import datetime
import pandas as pd
from pathlib import Path

# 模块内的导入使用相对导入
from .base_metainfo import BaseMetaInfo


class MetaInfo(BaseMetaInfo):
    """元数据信息类

    用于保存和管理数据存储的元数据信息，扩展了BaseMetaInfo类，额外包括：
    - 数据类型定义

    属性:
        name: 数据集名称
        format: 文件格式（csv、parquet等）
        dtypes: 数据字段类型映射
        dataset_level: 文件层级数
        structure_fields: 文件结构字段列表
        update_mode: 更新模式（append、overwrite等）
        created_at: 创建时间
        updated_at: 更新时间
    """

    # 扩展元信息字典的关键字常量定义
    KEY_DTYPES = "dtypes"

    def __init__(
        self,
        name: str,
        dtypes: Dict[str, str],
        format: str = None,
        structure_fields: List[str] = None,
        update_mode: str = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        """初始化元数据信息

        Args:
            name: 数据集名称
            dtypes: 数据字段类型映射
            format: 文件格式，默认为csv
            structure_fields: 文件结构字段列表，默认为None
            update_mode: 更新模式，默认为append
            created_at: 创建时间，如果为None则使用当前时间
            updated_at: 更新时间，如果为None则使用当前时间
        """
        # 调用父类初始化方法
        super().__init__(
            name=name,
            format=format,
            structure_fields=structure_fields,
            update_mode=update_mode,
            created_at=created_at,
            updated_at=updated_at,
        )

        # 设置MetaInfo特有的属性
        if dtypes is None:
            dtypes = {}
        self.dtypes = dtypes

    @staticmethod
    def is_valid_dict(meta_dict: Dict[str, Any]) -> bool:
        """验证字典是否可以作为元数据信息使用

        Args:
            meta_dict: 要验证的元数据字典

        Returns:
            bool: 如果字典可以用作元数据信息，则返回True，否则返回False
        """
        # 首先检查基本元数据信息
        if not BaseMetaInfo.is_valid_base_dict(meta_dict):
            return False

        # 检查dtypes是否存在、是字典且长度大于0
        if MetaInfo.KEY_DTYPES not in meta_dict:
            return False

        dtypes = meta_dict.get(MetaInfo.KEY_DTYPES)
        if not isinstance(dtypes, dict):
            return False

        if len(dtypes) < 1:
            return False

        # 所有检查都通过
        return True

    @classmethod
    def from_dict(cls, meta_dict: Dict[str, Any]) -> "MetaInfo":
        """从字典创建元数据信息对象

        Args:
            meta_dict: 元数据字典

        Returns:
            MetaInfo: 创建的元数据信息对象

        Raises:
            ValueError: 当字典格式无效时抛出
        """
        # 验证字典格式
        if not cls.is_valid_dict(meta_dict):
            raise ValueError("无效的元数据字典格式")

        # 获取dataset信息
        dataset_info = meta_dict.get(cls.KEY_DATASET, {})

        return cls(
            name=meta_dict.get(cls.KEY_NAME),
            format=meta_dict.get(cls.KEY_FORMAT),
            dtypes=meta_dict.get(cls.KEY_DTYPES),
            structure_fields=dataset_info.get(cls.KEY_STRUCTURE_FIELDS),
            update_mode=meta_dict.get(cls.KEY_UPDATE_MODE),
            created_at=meta_dict.get(cls.KEY_CREATED_AT),
            updated_at=meta_dict.get(cls.KEY_UPDATED_AT),
        )

    def to_dict(self) -> Dict[str, Any]:
        """将元数据信息转换为字典

        Returns:
            Dict: 元数据字典
        """
        # 获取基本元数据字典
        base_dict = super().to_dict()

        # 添加MetaInfo特有的属性
        base_dict[self.KEY_DTYPES] = self.dtypes

        return base_dict

    @classmethod
    def infer_dtypes_from_data(cls, data: pd.DataFrame) -> Dict[str, str]:
        """根据数据自动推断字段类型

        分析DataFrame的每一列，根据实际数据自动推断适合的数据类型。
        支持的类型映射:
        - 整数类型 -> 'int64'
        - 浮点类型 -> 'float64'
        - 字符串/对象类型 -> 'string'
        - 布尔类型 -> 'bool'
        - 日期时间类型 -> 'datetime64'

        Args:
            data: 待分析的数据框

        Returns:
            字段名到类型字符串的映射字典
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("输入数据必须是pandas DataFrame")

        if data.empty:
            return {}

        dtypes = {}

        for column in data.columns:
            # 获取列的pandas数据类型
            col_type = data[column].dtype

            # 根据数据类型进行映射
            if pd.api.types.is_integer_dtype(col_type):
                dtype_str = "int64"
            elif pd.api.types.is_float_dtype(col_type):
                dtype_str = "float64"
            elif pd.api.types.is_bool_dtype(col_type):
                dtype_str = "bool"
            elif pd.api.types.is_datetime64_dtype(col_type):
                dtype_str = "datetime64"
            else:
                # 默认为字符串类型
                dtype_str = "string"

            dtypes[column] = dtype_str

        return dtypes

    def __str__(self) -> str:
        """返回元数据信息的字符串表示

        Returns:
            str: 元数据信息的字符串表示
        """
        return (
            f"MetaInfo(name={self.name}, format={self.format}, "
            f"level={self.dataset_level}, dtypes={self.dtypes}, update_mode={self.update_mode})"
        )
