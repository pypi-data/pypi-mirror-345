#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务图接口模块

提供任务图和任务阶段的统一接口
"""

# 从task_gragh模块导入
from datawhale.infrastructure_pro.task_gragh import (
    Node,
    Graph,
    NodeStatus,
    GraphStatus,
    node,
    create_graph,
    NamespaceRegistry,
)

# 从task_stage模块导入
from datawhale.infrastructure_pro.task_stage import Stage, StageStatus

__all__ = [
    # task_gragh模块
    "Node",
    "Graph",
    "NodeStatus",
    "GraphStatus",
    "node",
    "create_graph",
    "NamespaceRegistry",
    # task_stage模块
    "Stage",
    "StageStatus",
]
