#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务服务模块

提供任务执行和管理服务的统一接口，支持单任务和批量任务处理。

主要功能:
- 执行单个任务
- 执行批量任务
- 恢复未完成的批量任务
- 重试失败的批量任务
- 获取失败任务列表
- 获取未完成任务列表

提供标准化的接口，隔离底层实现细节，便于用户快速上手和使用。
"""

from typing import Dict, List, Any, Callable, TypeVar, Optional, Literal
import os
import time
import traceback

# 跨模块的导入优先从顶层模块导入
from datawhale.logging import get_system_logger, get_user_logger
from datawhale.config import config, get_config
from datawhale.infrastructure_pro.exceptions import TaskExecutionError

# 同模块内的导入使用相对导入
from .task_execution.task import Task, TaskStatus
from .task_execution.result import Result
from .batch_task_executor import BatchTaskExecutor
from .batch_task.batch_task import BatchTask
from .batch_task.batch_status import BatchStatus
from .batch_task.batch_task_failure_manager import BatchTaskFailureManager
from .batch_task.batch_task_unfinished_manager import BatchTaskUnfinishedManager

# 系统日志记录器，用于详细技术日志
logger = get_system_logger(__name__)
# 用户日志记录器，用于记录主要操作和状态变化
user_logger = get_user_logger(__name__)

T = TypeVar("T")
# 定义执行模式类型
ExecutionMode = Literal["thread", "process"]


class TaskService:
    """任务服务实现

    提供基于配置的任务执行和管理服务，支持单任务和批量任务处理。

    主要功能：
    1. 单任务执行与重试
    2. 批量任务处理
    3. 任务进度跟踪和恢复
    4. 失败任务管理

    属性：
        failed_task_dir (str): 失败任务存储目录
        unfinished_task_dir (str): 未完成任务存储目录
        default_max_workers (int): 默认最大工作线程数
        default_task_timeout (float): 默认任务超时时间
        default_task_interval (float): 默认任务间隔时间
        default_max_retries (int): 默认最大重试次数
        default_retry_interval (float): 默认重试间隔
        default_backoff_factor (float): 默认退避因子
        default_execution_mode (str): 默认执行模式
        default_process_initialization_timeout (int): 默认进程初始化超时时间
        default_show_progress (bool): 默认是否显示进度条
    """

    def __init__(self, task_config=None):
        """初始化任务服务

        使用task.yaml配置文件中的配置初始化任务服务。

        Args:
            task_config: 任务配置，如果为None则从配置系统获取

        Raises:
            TaskExecutionError: 配置文件缺少必要字段时抛出
        """
        try:
            # 声明storage_config变量
            storage_config = None

            # 如果没有提供配置，则从config装饰器获取
            if task_config is None:
                config_manager = get_config()
                task_config = config_manager.get("infrastructure.task")
                storage_config = config_manager.get("infrastructure.storage")
                if task_config is None:
                    raise TaskExecutionError("配置文件缺少[infrastructure.task]配置项")
                if storage_config is None:
                    raise TaskExecutionError(
                        "配置文件缺少[infrastructure.storage]配置项"
                    )
            else:
                # 如果提供了自定义task_config，确保也有storage_config
                config_manager = get_config()
                storage_config = config_manager.get("infrastructure.storage")
                if storage_config is None:
                    # 使用测试环境下的默认配置，假设task_config中包含runtime_dir
                    storage_config = {
                        "runtime_dir": task_config.get("runtime_dir", "test_runtime")
                    }

            if "runtime_dir" not in storage_config:
                raise TaskExecutionError("配置文件缺少[runtime_dir]参数")

            # 检查并获取必要的配置项
            # 目录配置
            if "failed_task_dir" not in task_config:
                raise TaskExecutionError("配置文件缺少[failed_task_dir]参数")
            if "unfinished_task_dir" not in task_config:
                raise TaskExecutionError("配置文件缺少[unfinished_task_dir]参数")
            # 规范化路径分隔符，确保跨平台兼容性
            runtime_dir = os.path.normpath(storage_config["runtime_dir"])
            self.failed_task_dir = os.path.normpath(
                os.path.join(runtime_dir, task_config["failed_task_dir"])
            )
            self.unfinished_task_dir = os.path.normpath(
                os.path.join(runtime_dir, task_config["unfinished_task_dir"])
            )

            # 执行参数配置
            if "max_workers" not in task_config:
                raise TaskExecutionError("配置文件缺少[max_workers]参数")
            if "task_timeout" not in task_config:
                raise TaskExecutionError("配置文件缺少[task_timeout]参数")
            if "task_interval" not in task_config:
                raise TaskExecutionError("配置文件缺少[task_interval]参数")
            if "max_retries" not in task_config:
                raise TaskExecutionError("配置文件缺少[max_retries]参数")
            if "retry_interval" not in task_config:
                raise TaskExecutionError("配置文件缺少[retry_interval]参数")
            if "backoff_factor" not in task_config:
                raise TaskExecutionError("配置文件缺少[backoff_factor]参数")
            if "execution_mode" not in task_config:
                raise TaskExecutionError("配置文件缺少[execution_mode]参数")
            if "process_initialization_timeout" not in task_config:
                raise TaskExecutionError(
                    "配置文件缺少[process_initialization_timeout]参数"
                )
            if "show_progress" not in task_config:
                raise TaskExecutionError("配置文件缺少[show_progress]参数")

            # 设置执行参数
            self.default_max_workers = task_config["max_workers"]
            self.default_task_timeout = task_config["task_timeout"]
            self.default_task_interval = task_config["task_interval"]
            self.default_max_retries = task_config["max_retries"]
            self.default_retry_interval = task_config["retry_interval"]
            self.default_backoff_factor = task_config["backoff_factor"]
            self.default_execution_mode = task_config["execution_mode"]
            self.default_process_initialization_timeout = task_config[
                "process_initialization_timeout"
            ]
            self.default_show_progress = task_config["show_progress"]

            # 确保必要目录存在
            self._init_dirs()

            # 创建批量任务执行器实例
            self.executor = BatchTaskExecutor(
                task_type="default",
                max_workers=self.default_max_workers,
                task_interval=self.default_task_interval,
                task_timeout=self.default_task_timeout,
                record_failed=True,
                max_retries=self.default_max_retries,
                retry_interval=self.default_retry_interval,
                backoff_factor=self.default_backoff_factor,
                failed_task_storage_dir=self.failed_task_dir,
                unfinished_task_storage_dir=self.unfinished_task_dir,
                execution_mode=self.default_execution_mode,
                process_initialization_timeout=self.default_process_initialization_timeout,
                show_progress=self.default_show_progress,
            )

            logger.info(
                f"任务服务初始化完成：failed_task_dir={self.failed_task_dir}, "
                f"unfinished_task_dir={self.unfinished_task_dir}, "
                f"execution_mode={self.default_execution_mode}"
            )
            user_logger.info("任务服务初始化完成")

        except Exception as e:
            if isinstance(e, TaskExecutionError):
                logger.error(f"任务服务初始化失败：{str(e)}")
                user_logger.error(f"任务服务初始化失败：{str(e)}")
                raise

            error_msg = f"任务服务初始化失败：{str(e)}"
            logger.error(error_msg)
            user_logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def _init_dirs(self) -> None:
        """初始化任务存储目录

        创建失败任务和未完成任务的存储目录。

        Raises:
            TaskExecutionError: 初始化失败时抛出
        """
        try:
            os.makedirs(self.failed_task_dir, exist_ok=True)
            os.makedirs(self.unfinished_task_dir, exist_ok=True)
            logger.info("任务存储目录初始化成功")
        except Exception as e:
            error_msg = f"初始化任务存储目录失败：{str(e)}"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def execute_task(
        self,
        task_func: Callable[..., T],
        task_params: Dict[str, Any] = None,
        task_id: str = None,
        task_type: str = "default",
        max_retries: int = None,
        retry_interval: float = None,
        backoff_factor: float = None,
    ) -> Any:
        """执行单个任务

        Args:
            task_func: 任务执行函数
            task_params: 任务参数
            task_id: 任务ID，默认自动生成
            task_type: 任务类型
            max_retries: 最大重试次数，如果为None则使用默认值
            retry_interval: 重试间隔（秒），如果为None则使用默认值
            backoff_factor: 重试间隔的退避因子，如果为None则使用默认值

        Returns:
            Any: 任务执行结果

        Raises:
            TaskExecutionError: 任务执行失败时抛出
        """
        try:
            user_logger.info(f"开始执行任务：{task_type}")
            logger.info(f"执行单个任务：task_id={task_id}, task_type={task_type}")

            # 使用默认值
            if max_retries is None:
                max_retries = self.default_max_retries
            if retry_interval is None:
                retry_interval = self.default_retry_interval
            if backoff_factor is None:
                backoff_factor = self.default_backoff_factor

            # 创建任务对象
            task = Task(
                task_type=task_type,
                params=task_params or {},
                task_func=task_func,
                task_id=task_id,
                max_retries=max_retries,
                retry_interval=retry_interval,
                backoff_factor=backoff_factor,
            )

            # 执行任务
            result = task.execute()

            # 处理结果
            if result.success:
                user_logger.info("任务执行成功")
                return result.data
            else:
                error_msg = f"任务执行失败：{result.error}"
                user_logger.error(error_msg)
                raise TaskExecutionError(error_msg)

        except Exception as e:
            if isinstance(e, TaskExecutionError):
                raise

            error_msg = f"任务执行出错：{str(e)}"
            logger.error(error_msg)
            user_logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def execute_batch_tasks(
        self,
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
        execution_mode: ExecutionMode = None,  # 新增参数：执行模式
        show_progress: bool = None,  # 新增参数：是否显示进度条
        process_initialization_timeout: int = None,  # 新增参数：进程初始化超时时间
    ) -> Dict[str, Any]:
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
            execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
            show_progress: 是否显示进度条
            process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

        Returns:
            Dict[str, Any]: 批量任务执行结果摘要

        Raises:
            TaskExecutionError: 批量任务执行过程中出错时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始执行批量任务：{task_type}，模式：{batch_mode}")
            task_count = len(task_params_list) if task_params_list else "未知"
            logger.info(
                f"执行批量任务：batch_id={batch_id}, task_type={task_type}, 任务数量={task_count}"
            )

            # 使用默认值
            if max_workers is None:
                max_workers = self.default_max_workers
            if task_timeout is None:
                task_timeout = self.default_task_timeout
            if task_interval is None:
                task_interval = self.default_task_interval
            if task_max_retries is None:
                task_max_retries = self.default_max_retries
            if task_retry_interval is None:
                task_retry_interval = self.default_retry_interval
            if backoff_factor is None:
                backoff_factor = self.default_backoff_factor
            if execution_mode is None:
                execution_mode = self.default_execution_mode
            if show_progress is None:
                show_progress = self.default_show_progress
            if process_initialization_timeout is None:
                process_initialization_timeout = (
                    self.default_process_initialization_timeout
                )

            # 更新执行器参数
            self.executor.max_workers = max_workers
            self.executor.task_interval = task_interval
            self.executor.task_timeout = task_timeout
            self.executor.max_retries = task_max_retries
            self.executor.retry_interval = task_retry_interval
            self.executor.backoff_factor = backoff_factor
            self.executor.record_failed = record_failed
            self.executor.task_type = task_type
            self.executor.execution_mode = execution_mode
            self.executor.show_progress = show_progress
            self.executor.process_initialization_timeout = (
                process_initialization_timeout
            )

            # 执行批量任务
            batch_task = self.executor.execute_batch_tasks(
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

            # 等待批量任务完成
            batch_task.wait()

            # 生成执行结果摘要
            result_summary = {
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

            # 记录执行结果
            if batch_task.failed_tasks == 0:
                user_logger.info(f"批量任务全部成功：共{batch_task.total_tasks}个任务")
            else:
                user_logger.warning(
                    f"批量任务部分失败：总数{batch_task.total_tasks}，"
                    f"成功{batch_task.completed_tasks}，"
                    f"失败{batch_task.failed_tasks}"
                )

            return result_summary

        except Exception as e:
            if isinstance(e, TaskExecutionError):
                raise

            error_msg = f"批量任务执行出错：{str(e)}"
            logger.error(error_msg)
            user_logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def resume_batch_tasks(
        self,
        task_func: Callable[..., T],
        batch_id: str,
        task_type: str = "default",
        max_workers: int = None,
        task_timeout: float = None,
        task_interval: float = None,
        task_max_retries: int = None,
        task_retry_interval: float = None,
        backoff_factor: float = None,
        execution_mode: ExecutionMode = None,  # 新增参数：执行模式
        show_progress: bool = None,  # 新增参数：是否显示进度条
        process_initialization_timeout: int = None,  # 新增参数：进程初始化超时时间
    ) -> Dict[str, Any]:
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
            execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
            show_progress: 是否显示进度条
            process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

        Returns:
            Dict[str, Any]: 批量任务执行结果摘要

        Raises:
            TaskExecutionError: 恢复批量任务过程中出错时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始恢复批量任务：{batch_id}")
            logger.info(f"恢复批量任务：batch_id={batch_id}, task_type={task_type}")

            # 复用execute_batch_tasks方法，使用resume模式
            return self.execute_batch_tasks(
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
                execution_mode=execution_mode,
                show_progress=show_progress,
                process_initialization_timeout=process_initialization_timeout,
            )
        except Exception as e:
            if isinstance(e, TaskExecutionError):
                raise

            error_msg = f"恢复批量任务出错：{str(e)}"
            logger.error(error_msg)
            user_logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def retry_failed_tasks(
        self,
        task_func: Callable[..., T],
        batch_id: str,
        task_type: str = "default",
        max_workers: int = None,
        task_timeout: float = None,
        task_interval: float = None,
        task_max_retries: int = None,
        task_retry_interval: float = None,
        backoff_factor: float = None,
        execution_mode: ExecutionMode = None,  # 新增参数：执行模式
        show_progress: bool = None,  # 新增参数：是否显示进度条
        process_initialization_timeout: int = None,  # 新增参数：进程初始化超时时间
    ) -> Dict[str, Any]:
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
            execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程）
            show_progress: 是否显示进度条
            process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效

        Returns:
            Dict[str, Any]: 批量任务执行结果摘要

        Raises:
            TaskExecutionError: 重试失败任务过程中出错时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始重试失败任务：{batch_id}")
            logger.info(f"重试失败任务：batch_id={batch_id}, task_type={task_type}")

            # 复用execute_batch_tasks方法，使用retry模式
            return self.execute_batch_tasks(
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
                execution_mode=execution_mode,
                show_progress=show_progress,
                process_initialization_timeout=process_initialization_timeout,
            )
        except Exception as e:
            if isinstance(e, TaskExecutionError):
                raise

            error_msg = f"重试失败任务出错：{str(e)}"
            logger.error(error_msg)
            user_logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def get_failed_tasks(
        self,
        batch_id: str,
        task_type: str = "default",
    ) -> List[Dict[str, Any]]:
        """获取失败任务列表

        Args:
            batch_id: 批次ID
            task_type: 任务类型

        Returns:
            List[Dict[str, Any]]: 失败任务列表

        Raises:
            TaskExecutionError: 获取失败任务列表过程中出错时抛出
        """
        try:
            logger.info(f"获取失败任务列表：batch_id={batch_id}, task_type={task_type}")

            # 创建失败任务管理器
            failure_manager = BatchTaskFailureManager(
                task_type=task_type, storage_dir=self.failed_task_dir
            )

            # 加载批次任务
            failure_manager.load_batch_tasks(batch_id)

            # 获取失败任务
            failed_tasks = failure_manager.get_failed_tasks(batch_id)

            logger.info(f"获取到{len(failed_tasks)}个失败任务")
            return failed_tasks

        except Exception as e:
            error_msg = f"获取失败任务列表出错：{str(e)}"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)

    def get_unfinished_tasks(
        self,
        batch_id: str,
        task_type: str = "default",
    ) -> List[Dict[str, Any]]:
        """获取未完成任务列表

        Args:
            batch_id: 批次ID
            task_type: 任务类型

        Returns:
            List[Dict[str, Any]]: 未完成任务列表

        Raises:
            TaskExecutionError: 获取未完成任务列表过程中出错时抛出
        """
        try:
            logger.info(
                f"获取未完成任务列表：batch_id={batch_id}, task_type={task_type}"
            )

            # 创建未完成任务管理器
            unfinished_manager = BatchTaskUnfinishedManager(
                task_type=task_type, storage_dir=self.unfinished_task_dir
            )

            # 加载批次任务
            unfinished_manager.load_batch_tasks(batch_id)

            # 获取未完成任务
            unfinished_tasks = unfinished_manager.get_unfinished_tasks(batch_id)

            logger.info(f"获取到{len(unfinished_tasks)}个未完成任务")
            return unfinished_tasks

        except Exception as e:
            error_msg = f"获取未完成任务列表出错：{str(e)}"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)


# 创建一个全局单例变量，但不立即初始化
_task_service_instance = None


def _get_task_service():
    """获取TaskService单例实例

    使用懒加载方式，只有在首次调用时才会创建实例

    Returns:
        TaskService: 任务服务实例
    """
    global _task_service_instance
    if _task_service_instance is None:
        # 首次调用时初始化
        _task_service_instance = TaskService()
        logger.debug("TaskService实例已按需初始化")
    return _task_service_instance


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
    return _get_task_service().execute_task(
        task_func=task_func,
        task_params=task_params,
        task_id=task_id,
        task_type=task_type,
        max_retries=max_retries,
        retry_interval=retry_interval,
        backoff_factor=backoff_factor,
    )


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
    execution_mode: ExecutionMode = None,  # 新增参数：执行模式
    show_progress: bool = None,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = None,  # 新增参数：进程初始化超时时间
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
    return _get_task_service().execute_batch_tasks(
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
    execution_mode: ExecutionMode = None,  # 新增参数：执行模式
    show_progress: bool = None,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = None,  # 新增参数：进程初始化超时时间
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
    return _get_task_service().resume_batch_tasks(
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
    execution_mode: ExecutionMode = None,  # 新增参数：执行模式
    show_progress: bool = None,  # 新增参数：是否显示进度条
    process_initialization_timeout: int = None,  # 新增参数：进程初始化超时时间
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
    return _get_task_service().retry_failed_tasks(
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
    return _get_task_service().get_failed_tasks(
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
        >>> for task in unfinished_tasks:
        ...     print(task["task_id"], task["params"])
    """
    return _get_task_service().get_unfinished_tasks(
        batch_id=batch_id,
        task_type=task_type,
    )
