#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""任务框架接口模块，提供简便的任务执行和管理功能"""

from typing import Dict, List, Any, Callable, TypeVar, Optional, Literal
import time

# 同模块内的导入使用相对导入
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

# 从当前模块导入BatchTaskExecutor
from .batch_task_executor import BatchTaskExecutor

# 跨模块的导入优先从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger

# 创建用户日志和系统日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")
# 定义执行模式类型
ExecutionMode = Literal["thread", "process"]


def execute_task(
    task_func: Callable[..., T],
    task_params: Dict[str, Any] = None,
    task_id: str = None,
    task_type: str = "default",
    max_retries: int = None,
    retry_interval: float = None,
    backoff_factor: float = None,
) -> Result[T]:
    """执行单个任务

    Args:
        task_func: 任务执行函数
        task_params: 任务参数
        task_id: 任务ID，默认自动生成
        task_type: 任务类型
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子

    Returns:
        Result[T]: 任务执行结果
    """
    # 记录任务开始
    system_logger.info(f"开始执行单个任务：task_type={task_type}, task_id={task_id}")

    task = Task(
        task_type=task_type,
        params=task_params or {},
        task_func=task_func,
        task_id=task_id,
        max_retries=max_retries,
        retry_interval=retry_interval,
        backoff_factor=backoff_factor,
    )

    result = task.execute()

    # 记录任务结果
    if result.success:
        system_logger.info(f"任务执行成功：task_id={task.task_id}")
    else:
        system_logger.error(
            f"任务执行失败：task_id={task.task_id}, error={result.error}"
        )
        user_logger.error(f"任务执行失败：{result.error}")

    return result


def execute_batch_tasks(
    task_func: Callable[..., T],
    task_params_list: List[Dict[str, Any]],
    batch_id: str = None,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    record_failed: bool = True,
    batch_mode: str = "new",
    failed_task_storage_dir: str = None,
    unfinished_task_storage_dir: str = None,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> BatchTask:
    """执行批量任务

    Args:
        task_func: 任务执行函数
        task_params_list: 任务参数列表
        batch_id: 批次ID，默认自动生成
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        record_failed: 是否记录失败任务
        batch_mode: 批次模式，可选值为"new"、"resume"和"retry"
        failed_task_storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录
        unfinished_task_storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        BatchTask: 批次任务对象
    """
    # 参数验证
    if batch_mode not in ["new", "resume", "retry"]:
        raise ValueError(
            f"不支持的批次模式: {batch_mode}，可选值为'new'、'resume'和'retry'"
        )

    if batch_mode in ["resume", "retry"] and batch_id is None:
        raise ValueError(f"在{batch_mode}模式下必须提供batch_id")

    if batch_mode == "new" and not task_params_list and batch_id is None:
        raise ValueError(
            "在创建新批次模式下，如果没有提供batch_id，则必须提供任务参数列表"
        )

    # 记录批量任务开始
    task_count = len(task_params_list) if task_params_list else "未知"
    system_logger.info(
        f"准备执行批量任务：batch_mode={batch_mode}, task_type={task_type}, "
        f"任务数量={task_count}, batch_id={batch_id}, execution_mode={execution_mode}"
    )
    user_logger.info(
        f"准备执行{task_count}个任务，模式：{batch_mode}，执行方式：{execution_mode}"
    )

    executor = BatchTaskExecutor(
        task_type=task_type,
        max_workers=max_workers,
        task_interval=task_interval,
        task_timeout=task_timeout,
        record_failed=record_failed,
        max_retries=task_max_retries,
        retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        failed_task_storage_dir=failed_task_storage_dir,
        unfinished_task_storage_dir=unfinished_task_storage_dir,
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )

    return executor.execute_batch_tasks(
        task_func=task_func,
        task_params_list=task_params_list,
        batch_id=batch_id,
        task_timeout=task_timeout,
        task_interval=task_interval,
        max_workers=max_workers,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        batch_mode=batch_mode,
        execution_mode=execution_mode,
        show_progress=show_progress,
    )


def resume_batch_tasks(
    task_func: Callable[..., T],
    batch_id: str,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    failed_task_storage_dir: str = None,
    unfinished_task_storage_dir: str = None,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> BatchTask:
    """恢复批量任务

    Args:
        task_func: 任务执行函数
        batch_id: 批次ID
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        failed_task_storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录
        unfinished_task_storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        BatchTask: 批次任务对象
    """
    # 记录恢复任务
    system_logger.info(
        f"恢复批量任务：batch_id={batch_id}, task_type={task_type}, execution_mode={execution_mode}"
    )
    user_logger.info(f"正在恢复批次任务：{batch_id}，执行方式：{execution_mode}")

    return execute_batch_tasks(
        task_func=task_func,
        task_params_list=[],  # 恢复模式不需要提供参数列表
        batch_id=batch_id,
        task_type=task_type,
        max_workers=max_workers,
        task_timeout=task_timeout,
        task_interval=task_interval,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        batch_mode="resume",
        failed_task_storage_dir=failed_task_storage_dir,
        unfinished_task_storage_dir=unfinished_task_storage_dir,
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )


def retry_failed_tasks(
    task_func: Callable[..., T],
    batch_id: str,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    failed_task_storage_dir: str = None,
    unfinished_task_storage_dir: str = None,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> BatchTask:
    """重试失败的批量任务

    Args:
        task_func: 任务执行函数
        batch_id: 批次ID
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        failed_task_storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录
        unfinished_task_storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        BatchTask: 批次任务对象
    """
    # 记录重试任务
    system_logger.info(
        f"重试失败任务：batch_id={batch_id}, task_type={task_type}, execution_mode={execution_mode}"
    )
    user_logger.info(f"正在重试失败任务：{batch_id}，执行方式：{execution_mode}")

    return execute_batch_tasks(
        task_func=task_func,
        task_params_list=[],  # 重试模式不需要提供参数列表
        batch_id=batch_id,
        task_type=task_type,
        max_workers=max_workers,
        task_timeout=task_timeout,
        task_interval=task_interval,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        batch_mode="retry",
        failed_task_storage_dir=failed_task_storage_dir,
        unfinished_task_storage_dir=unfinished_task_storage_dir,
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )


def get_failed_tasks(
    batch_id: str,
    task_type: str = "default",
    storage_dir: str = None,
) -> List[Dict[str, Any]]:
    """获取失败任务列表

    Args:
        batch_id: 批次ID
        task_type: 任务类型
        storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录

    Returns:
        List[Dict[str, Any]]: 失败任务列表
    """
    system_logger.info(f"获取失败任务列表：batch_id={batch_id}, task_type={task_type}")

    manager = BatchTaskFailureManager(task_type, storage_dir=storage_dir)
    manager.load_batch_tasks(batch_id)
    tasks = manager.get_failed_tasks(batch_id)

    system_logger.info(f"找到{len(tasks)}个失败任务：batch_id={batch_id}")
    return tasks


def get_unfinished_tasks(
    batch_id: str,
    task_type: str = "default",
    storage_dir: str = None,
) -> List[Dict[str, Any]]:
    """获取未完成任务列表

    Args:
        batch_id: 批次ID
        task_type: 任务类型
        storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录

    Returns:
        List[Dict[str, Any]]: 未完成任务列表
    """
    system_logger.info(
        f"获取未完成任务列表：batch_id={batch_id}, task_type={task_type}"
    )

    manager = BatchTaskUnfinishedManager(task_type, storage_dir=storage_dir)
    manager.load_batch_tasks(batch_id)
    tasks = manager.get_unfinished_tasks(batch_id)

    system_logger.info(f"找到{len(tasks)}个未完成任务：batch_id={batch_id}")
    return tasks


def execute_new_batch_tasks(
    task_func: Callable[..., T],
    task_params_list: List[Dict[str, Any]],
    batch_id: str = None,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    record_failed: bool = True,
    failed_task_storage_dir: str = None,
    unfinished_task_storage_dir: str = None,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> BatchTask:
    """创建并执行新的批量任务

    此函数专门用于创建和执行新的批次任务，与execute_batch_tasks的区别是它不支持批次模式参数。

    Args:
        task_func: 任务执行函数
        task_params_list: 任务参数列表
        batch_id: 批次ID，默认自动生成
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        record_failed: 是否记录失败任务
        failed_task_storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录
        unfinished_task_storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        BatchTask: 批次任务对象
    """
    # 记录批量任务开始
    task_count = len(task_params_list) if task_params_list else 0
    system_logger.info(
        f"准备执行新批量任务：task_type={task_type}, "
        f"任务数量={task_count}, batch_id={batch_id}, execution_mode={execution_mode}"
    )
    user_logger.info(f"准备执行{task_count}个新任务，执行方式：{execution_mode}")

    # 参数验证
    if not task_params_list:
        raise ValueError("任务参数列表不能为空")

    executor = BatchTaskExecutor(
        task_type=task_type,
        max_workers=max_workers,
        task_interval=task_interval,
        task_timeout=task_timeout,
        record_failed=record_failed,
        max_retries=task_max_retries,
        retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        failed_task_storage_dir=failed_task_storage_dir,
        unfinished_task_storage_dir=unfinished_task_storage_dir,
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )

    return executor.execute_batch_tasks(
        task_func=task_func,
        task_params_list=task_params_list,
        batch_id=batch_id,
        task_timeout=task_timeout,
        task_interval=task_interval,
        max_workers=max_workers,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        batch_mode="new",  # 固定为新建模式
        execution_mode=execution_mode,
        show_progress=show_progress,
    )


# 以下是面向用户的简化接口函数


def dw_execute_task(
    task_func: Callable[..., T],
    task_params: Dict[str, Any] = None,
    task_id: str = None,
    task_type: str = "default",
    max_retries: int = None,
    retry_interval: float = None,
    backoff_factor: float = None,
) -> Any:
    """执行DataWhale单个任务

    Args:
        task_func: 任务执行函数
        task_params: 任务参数
        task_id: 任务ID，默认自动生成
        task_type: 任务类型
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子

    Returns:
        Any: 任务执行结果

    Examples:
        >>> def my_task(x, y):
        ...     return x + y
        >>> result = dw_execute_task(my_task, {"x": 1, "y": 2})
        >>> print(result)
        3
    """
    result = execute_task(
        task_func=task_func,
        task_params=task_params,
        task_id=task_id,
        task_type=task_type,
        max_retries=max_retries,
        retry_interval=retry_interval,
        backoff_factor=backoff_factor,
    )

    # 返回结果数据，而不是Result对象
    if result.success:
        return result.data
    else:
        raise ValueError(f"任务执行失败：{result.error}")


def dw_execute_batch_tasks(
    task_func: Callable[..., T],
    task_params_list: List[Dict[str, Any]],
    batch_id: str = None,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    record_failed: bool = True,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> Dict[str, Any]:
    """执行DataWhale批量任务

    Args:
        task_func: 任务执行函数
        task_params_list: 任务参数列表
        batch_id: 批次ID，默认自动生成
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        record_failed: 是否记录失败任务
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        Dict[str, Any]: 批量任务执行结果摘要

    Examples:
        >>> def my_task(x, y):
        ...     return x + y
        >>> params_list = [
        ...     {"x": 1, "y": 2},
        ...     {"x": 3, "y": 4},
        ...     {"x": 5, "y": 6}
        ... ]
        >>> result = dw_execute_batch_tasks(my_task, params_list)
        >>> print(result["total_tasks"])
        3
    """
    batch_task = execute_batch_tasks(
        task_func=task_func,
        task_params_list=task_params_list,
        batch_id=batch_id,
        task_type=task_type,
        max_workers=max_workers,
        task_timeout=task_timeout,
        task_interval=task_interval,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        record_failed=record_failed,
        batch_mode="new",  # 固定为新建模式
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )

    # 等待批次任务完成
    batch_task.wait()

    # 生成执行结果摘要
    return {
        "batch_id": batch_task.batch_id,
        "status": batch_task.status.name,
        "total_tasks": batch_task.total_tasks,
        "completed_tasks": batch_task.completed_tasks,
        "failed_tasks": batch_task.failed_tasks,
        "success_rate": batch_task.success_rate,
        "start_time": batch_task.start_time,
        "end_time": batch_task.end_time,
        "duration_seconds": batch_task.duration_seconds,
    }


def dw_resume_batch_tasks(
    task_func: Callable[..., T],
    batch_id: str,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> Dict[str, Any]:
    """恢复DataWhale批量任务

    Args:
        task_func: 任务执行函数
        batch_id: 批次ID
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        Dict[str, Any]: 批量任务执行结果摘要

    Examples:
        >>> def my_task(x, y):
        ...     return x + y
        >>> result = dw_resume_batch_tasks(my_task, "batch_123456")
        >>> print(result["status"])
        'COMPLETED'
    """
    batch_task = resume_batch_tasks(
        task_func=task_func,
        batch_id=batch_id,
        task_type=task_type,
        max_workers=max_workers,
        task_timeout=task_timeout,
        task_interval=task_interval,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )

    # 等待批次任务完成
    batch_task.wait()

    # 生成执行结果摘要
    return {
        "batch_id": batch_task.batch_id,
        "status": batch_task.status.name,
        "total_tasks": batch_task.total_tasks,
        "completed_tasks": batch_task.completed_tasks,
        "failed_tasks": batch_task.failed_tasks,
        "success_rate": batch_task.success_rate,
        "start_time": batch_task.start_time,
        "end_time": batch_task.end_time,
        "duration_seconds": batch_task.duration_seconds,
    }


def dw_retry_failed_tasks(
    task_func: Callable[..., T],
    batch_id: str,
    task_type: str = "default",
    max_workers: int = None,
    task_timeout: float = None,
    task_interval: float = None,
    task_max_retries: int = None,
    task_retry_interval: float = None,
    backoff_factor: float = None,
    execution_mode: ExecutionMode = "thread",  # 新增参数：执行模式
    show_progress: bool = True,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = 60,  # 新增参数：进程初始化超时时间
) -> Dict[str, Any]:
    """重试DataWhale失败的批量任务

    Args:
        task_func: 任务执行函数
        batch_id: 批次ID
        task_type: 任务类型
        max_workers: 最大工作线程数
        task_timeout: 单个任务超时时间（秒）
        task_interval: 任务提交间隔（秒）
        task_max_retries: 最大重试次数
        task_retry_interval: 重试间隔（秒）
        backoff_factor: 重试间隔的退避因子
        execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
        show_progress: 是否显示进度条
        process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

    Returns:
        Dict[str, Any]: 批量任务执行结果摘要

    Examples:
        >>> def my_task(x, y):
        ...     return x + y
        >>> result = dw_retry_failed_tasks(my_task, "batch_123456")
        >>> print(result["failed_tasks"])
        0
    """
    batch_task = retry_failed_tasks(
        task_func=task_func,
        batch_id=batch_id,
        task_type=task_type,
        max_workers=max_workers,
        task_timeout=task_timeout,
        task_interval=task_interval,
        task_max_retries=task_max_retries,
        task_retry_interval=task_retry_interval,
        backoff_factor=backoff_factor,
        execution_mode=execution_mode,
        show_progress=show_progress,
        process_initialization_timeout=process_initialization_timeout,
    )

    # 等待批次任务完成
    batch_task.wait()

    # 生成执行结果摘要
    return {
        "batch_id": batch_task.batch_id,
        "status": batch_task.status.name,
        "total_tasks": batch_task.total_tasks,
        "completed_tasks": batch_task.completed_tasks,
        "failed_tasks": batch_task.failed_tasks,
        "success_rate": batch_task.success_rate,
        "start_time": batch_task.start_time,
        "end_time": batch_task.end_time,
        "duration_seconds": batch_task.duration_seconds,
    }


def dw_get_failed_tasks(
    batch_id: str,
    task_type: str = "default",
) -> List[Dict[str, Any]]:
    """获取DataWhale失败任务列表

    Args:
        batch_id: 批次ID
        task_type: 任务类型

    Returns:
        List[Dict[str, Any]]: 失败任务列表

    Examples:
        >>> failed_tasks = dw_get_failed_tasks("batch_123456")
        >>> for task in failed_tasks:
        ...     print(task["task_id"], task["error"])
    """
    return get_failed_tasks(
        batch_id=batch_id,
        task_type=task_type,
    )


def dw_get_unfinished_tasks(
    batch_id: str,
    task_type: str = "default",
) -> List[Dict[str, Any]]:
    """获取DataWhale未完成任务列表

    Args:
        batch_id: 批次ID
        task_type: 任务类型

    Returns:
        List[Dict[str, Any]]: 未完成任务列表

    Examples:
        >>> unfinished_tasks = dw_get_unfinished_tasks("batch_123456")
        >>> print(f"未完成任务数量: {len(unfinished_tasks)}")
    """
    return get_unfinished_tasks(
        batch_id=batch_id,
        task_type=task_type,
    )
