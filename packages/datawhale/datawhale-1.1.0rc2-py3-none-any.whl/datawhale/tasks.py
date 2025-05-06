#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务系统接口模块

提供任务系统的统一接口
"""

# 从task_system模块导入
from datawhale.infrastructure_pro.task_system import (
    Task,
    TaskStatus,
    with_retry,
    Result,
    BatchStatus,
    BatchTask,
    BatchTaskExecutor,
    BatchTaskFailureManager,
    BatchTaskUnfinishedManager,
    # 接口函数
    execute_task,
    execute_batch_tasks,
    resume_batch_tasks,
    retry_failed_tasks,
    get_failed_tasks,
    get_unfinished_tasks,
    # 任务服务和DataWhale接口函数
    TaskService,
    dw_execute_task,
    dw_execute_batch_tasks,
    dw_resume_batch_tasks,
    dw_retry_failed_tasks,
    dw_get_failed_tasks,
    dw_get_unfinished_tasks,
)

__all__ = [
    # task_system模块
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
