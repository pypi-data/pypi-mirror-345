#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务图接口模块

提供简洁易用的任务图构建和执行接口，支持使用node装饰器创建节点，以及创建和执行任务图。
"""

from typing import Dict, List, Any, Callable, TypeVar, Optional, Set, Tuple, Union
import os
from uuid import uuid4

# 同一模块内的导入使用相对导入
from .graph import Graph, GraphStatus
from .node.node import Node, node
from .node.decision_node import DecisionNode, decision_node
from .node.status import NodeStatus
from .namespace import NamespaceRegistry

# 从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger

# 创建日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")

__all__ = [
    # 类
    "Node",
    "Graph",
    "NodeStatus",
    "GraphStatus",
    # 函数和装饰器
    "node",
    "create_graph",
    "create_decision_path",
    "DecisionNode",
    "decision_node",
]


def create_graph(name: str, nodes: List[Node] = None, cache_dir: str = None) -> Graph:
    """
    创建任务图

    Args:
        name: 图名称
        nodes: 初始节点列表
        cache_dir: 缓存目录路径，用于存储节点执行结果的缓存

    Returns:
        Graph: 创建的图对象

    Examples:
        >>> # 装饰器方式创建节点
        >>> @node
        ... def load_data():
        ...     return [1, 2, 3]
        ...
        >>> @node(inputs={"data": "load_data"})
        ... def process_data(data):
        ...     return [x * 2 for x in data]
        ...
        >>> # 创建和执行图
        >>> graph = create_graph("data_pipeline", [load_data, process_data])
        >>> graph.execute()
        >>> result = graph.get_node_value("process_data")
        >>> print(result)  # [2, 4, 6]
    """
    return Graph(name=name, nodes=nodes, cache_dir=cache_dir)
