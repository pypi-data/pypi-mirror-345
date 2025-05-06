#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""节点状态模块，定义节点执行状态的常量"""

from typing import Any, Optional


class NodeStatus:
    """节点状态常量"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    SKIPPED = "skipped"  # 跳过执行
