#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提供用于分割和拆分数据的节点函数集合
"""

import pandas as pd
from typing import Dict, List, Any, Callable, Tuple, Optional
import os
import pickle
import uuid
import json

# 从顶层模块导入
from datawhale.graph import node
from datawhale.logging import get_user_logger

# 创建用户日志记录器
user_logger = get_user_logger(__name__)


@node(
    name="extract_df_params",
    cache_result=True,
    remove_from_namespace_after_execution=True,
    save_to_namespace=False,
)
def extract_df_params(df: pd.DataFrame, param_cols: List[str] = None) -> Dict[str, Any]:
    """从DataFrame中提取参数列的值

    简化版的extract_df_params_and_group，只提取参数不进行分组。
    提取的参数会进行标准化处理，以便于后续比较。

    处理多种情况的组合：
    1. 当df为空或None时，返回包含空params和空DataFrame的字典
    2. 当param_cols为空或None时，返回包含空params和原始df的字典
    3. 当param_cols有效时，从df中提取这些列的值

    Args:
        df: 输入的DataFrame
        param_cols: 需要提取值的参数列名列表（这些列应具有相同值），默认为None

    Returns:
        包含以下键的字典:
        - params: 参数字典，包含param_cols列的值
        - data: 原始DataFrame
    """
    # 初始化默认值
    params = {}
    if param_cols is None:
        param_cols = []

    # 场景1: DataFrame为空或None
    if df is None or df.empty:
        user_logger.warning("输入的DataFrame为空或None")
        return {"params": {}, "data": pd.DataFrame()}

    # 场景2: 参数列为空或None
    if not param_cols:
        user_logger.warning("参数列为空或None")
        return {"params": {}, "data": df}

    # 检查参数列是否存在于DataFrame中
    missing_param_cols = [col for col in param_cols if col not in df.columns]
    if missing_param_cols:
        user_logger.error(f"以下参数列不存在于DataFrame中: {missing_param_cols}")
        raise ValueError(f"参数列不存在: {missing_param_cols}")

    # 提取参数列的值
    for col in param_cols:
        # 检查参数列是否具有相同的值
        if df[col].nunique() > 1:
            user_logger.warning(f"参数列 {col} 包含多个不同的值，将使用第一个值")

        # 获取值并根据类型进行适当处理
        value = df[col].iloc[0]

        params[col] = value

    user_logger.info(f"成功从DataFrame提取了 {len(params)} 个参数")

    # 计算参数的哈希值，以便于后续进行比较
    params_hash = hash(json.dumps(params, sort_keys=True))

    return {"params": params, "data": df, "hash": params_hash}


@node(
    name="extract_df_params_and_group",
    cache_result=True,
    remove_from_namespace_after_execution=True,
    save_to_namespace=False,
)
def extract_df_params_and_group(
    df: pd.DataFrame, param_cols: List[str] = None, group_col: str = None
) -> List[Dict[str, Any]]:
    """从DataFrame中提取参数列的值和按照指定列分组数据

    处理多种情况的组合：
    1. 当df为空或None时，返回包含空params和空DataFrame的单元素列表
    2. 当param_cols为空或None时，返回包含空params和原始df的单元素列表
    3. 当group_col为空或None时，从df中提取param_cols的值，返回包含这些参数和原始df的单元素列表
    4. 当所有参数有效时，按group_col分组并提取param_cols的值，返回多元素列表

    Args:
        df: 输入的DataFrame
        param_cols: 需要提取值的参数列名列表（这些列应具有相同值），默认为None
        group_col: 用于分组的列名，默认为None

    Returns:
        列表，每个元素是包含 params 和 data 两个键的字典：
        - params: 参数字典，包含param_cols列的值和group_col列名及其对应的分组值
        - data: 按group_col分组后的DataFrame子集
    """
    # 初始化默认值
    if param_cols is None:
        param_cols = []

    # 场景1: DataFrame为空或None
    if df is None or df.empty:
        user_logger.warning("输入的DataFrame为空或None")
        return [{"params": {}, "data": pd.DataFrame()}]

    # 场景2: 参数列为空或None
    if not param_cols:
        user_logger.warning("参数列为空或None")
        return [{"params": {}, "data": df}]

    # 检查参数列是否存在于DataFrame中
    missing_param_cols = [col for col in param_cols if col not in df.columns]
    if missing_param_cols:
        user_logger.error(f"以下参数列不存在于DataFrame中: {missing_param_cols}")
        raise ValueError(f"参数列不存在: {missing_param_cols}")

    # 场景3: 分组列为空或None
    if not group_col:
        user_logger.info("分组列为空或None，仅提取参数列的值")
        params = {}
        for col in param_cols:
            # 检查参数列是否具有相同的值
            if df[col].nunique() > 1:
                user_logger.warning(f"参数列 {col} 包含多个不同的值，将使用第一个值")
            params[col] = df[col].iloc[0]

        return [{"params": params, "data": df}]

    # 场景4: 标准情况 - 检查分组列并执行分组
    if group_col not in df.columns:
        user_logger.error(f"分组列 {group_col} 不存在于DataFrame中")
        raise ValueError(f"分组列不存在: {group_col}")

    # 检查参数列的值是否在每个分组内都相同
    for col in param_cols:
        if df.groupby(group_col)[col].nunique().max() > 1:
            user_logger.warning(
                f"参数列 {col} 在某些分组内包含不同的值，将使用每个分组的第一个值"
            )

    # 创建结果列表
    result = []

    # 进行分组
    grouped = df.groupby(group_col)
    group_names = list(grouped.groups.keys())

    # 如果分组为空，返回空参数和原始DataFrame
    if not group_names:
        user_logger.warning(f"根据分组列 {group_col} 未找到任何分组")
        return [{"params": {}, "data": df}]

    # 处理每个分组
    for group_name in group_names:
        group_data = grouped.get_group(group_name)

        # 提取参数列的值
        params = {}
        for col in param_cols:
            params[col] = group_data[col].iloc[0]

        # 添加分组信息
        params[group_col] = group_name

        # 添加结果
        result.append({"params": params, "data": group_data})

        user_logger.debug(f"创建了分组 {group_name}，参数: {params}")

    user_logger.info(f"成功从DataFrame创建了 {len(result)} 个分组")
    return result


def create_node_save_df_to_cache(
    cache_dir: str, node_name: str = "save_df_to_cache"
) -> Callable:
    """创建一个保存DataFrame到指定缓存目录的节点函数

    Args:
        cache_dir: 缓存目录路径

    Returns:
        一个预配置了缓存目录的节点函数
    """
    user_logger.info(f"创建使用缓存目录 {cache_dir} 的save_df_to_cache节点")

    # 创建保存函数
    @node(
        name=node_name,
        cache_result=True,
        remove_from_namespace_after_execution=False,
        save_to_namespace=True,
        default_params={"cache_dir": cache_dir},
    )
    def save_df_to_cache(
        result: List[Dict[str, Any]], cache_dir: str
    ) -> List[Dict[str, Any]]:
        """将分组结果中的DataFrame保存到缓存目录，并将路径替换原始数据

        接收extract_df_params_and_group函数的返回结果，将每个结果中的DataFrame保存为pickle文件，
        然后将data的值替换为文件路径。

        Args:
            result: extract_df_params_and_group函数的返回结果，包含params和data的字典列表
            cache_dir: 缓存文件夹路径

        Returns:
            修改后的result列表，data字段已被替换为文件路径
        """
        # 验证输入
        if not result:
            user_logger.warning("输入的结果列表为空")
            return []

        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        user_logger.debug(f"确保缓存目录存在: {cache_dir}")

        # 处理每个结果项
        for i, item in enumerate(result):
            # 跳过无效项
            if not isinstance(item, dict) or "data" not in item or "params" not in item:
                user_logger.warning(f"跳过无效的结果项 #{i}: 缺少必要的键")
                continue

            # 获取DataFrame
            df = item["data"]

            # 跳过非DataFrame项
            if not isinstance(df, pd.DataFrame):
                user_logger.warning(f"跳过结果项 #{i}: data不是DataFrame")
                continue

            # 创建唯一文件名
            unique_id = str(uuid.uuid4())[:8]

            # 从params中获取有用的标识信息
            identifiers = []
            for key, value in item["params"].items():
                # 尝试将值转换为字符串并用于文件名
                try:
                    # 避免文件名太长，只取值的前几个字符
                    str_value = str(value)
                    if len(str_value) > 10:
                        str_value = str_value[:10]

                    # 去除非法字符
                    str_value = "".join(
                        c for c in str_value if c.isalnum() or c in "_-"
                    )

                    if str_value:
                        identifiers.append(f"{key}_{str_value}")
                except:
                    pass

            # 如果没有有效标识符，只使用索引和随机ID
            if not identifiers:
                filename = f"data_{i}_{unique_id}.pkl"
            else:
                # 使用最多前两个标识符和随机ID
                prefix = "_".join(identifiers[:2])
                filename = f"{prefix}_{unique_id}.pkl"

            # 完整的文件路径
            filepath = os.path.join(cache_dir, filename)

            # 保存DataFrame
            try:
                with open(filepath, "wb") as f:
                    pickle.dump(df, f)

                # 替换data为文件路径
                item["data"] = filepath
                user_logger.debug(f"DataFrame已保存到: {filepath}")

            except Exception as e:
                user_logger.error(f"保存DataFrame到 {filepath} 失败: {str(e)}")
                # 继续处理下一项，但保留原始DataFrame

        user_logger.info(
            f"已将 {len(result)} 个结果项中的DataFrame保存到缓存目录: {cache_dir}"
        )
        return result

    return save_df_to_cache
