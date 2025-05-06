#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""任务框架模块，包含任务执行、批量任务管理与执行等功能"""

# 从本模块导入核心组件
from .task_execution import (
    Task,
    TaskStatus,
    with_retry,
    Result,
)

from .batch_task import (
    BatchStatus,
    BatchTask,
    BatchTaskFailureManager,
    BatchTaskUnfinishedManager,
)

# 从当前目录导入 BatchTaskExecutor
from .batch_task_executor import BatchTaskExecutor

# 导入接口函数
from .interface import (
    execute_task,
    execute_batch_tasks,
    resume_batch_tasks,
    retry_failed_tasks,
    get_failed_tasks,
    get_unfinished_tasks,
)

# 导入任务服务和DataWhale接口函数
from .task_service import (
    TaskService,
    dw_execute_task,
    dw_execute_batch_tasks,
    dw_resume_batch_tasks,
    dw_retry_failed_tasks,
    dw_get_failed_tasks,
    dw_get_unfinished_tasks,
)

__all__ = [
    # 核心组件
    "Task",
    "TaskStatus",
    "with_retry",
    "Result",
    "BatchStatus",
    "BatchTask",
    "BatchTaskExecutor",
    "BatchTaskFailureManager",
    "BatchTaskUnfinishedManager",
    # 接口函数
    "execute_task",
    "execute_batch_tasks",
    "resume_batch_tasks",
    "retry_failed_tasks",
    "get_failed_tasks",
    "get_unfinished_tasks",
    # 任务服务和DataWhale接口函数
    "TaskService",
    "dw_execute_task",
    "dw_execute_batch_tasks",
    "dw_resume_batch_tasks",
    "dw_retry_failed_tasks",
    "dw_get_failed_tasks",
    "dw_get_unfinished_tasks",
]
