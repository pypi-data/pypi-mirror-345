#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""字段接口模块

为用户提供简单易用的字段管理接口，封装FieldManager的功能。
提供字段的添加、查询、更新和删除等常用操作。
本模块使用函数式接口，方便用户直接调用。
"""

from typing import Dict, List, Optional, Set
from ...infrastructure_pro.logging import get_system_logger
from .field_manager import FieldManager
from .fields import Fields
import pandas as pd

# 获取系统日志记录器
logger = get_system_logger(__name__)

# 创建全局管理器实例，供所有函数共享
_manager = FieldManager()


def get_field(field_key: str) -> Optional[Fields]:
    """获取指定字段

    Args:
        field_key: 字段键名

    Returns:
        Optional[Fields]: 字段对象，如果不存在则返回None
    """
    # 尝试直接匹配
    field = _manager.get_field(field_key)
    if field is None:
        # 尝试使用大写键名查找
        field = _manager.get_field(field_key.upper())

    if field is None:
        logger.debug(f"查询字段未找到: {field_key}")
    else:
        logger.debug(f"查询字段成功: {field_key}")
    return field


def get_all_fields() -> List[Fields]:
    """获取所有字段

    Returns:
        List[Fields]: 所有字段列表
    """
    fields = _manager.get_all_fields()
    logger.debug(f"获取全部字段，共{len(fields)}个")
    return fields


def add_field(key: str, name: str, description: str, field_type: str) -> Fields:
    """添加新字段

    Args:
        key: 字段键名
        name: 字段名称
        description: 字段描述
        field_type: 字段类型，如'string', 'float', 'boolean'等

    Returns:
        Fields: 添加的字段对象

    Raises:
        ValueError: 当字段已存在时抛出异常
    """
    try:
        field = Fields(
            key=key, name=name, description=description, field_type=field_type
        )
        _manager.add_field(field)
        logger.info(f"添加字段成功: {key}")
        return field
    except ValueError as e:
        logger.error(f"添加字段失败: {key}, 错误: {str(e)}")
        raise


def update_field(
    key: str, name: str = None, description: str = None, field_type: str = None
) -> Fields:
    """更新字段信息

    Args:
        key: 字段键名
        name: 新的字段名称，None表示不更新
        description: 新的字段描述，None表示不更新
        field_type: 新的字段类型，None表示不更新

    Returns:
        Fields: 更新后的字段对象

    Raises:
        ValueError: 当字段不存在时抛出异常
    """
    try:
        field = _manager.get_field(key)
        if field is None:
            logger.error(f"更新字段失败，字段不存在: {key}")
            raise ValueError(f"字段不存在: {key}")

        update_info = []
        if name is not None:
            field.name = name
            update_info.append(f"名称: {name}")
        if description is not None:
            field.description = description
            update_info.append(f"描述: {description}")
        if field_type is not None:
            field.field_type = field_type
            update_info.append(f"类型: {field_type}")

        _manager.update_field(field)
        logger.info(f"更新字段成功: {key}, 更新内容: {', '.join(update_info)}")
        return field
    except ValueError as e:
        logger.error(f"更新字段失败: {key}, 错误: {str(e)}")
        raise


def remove_field(field_key: str) -> None:
    """删除字段

    Args:
        field_key: 字段键名

    Raises:
        ValueError: 当字段不存在时抛出异常
    """
    try:
        _manager.remove_field(field_key)
        logger.info(f"删除字段成功: {field_key}")
    except ValueError as e:
        logger.error(f"删除字段失败: {field_key}, 错误: {str(e)}")
        raise


def set_source_mapping(field_key: str, source: str, source_field_name: str) -> None:
    """设置字段数据源映射

    Args:
        field_key: 字段键名
        source: 数据源名称，如'baostock', 'tushare'等
        source_field_name: 数据源中的字段名称

    Raises:
        ValueError: 当字段不存在时抛出异常
    """
    try:
        _manager.set_field_source_mapping(field_key, source, source_field_name)
        logger.info(
            f"设置字段数据源映射成功: {field_key} -> {source}.{source_field_name}"
        )
    except ValueError as e:
        logger.error(
            f"设置字段数据源映射失败: {field_key} -> {source}.{source_field_name}, 错误: {str(e)}"
        )
        raise


def remove_source_mapping(field_key: str, source: str) -> None:
    """移除字段数据源映射

    Args:
        field_key: 字段键名
        source: 数据源名称，如'baostock', 'tushare'等

    Raises:
        ValueError: 当字段不存在时抛出异常
    """
    try:
        _manager.remove_field_source_mapping(field_key, source)
        logger.info(f"移除字段数据源映射成功: {field_key} -> {source}")
    except ValueError as e:
        logger.error(f"移除字段数据源映射失败: {field_key} -> {source}, 错误: {str(e)}")
        raise


def get_field_by_source(source: str, source_field_name: str) -> Optional[Fields]:
    """根据数据源和数据源字段名查找标准字段

    Args:
        source: 数据源名称，如'baostock', 'tushare'等
        source_field_name: 数据源中的字段名称

    Returns:
        Optional[Fields]: 匹配的标准字段对象，如果不存在则返回None
    """
    field = _manager.get_field_by_source(source, source_field_name)
    if field is None:
        logger.debug(f"根据数据源查询字段未找到: {source}.{source_field_name}")
    else:
        logger.debug(
            f"根据数据源查询字段成功: {source}.{source_field_name} -> {field.key}"
        )
    return field


def get_all_data_sources() -> Set[str]:
    """获取所有已配置的数据源名称

    Returns:
        Set[str]: 所有数据源名称集合
    """
    sources = _manager.get_all_data_sources()
    logger.debug(f"获取全部数据源，共{len(sources)}个")
    return sources


def get_field_source_mapping(field_key: str, source: str) -> Optional[str]:
    """获取字段特定数据源的映射

    Args:
        field_key: 字段键名
        source: 数据源名称，如'baostock', 'tushare'等

    Returns:
        Optional[str]: 该数据源对应的字段名称，如果不存在则返回None

    Raises:
        ValueError: 当字段不存在时抛出异常
    """
    try:
        field = _manager.get_field(field_key)
        if field is None:
            logger.error(f"获取字段数据源映射失败，字段不存在: {field_key}")
            raise ValueError(f"字段不存在: {field_key}")

        source_key = f"from_{source}"
        mapping = field.data_source_mappings.get(source_key)
        logger.debug(f"获取字段数据源映射: {field_key} -> {source} = {mapping}")
        return mapping
    except ValueError as e:
        logger.error(f"获取字段数据源映射失败: {field_key} -> {source}, 错误: {str(e)}")
        raise


def search_fields(keyword: str = None, field_type: str = None) -> List[Fields]:
    """搜索符合条件的字段

    Args:
        keyword: 关键词，会在字段名和描述中搜索
        field_type: 字段类型筛选

    Returns:
        List[Fields]: 匹配的字段列表
    """
    fields = _manager.get_all_fields()

    if keyword is None and field_type is None:
        logger.debug("搜索字段时未指定条件，返回所有字段")
        return fields

    result = []
    for field in fields:
        match = True

        if keyword is not None:
            keyword_lower = keyword.lower()
            if (
                keyword_lower not in field.name.lower()
                and keyword_lower not in field.description.lower()
                and keyword_lower not in field.key.lower()
            ):
                match = False

        if field_type is not None and field.field_type != field_type:
            match = False

        if match:
            result.append(field)

    search_conditions = []
    if keyword:
        search_conditions.append(f"关键词: {keyword}")
    if field_type:
        search_conditions.append(f"类型: {field_type}")

    logger.debug(
        f"搜索字段，条件: {', '.join(search_conditions)}，结果: {len(result)}个"
    )
    return result


def reload() -> None:
    """重新加载字段配置"""
    try:
        _manager.reload()
        logger.info("字段配置重新加载成功")
    except Exception as e:
        logger.error(f"字段配置重新加载失败: {str(e)}")
        raise


def standardize_field(
    field_name: str, source: Optional[str] = None, field_type: Optional[str] = None
) -> str:
    """将数据源的字段名标准化为通用格式

    Args:
        field_name: 原始字段名
        source: 数据源名称，如'baostock', 'tushare'等。默认为None，表示字段名已是标准格式
        field_type: 可选的字段类型，用于提高匹配准确性

    Returns:
        str: 标准化后的字段名
    """
    if source is None:
        # 字段已经是标准格式，直接返回
        return field_name

    # 查找匹配的标准字段
    field = get_field_by_source(source, field_name)
    if field is None:
        # 未找到匹配的标准字段，保持原样返回
        logger.debug(f"未找到字段对应的标准格式，保持原值: {source}.{field_name}")
        return field_name

    logger.debug(f"标准化字段: {source}.{field_name} -> {field.key}")
    return field.name  # 返回name属性（小写）而不是key（大写）


def convert_field(
    field_name: str, target_source: str, field_type: Optional[str] = None
) -> str:
    """将标准字段名转换为特定数据源的字段名

    Args:
        field_name: 标准字段名
        target_source: 目标数据源名称
        field_type: 字段类型，用于消除歧义

    Returns:
        str: 转换后的字段名。如果无法转换，则返回原字段名
    """
    field = get_field(field_name)
    if field is None and field_type is not None:
        # 尝试使用字段类型进行查找
        all_fields = get_all_fields()
        for f in all_fields:
            if f.field_type == field_type and (
                f.key == field_name.upper() or f.name == field_name
            ):
                field = f
                break

    if field:
        mapping_key = f"from_{target_source}"
        if mapping_key in field.data_source_mappings:
            logger.debug(
                f"字段转换成功: {field_name} -> {field.data_source_mappings[mapping_key]}({target_source})"
            )
            return field.data_source_mappings[mapping_key]

    logger.debug(f"字段无法转换，保持原值: {field_name}")
    return field_name


def get_field_type(field_name: str, source: Optional[str] = None) -> Optional[str]:
    """获取字段的类型

    Args:
        field_name: 字段名称，可以是标准字段名或数据源中的字段名
        source: 数据源名称，如果提供，则根据数据源查找对应的标准字段

    Returns:
        Optional[str]: 字段类型，如果字段不存在则返回None
    """
    field = None

    # 如果提供了数据源，尝试从数据源字段映射获取标准字段
    if source:
        field = get_field_by_source(source, field_name)

    # 如果没有提供数据源或通过数据源未找到，直接按标准字段名查找
    if field is None:
        # 尝试直接查找
        field = get_field(field_name)

    # 如果找到了字段，返回其类型
    if field:
        logger.debug(f"获取字段类型成功: {field_name} -> {field.field_type}")
        return field.field_type

    logger.debug(f"获取字段类型失败，字段不存在: {field_name}")
    return None


def get_fields_type(
    field_names: List[str], source: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """获取多个字段的类型

    Args:
        field_names: 字段名称列表，可以是标准字段名或数据源中的字段名
        source: 数据源名称，如果提供，则根据数据源查找对应的标准字段

    Returns:
        Dict[str, Optional[str]]: 字段名到类型的映射字典，如果某字段不存在则其值为None
    """
    result = {}

    for field_name in field_names:
        # 获取标准字段名
        std_field_name = field_name
        if source:
            # 如果提供了数据源，先尝试标准化字段名
            std_field_name = standardize_field(field_name, source)

        # 获取字段类型
        field_type = get_field_type(std_field_name)

        # 将结果添加到字典中
        result[std_field_name] = field_type

    logger.debug(f"批量获取字段类型，共{len(field_names)}个字段")
    return result


def get_field_value_map(
    field_name: str, source: Optional[str] = None
) -> Optional[Dict]:
    """获取字段的值映射

    Args:
        field_name: 字段名称，可以是标准字段名或数据源中的字段名
        source: 数据源名称，如果提供，则根据数据源查找对应的标准字段

    Returns:
        Optional[Dict]: 字段值映射字典，如果字段不存在或无值映射则返回None
    """
    field = None

    # 如果提供了数据源，尝试从数据源字段映射获取标准字段
    if source:
        field = get_field_by_source(source, field_name)

    # 如果没有提供数据源或通过数据源未找到，直接按标准字段名查找
    if field is None:
        field = get_field(field_name)

    # 如果找到了字段，检查是否有值映射
    if field and hasattr(field, "value_map") and field.value_map:
        logger.debug(f"获取字段值映射成功: {field_name}")
        return field.value_map

    logger.debug(f"字段值映射不存在: {field_name}")
    return None


def standardize_fields(
    field_names: List[str],
    source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Dict[str, str]:
    """将多个数据源字段名标准化为通用格式

    Args:
        field_names: 原始字段名列表
        source: 数据源名称，如'baostock', 'tushare'等。默认为None，表示字段名已是标准格式
        field_type: 可选的字段类型，用于提高匹配准确性

    Returns:
        Dict[str, str]: 原始字段名到标准化后字段名的映射字典
    """
    result = {}

    for field_name in field_names:
        # 将字段标准化
        std_field_name = standardize_field(field_name, source, field_type)
        # 添加到结果字典中
        result[field_name] = std_field_name

    logger.debug(
        f"批量标准化字段，共{len(field_names)}个字段，数据源: {source or '无'}"
    )
    return result


def convert_dataframe_types(
    df: pd.DataFrame, special_mappings: Optional[Dict[str, Dict]] = None
) -> pd.DataFrame:
    """根据标准字段定义转换DataFrame的数据类型

    根据字段的标准定义，将DataFrame中的列转换为对应的数据类型。
    支持对特定字段的值映射处理。

    Args:
        df: 原始DataFrame
        special_mappings: 特殊字段的值映射，格式为{字段名: {原始值: 目标值}}
                         例如: {'listing_status': {'1': True, '0': False}}

                         这个参数用于对字段值进行标准化转换，将原始数据中的各种表示形式
                         统一为标准格式。特别适用于将字符串类型的标识符转换为布尔值、
                         枚举值或其他标准格式的情况。

    Returns:
        pd.DataFrame: 类型转换后的DataFrame
    """
    if df.empty:
        return df

    # 获取所有列的标准类型定义
    field_types = {}
    for col in df.columns:
        # 获取字段类型
        field_type = get_field_type(col)
        if field_type:
            field_types[col] = field_type

    # 根据字段类型转换数据类型
    for col, field_type in field_types.items():
        if col not in df.columns:
            continue

        try:
            # 根据字段类型转换列的数据类型
            if field_type in ["int", "integer"]:
                # 处理数值转换，保留NA值
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = df[col].astype("Int64")  # 使用可空整数类型
            elif field_type in ["float", "double"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = df[col].astype("float")
            elif field_type == "boolean":
                # 默认的布尔值映射
                bool_map = {
                    "1": True,
                    "0": False,
                    "true": True,
                    "false": False,
                    "True": True,
                    "False": False,
                }

                # 应用特殊值映射（如果存在）
                if special_mappings and col in special_mappings:
                    bool_map.update(special_mappings[col])

                # 将字符串值转为布尔值，保留NA值
                df[col] = df[col].astype(str).map(bool_map)
                df[col] = df[col].astype("boolean")
            elif field_type == "string":
                # 确保字符串类型
                df[col] = df[col].astype("string")

                # 应用特殊值映射（如果存在）
                if special_mappings and col in special_mappings:
                    value_map = special_mappings[col]
                    df[col] = df[col].map(lambda x: value_map.get(x, x))
        except Exception as e:
            logger.warning(f"转换列 {col} 类型失败: {str(e)}")

    logger.debug(f"数据类型转换完成，共处理{len(field_types)}个字段")
    return df
