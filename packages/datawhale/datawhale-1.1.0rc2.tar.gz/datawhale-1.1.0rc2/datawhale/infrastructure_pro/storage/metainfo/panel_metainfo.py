#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any, Union
import os
import yaml
import datetime
import pandas as pd
from pathlib import Path
from .base_metainfo import BaseMetaInfo


class PanelMetaInfo(BaseMetaInfo):
    """面板数据元数据信息类

    用于保存和管理面板数据的元数据信息，扩展了BaseMetaInfo类，额外包括：
    - 索引列名称（通常是日期列）
    - 实体列名称（通常是存储实体ID的列名）
    - 值数据类型（面板数据值的数据类型）

    属性:
        name: 数据集名称
        format: 文件格式（csv、parquet等）
        dataset_level: 文件层级数
        structure_fields: 文件结构字段列表
        update_mode: 更新模式（append、overwrite等）
        created_at: 创建时间
        updated_at: 更新时间
        index_col: 索引列名称（日期列）
        entity_col_name: 实体列名称（实体ID列名）
        value_dtype: 值数据类型（数据的类型，如"float64"）
    """

    # 面板数据特有元信息关键字常量
    KEY_INDEX_COL = "index_col"
    KEY_ENTITY_COL_NAME = "entity_col_name"
    KEY_VALUE_DTYPE = "value_dtype"

    def __init__(
        self,
        name: str,
        index_col: str,
        value_dtype: str,
        entity_col_name: str = "entity_id",  # 默认改为entity_id而不是stock_code，更通用
        format: str = None,
        structure_fields: List[str] = None,
        update_mode: str = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        """初始化面板数据元数据信息

        Args:
            name: 数据集名称
            index_col: 索引列名称（日期列）
            value_dtype: 值数据类型（如"float64"）
            entity_col_name: 实体列名称（实体ID列名），默认为'entity_id'
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

        # 设置面板数据特有的属性
        self.index_col = index_col
        self.entity_col_name = entity_col_name
        self.value_dtype = value_dtype

        # 创建dtypes属性，只包含索引列，不包含实体列
        self.dtypes = {index_col: "string"}

    @staticmethod
    def is_valid_dict(meta_dict: Dict[str, Any]) -> bool:
        """验证字典是否可以作为面板数据元数据信息使用

        Args:
            meta_dict: 要验证的元数据字典

        Returns:
            bool: 如果字典可以用作面板数据元数据信息，则返回True，否则返回False
        """
        # 首先检查基本元数据信息
        if not BaseMetaInfo.is_valid_base_dict(meta_dict):
            return False

        # 检查面板数据特有的必需属性
        if PanelMetaInfo.KEY_INDEX_COL not in meta_dict:
            return False

        if PanelMetaInfo.KEY_VALUE_DTYPE not in meta_dict:
            return False

        # 所有检查都通过
        return True

    @classmethod
    def from_dict(cls, meta_dict: Dict[str, Any]) -> "PanelMetaInfo":
        """从字典创建面板数据元数据信息对象

        Args:
            meta_dict: 元数据字典

        Returns:
            PanelMetaInfo: 创建的面板数据元数据信息对象

        Raises:
            ValueError: 当字典格式无效时抛出
        """
        # 验证字典格式
        if not cls.is_valid_dict(meta_dict):
            raise ValueError("无效的面板数据元数据字典格式")

        # 获取dataset信息
        dataset_info = meta_dict.get(cls.KEY_DATASET, {})

        # 支持旧版的entity_col字段和新版的entity_col_name字段
        entity_col_name = meta_dict.get(cls.KEY_ENTITY_COL_NAME)
        if entity_col_name is None:
            entity_col_name = meta_dict.get("entity_col", "entity_id")

        return cls(
            name=meta_dict.get(cls.KEY_NAME),
            index_col=meta_dict.get(cls.KEY_INDEX_COL),
            entity_col_name=entity_col_name,  # 默认更通用的entity_id
            value_dtype=meta_dict.get(cls.KEY_VALUE_DTYPE),
            format=meta_dict.get(cls.KEY_FORMAT),
            structure_fields=dataset_info.get(cls.KEY_STRUCTURE_FIELDS),
            update_mode=meta_dict.get(cls.KEY_UPDATE_MODE),
            created_at=meta_dict.get(cls.KEY_CREATED_AT),
            updated_at=meta_dict.get(cls.KEY_UPDATED_AT),
        )

    def to_dict(self) -> Dict[str, Any]:
        """将面板数据元数据信息转换为字典

        Returns:
            Dict: 面板数据元数据字典
        """
        # 获取基本元数据字典
        base_dict = super().to_dict()

        # 添加面板数据特有的属性
        base_dict[self.KEY_INDEX_COL] = self.index_col
        base_dict[self.KEY_ENTITY_COL_NAME] = self.entity_col_name
        base_dict[self.KEY_VALUE_DTYPE] = self.value_dtype

        return base_dict

    @classmethod
    def infer_value_dtype_from_data(
        cls, data: pd.DataFrame, index_col: str, entity_col_name: str = "entity_id"
    ) -> str:
        """根据数据自动推断值数据类型

        根据DataFrame的内容，推断值的数据类型。

        Args:
            data: 待分析的数据框
            index_col: 索引列名称（日期列）
            entity_col_name: 实体列名称（实体ID列名），默认为'entity_id'

        Returns:
            值数据类型的字符串表示
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("输入数据必须是pandas DataFrame")

        if data.empty:
            return "float64"  # 默认返回float64

        if index_col not in data.columns:
            raise ValueError(f"指定的索引列 {index_col} 不在数据列中")

        # 首先判断是宽格式还是长格式
        if entity_col_name in data.columns:
            # 长格式：有entity_col_name列
            # 尝试找出值列，排除索引列和实体列
            value_cols = [
                col
                for col in data.columns
                if col != index_col and col != entity_col_name
            ]
            if value_cols:
                # 获取第一个值列的数据类型
                sample_col = value_cols[0]
                col_type = data[sample_col].dtype

                # 根据数据类型进行映射
                if pd.api.types.is_integer_dtype(col_type):
                    return "int64"
                elif pd.api.types.is_float_dtype(col_type):
                    return "float64"
                elif pd.api.types.is_bool_dtype(col_type):
                    return "bool"
                else:
                    # 默认为浮点类型，因为面板数据通常是数值类型
                    return "float64"
        else:
            # 宽格式：将所有非索引列视为实体列，它们共享相同的数据类型
            entity_cols = [col for col in data.columns if col != index_col]
            if entity_cols:
                # 获取第一个实体列的类型作为示例
                sample_col = entity_cols[0]
                col_type = data[sample_col].dtype

                # 根据数据类型进行映射
                if pd.api.types.is_integer_dtype(col_type):
                    return "int64"
                elif pd.api.types.is_float_dtype(col_type):
                    return "float64"
                elif pd.api.types.is_bool_dtype(col_type):
                    return "bool"
                # 其他类型保持默认的float64

        # 如果没有找到值列，返回默认值类型
        return "float64"

    def __str__(self) -> str:
        """返回面板数据元数据信息的字符串表示

        Returns:
            str: 面板数据元数据信息的字符串表示
        """
        return (
            f"PanelMetaInfo(name={self.name}, format={self.format}, "
            f"level={self.dataset_level}, index_col={self.index_col}, "
            f"entity_col_name={self.entity_col_name}, value_dtype={self.value_dtype})"
        )
