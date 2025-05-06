#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""抽取数据并保存的通用图结构"""

import pandas as pd
from typing import Dict, List, Any, Tuple, Callable, Optional

# 模块外的从顶层模块导入
from datawhale.graph import Graph, Node

# 模块内的使用相对导入
from ..util_nodes.extract_nodes import (
    extract_return_value,
    extract_cache_path,
    load_cache,
)
from ..util_nodes.split_nodes import (
    extract_df_params,
    extract_df_params_and_group,
    create_node_save_df_to_cache,
)
from datawhale.logging import get_user_logger

# 创建用户日志记录器
user_logger = get_user_logger(__name__)


def create_extract_value_and_save_graph(
    name: str = "extract_value_and_save", cache_dir: str = "./cache"
) -> Graph:
    """创建从命名空间提取值并保存为缓存的任务图

    图的执行流程：
    1. 使用extract_return_value从命名空间提取值
    2. 使用extract_df_params_and_group处理DataFrame
    3. 使用save_df_to_cache保存处理后的DataFrame

    Args:
        name: 图的名称
        cache_dir: 缓存目录路径，默认为"./cache"

    Returns:
        配置好的Graph对象
    """
    # 创建节点和任务图
    graph = Graph(name=name, cache_dir=cache_dir)

    # 创建用于保存DataFrame的节点
    save_df_node = create_node_save_df_to_cache(cache_dir)

    # 使用 >> 运算符设置节点之间的连接关系
    extract_return_value >> extract_df_params_and_group >> save_df_node

    # 创建完整的图结构
    graph.add_node(save_df_node)

    user_logger.info(f"创建了从值提取到保存的任务图: {name}")
    return graph


def create_extract_cache_and_save_graph(
    name: str = "extract_cache_and_save", cache_dir: str = "./cache"
) -> Graph:
    """创建从缓存文件加载并保存为新缓存的任务图

    图的执行流程：
    1. 使用extract_cache_path从命名空间提取缓存路径
    2. 使用load_cache加载缓存数据
    3. 使用extract_df_params_and_group处理DataFrame
    4. 使用save_df_to_cache保存处理后的DataFrame

    Args:
        name: 图的名称
        cache_dir: 缓存目录路径，默认为"./cache"

    Returns:
        配置好的Graph对象
    """
    # 创建节点和任务图
    graph = Graph(name=name, cache_dir=cache_dir)

    # 创建用于保存DataFrame的节点
    save_df_node = create_node_save_df_to_cache(cache_dir)

    # 使用 >> 运算符设置节点之间的连接关系
    extract_cache_path >> load_cache >> extract_df_params_and_group >> save_df_node

    # 创建完整的图结构
    graph.add_node(save_df_node)

    user_logger.info(f"创建了从缓存加载到保存的任务图: {name}")
    return graph
