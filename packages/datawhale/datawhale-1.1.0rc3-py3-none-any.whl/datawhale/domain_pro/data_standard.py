#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据标准化模块

提供用于标准化DataFrame的通用函数，包括字段标准化、代码标准化、日期标准化和数据类型转换
"""

import pandas as pd
from typing import List, Dict, Optional, Union, Any

from datawhale.domain_pro.field_standard import (
    standardize_fields,
    get_field_value_map,
    get_fields_type,
    StandardFields,
)
from datawhale.domain_pro.code_standard import standardize_code
from datawhale.domain_pro.datetime_standard import to_standard_date

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)


def standardize_dataframe(
    df: pd.DataFrame,
    source: str,
    code_field: str,
    date_fields: Optional[List[str]] = None,
    required_columns: Optional[List[str]] = None,
    value_mapping_fields: Optional[List[str]] = None,
    sort_by: Optional[Union[str, List[str]]] = None,
    ascending: Union[bool, List[bool]] = True,
) -> pd.DataFrame:
    """
    对DataFrame进行标准化处理，包括字段名标准化、代码标准化、日期标准化和数据类型转换

    Args:
        df: 需要标准化的DataFrame
        source: 数据源名称，如"baostock"、"tushare"等
        code_field: 证券代码字段名，必须提供以进行证券代码标准化
        date_fields: 日期字段列表，会对这些字段进行日期标准化
        required_columns: 需要保留的标准字段列表，如果不为None则会筛选这些字段
        value_mapping_fields: 需要进行值映射的字段列表
        sort_by: 排序字段名称或字段列表（使用标准化后的字段名），如果为None则不排序
        ascending: 排序方向，True为升序，False为降序，默认为升序；也可以是布尔值列表，
                  指定每个排序字段的排序方向，列表长度必须与sort_by列表长度一致

    Returns:
        pd.DataFrame: 标准化后的DataFrame
    """
    if df.empty:
        return df

    # 校验code_field是否存在
    if code_field not in df.columns:
        logger.warning(f"证券代码字段 '{code_field}' 不存在于DataFrame中")
        return df

    # 第1步: 使用field_standard模块对列名进行标准化
    field_mapping = standardize_fields(list(df.columns), source=source)
    renamed_columns = {
        col: std_name for col, std_name in field_mapping.items() if std_name != col
    }

    # 应用列名重命名
    if renamed_columns:
        df.rename(columns=renamed_columns, inplace=True)
        logger.debug(f"标准化字段名完成，共重命名{len(renamed_columns)}个字段")

    # 第2步: 处理证券代码标准化（现在是必需的）
    std_code_field = field_mapping.get(code_field, code_field)
    df[std_code_field] = df[std_code_field].apply(
        lambda x: standardize_code(x, source=source) if pd.notna(x) else x
    )
    logger.debug(f"标准化证券代码字段完成: {std_code_field}")

    # 第3步: 如果指定了日期字段，处理日期标准化
    if date_fields:
        for date_col in date_fields:
            std_date_field = field_mapping.get(date_col, date_col)
            if std_date_field in df.columns:
                df[std_date_field] = df[std_date_field].apply(
                    lambda x: to_standard_date(x) if pd.notna(x) and x != "" else x
                )
                logger.debug(f"标准化日期字段完成: {std_date_field}")

    # 第4步: 处理数据类型转换
    # 创建字段值映射字典
    standard_value_mappings = {}
    if value_mapping_fields:
        for field in value_mapping_fields:
            field_value_map = get_field_value_map(field)
            if field_value_map:
                standard_value_mappings[field] = field_value_map

    # 获取所有字段的数据类型
    field_types = get_fields_type(list(df.columns))

    # 应用数据类型转换
    for col, dtype in field_types.items():
        if col in df.columns:
            try:
                # 如果字段有值映射，先应用值映射
                if col in standard_value_mappings:
                    value_map = standard_value_mappings[col]
                    df[col] = df[col].apply(
                        lambda x: value_map.get(str(x), x) if pd.notna(x) else x
                    )

                # 应用数据类型转换
                if dtype == "int" or dtype == "integer":
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                    )
                elif dtype == "float":
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif dtype == "string" or dtype == "str":
                    df[col] = df[col].astype(str)
                # 其他数据类型保持不变
            except Exception as e:
                logger.warning(f"字段{col}类型转换失败: {str(e)}")

    logger.debug(f"数据类型转换完成，共处理{len(field_types)}个字段")

    # 第5步: 如果指定了required_columns，筛选所需的列
    if required_columns:
        # 确保证券代码字段被包含（如果不在required_columns中）
        std_code_name = StandardFields.CODE  # 标准证券代码字段名
        if std_code_name not in required_columns:
            required_columns = [std_code_name] + required_columns

        existing_columns = [col for col in required_columns if col in df.columns]
        if existing_columns:
            df = df[existing_columns]
            logger.debug(f"筛选字段完成，保留{len(existing_columns)}个字段")

    # 第6步: 如果指定了排序字段，对DataFrame进行排序
    if sort_by is not None:
        # 将排序字段转换为列表
        if isinstance(sort_by, str):
            sort_fields = [sort_by]
        else:
            sort_fields = sort_by

        # 检查排序字段是否存在于DataFrame中
        std_sort_fields = []
        for field in sort_fields:
            if field in df.columns:
                std_sort_fields.append(field)
            else:
                logger.warning(f"排序字段'{field}'不存在于DataFrame中")

        # 对存在的字段进行排序
        if std_sort_fields:
            df = df.sort_values(by=std_sort_fields, ascending=ascending)
            logger.debug(
                f"数据排序完成，按字段{std_sort_fields}{'升序' if ascending else '降序'}排序"
            )
        else:
            logger.warning(
                f"所有指定的排序字段{sort_fields}不存在于DataFrame中，跳过排序"
            )

    return df
