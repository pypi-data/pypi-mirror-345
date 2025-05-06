#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提供用于数据提取的通用节点函数
"""

import os
import pickle
import pandas as pd
from typing import Dict, List, Any, Callable, TypeVar, Union, Optional

# 从顶层模块导入
from datawhale.graph import node, NamespaceRegistry
from datawhale.logging import get_user_logger

# 创建用户日志记录器
user_logger = get_user_logger(__name__)


@node(
    name="extract_return_value",
    cache_result=True,
    remove_from_namespace_after_execution=True,
    save_to_namespace=False,
)
def extract_return_value(namespace_registry: NamespaceRegistry, node_name: str) -> Any:
    """从命名空间注册表中提取指定节点的返回值

    Args:
        namespace_registry: 命名空间注册表实例
        node_name: 节点名称

    Returns:
        节点的返回值
    """
    try:
        # 从命名空间注册表中获取指定节点的返回值
        return_value = namespace_registry.get_value(node_name)
        user_logger.info(f"成功从节点 {node_name} 提取返回值")
        return return_value
    except Exception as e:
        user_logger.error(f"从节点 {node_name} 提取返回值失败: {str(e)}")
        raise ValueError(
            f"无法从命名空间注册表中获取节点 {node_name} 的返回值: {str(e)}"
        )


@node(
    name="extract_cache_path",
    cache_result=False,
    remove_from_namespace_after_execution=True,
    save_to_namespace=False,
)
def extract_cache_path(namespace_registry: NamespaceRegistry, node_name: str) -> str:
    """从命名空间注册表中提取指定节点的缓存路径

    Args:
        namespace_registry: 命名空间注册表实例
        node_name: 节点名称

    Returns:
        节点结果的缓存文件路径
    """
    try:
        # 从命名空间注册表中获取指定节点的缓存路径
        cache_path = namespace_registry.get_cache_path(node_name)
        if not cache_path:
            user_logger.warning(f"节点 {node_name} 没有缓存路径")
            return ""

        user_logger.info(f"成功从节点 {node_name} 提取缓存路径: {cache_path}")
        return cache_path
    except Exception as e:
        user_logger.error(f"从节点 {node_name} 提取缓存路径失败: {str(e)}")
        return ""


@node(
    name="load_cache",
    cache_result=True,
    remove_from_namespace_after_execution=True,
    save_to_namespace=False,
    inputs={"cache_path": "extract_cache_path"},
)
def load_cache(cache_path: str) -> Any:
    """从缓存文件加载数据

    Args:
        cache_path: 缓存文件路径，来自extract_cache_path节点

    Returns:
        从缓存文件加载的数据
    """
    if not cache_path:
        user_logger.warning("缓存路径为空，无法加载数据")
        return None

    try:
        if not os.path.exists(cache_path):
            user_logger.error(f"缓存文件不存在: {cache_path}")
            raise FileNotFoundError(f"缓存文件不存在: {cache_path}")

        # 从pickle文件加载数据
        with open(cache_path, "rb") as f:
            data = pickle.load(f)

        user_logger.info(f"成功从缓存文件加载数据: {cache_path}")
        return data
    except Exception as e:
        user_logger.error(f"从缓存文件加载数据失败: {str(e)}")
        raise ValueError(f"无法从缓存文件加载数据: {str(e)}")
