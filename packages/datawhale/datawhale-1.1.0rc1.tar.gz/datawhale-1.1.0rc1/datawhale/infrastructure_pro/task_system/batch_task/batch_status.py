#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum


class BatchStatus(Enum):
    """批次状态枚举

    定义批次任务的各种状态
    """

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消
    PAUSED = "paused"  # 已暂停
    INTERRUPTED = "interrupted"  # 任务被中断
