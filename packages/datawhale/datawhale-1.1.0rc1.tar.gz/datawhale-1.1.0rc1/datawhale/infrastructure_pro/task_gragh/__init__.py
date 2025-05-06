#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""任务图模块，用于构建和执行有向无环图(DAG)任务
支持使用node装饰器创建节点，以及使用create_graph创建和执行任务图
"""

# 从本模块导入组件
from .graph import Graph, GraphStatus
from .node.node import Node, node
from .node.decision_node import DecisionNode, decision_node
from .node.status import NodeStatus
from .interface import create_graph
from .namespace import NamespaceRegistry

__all__ = [
    "Graph",
    "GraphStatus",
    "Node",
    "node",
    "NodeStatus",
    "DecisionNode",
    "decision_node",
    "create_graph",
    "NamespaceRegistry",
]
