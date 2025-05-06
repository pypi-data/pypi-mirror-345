#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional, TypeVar, Callable
from enum import Enum
import time
import traceback
from uuid import uuid4

# 同模块内的导入使用相对导入
from .retry_decorator import with_retry
from .result import Result

# 跨模块的导入使用绝对导入，优先从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger
from datawhale.infrastructure_pro.exceptions import TaskExecutionError

# 创建用户和系统日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")


class TaskStatus(Enum):
    """任务状态枚举

    定义任务的可能状态，用于跟踪任务的生命周期。
    """

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败


class Task:
    """任务对象

    封装任务的基本属性和行为，提供统一的任务管理接口。
    作为基础设施层的核心组件，为进程管理器提供任务抽象。

    任务状态说明：
    - PENDING: 等待执行，表示任务已创建但尚未开始执行
    - RUNNING: 正在执行，表示任务正在执行过程中
    - COMPLETED: 执行完成，表示任务已成功完成
    - FAILED: 执行失败，表示任务执行过程中遇到错误
    """

    def __init__(
        self,
        task_type: str,
        params: Dict[str, Any],
        task_func: Callable[[Dict[str, Any]], T],
        task_id: str = None,
        max_retries: int = None,
        retry_interval: float = None,
        backoff_factor: float = None,
        timeout: float = None,
        batch_id: str = None,
    ):
        """初始化任务对象

        Args:
            task_type (str): 任务类型标识
            params (Dict[str, Any]): 任务执行参数字典。这个字典中的键值对将作为关键字参数传递给task_func函数，
                                    因此params中的键必须与task_func函数的参数名称完全匹配。
            task_func (Callable[[Dict[str, Any]], T]): 任务执行函数。这个函数将在任务执行时被调用，
                                                     它接收params字典中的参数作为关键字参数（使用**params方式传递），
                                                     因此task_func的参数签名必须能够接收params字典中指定的所有参数。
            task_id (str, optional): 任务唯一标识符。如果不提供，将自动生成。
            max_retries (int, optional): 最大重试次数。这是指任务失败后允许重试的次数，不包括首次执行。
                                        例如，max_retries=3表示任务最多可以执行4次（1次初始执行+3次重试）。
            retry_interval (float, optional): 重试间隔时间（秒），即两次重试之间的等待时间
            backoff_factor (float, optional): 重试间隔的退避因子，用于计算递增的重试间隔
            timeout (float, optional): 任务执行超时时间（秒）
            batch_id (str, optional): 批处理任务ID
        """
        self.task_id = task_id or f"{task_type}_{uuid4().hex}"
        self.task_type = task_type
        self.params = params
        self.task_func = task_func
        self.status = TaskStatus.PENDING
        self.result: Optional[Result[Any]] = None
        self.error: Optional[str] = None
        self.error_trace: Optional[str] = None  # 添加错误跟踪信息字段
        self.create_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.timeout = timeout
        self.batch_id = batch_id

        # 保存重试相关参数
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.backoff_factor = backoff_factor

        # 记录任务创建信息
        system_logger.debug(
            f"创建任务：task_id={self.task_id}, task_type={self.task_type}"
        )

    def execute(self) -> Result[Any]:
        """执行任务

        Returns:
            Result[Any]: 任务执行结果
        """
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()

        # 记录任务开始执行
        system_logger.debug(f"开始执行任务：task_id={self.task_id}")

        # 提取关键参数（如有）用于日志记录
        log_params = {}
        # 如果有id或name类型的参数，记录到日志
        for key, value in self.params.items():
            if (
                key.endswith("_id")
                or key.endswith("_name")
                or key == "id"
                or key == "name"
            ):
                log_params[key] = value

        if log_params:
            param_str = ", ".join(f"{k}={v}" for k, v in log_params.items())
            system_logger.debug(f"任务参数：{param_str}")

        # 创建带有重试功能的任务执行函数
        @with_retry(
            max_retries=self.max_retries,
            retry_interval=self.retry_interval,
            backoff_factor=self.backoff_factor,
        )
        def _execute_task() -> Result[Any]:
            try:
                # 检查任务超时
                if self.timeout:
                    start = time.time()

                    # 执行任务函数
                    result = self.task_func(**self.params)

                    # 检查是否超时
                    if time.time() - start > self.timeout:
                        self.error = f"任务执行超时，超过了{self.timeout}秒"
                        error_trace = traceback.format_exc()
                        self.error_trace = error_trace
                        system_logger.error(
                            f"任务执行超时：task_id={self.task_id}, timeout={self.timeout}\n{error_trace}"
                        )
                        raise TaskExecutionError(self.error)
                else:
                    # 执行任务函数
                    result = self.task_func(**self.params)

                # 标准化返回结果
                if isinstance(result, Result):
                    task_result = result
                else:
                    task_result = Result.success(result)

                return task_result

            except Exception as e:
                # 捕获详细的错误跟踪信息
                error_trace = traceback.format_exc()
                self.error = str(e)
                self.error_trace = error_trace
                system_logger.error(
                    f"任务执行异常：task_id={self.task_id}, error={self.error}\n{error_trace}"
                )

                # 创建包含详细错误信息的TaskExecutionError
                error = TaskExecutionError(self.error)
                error.traceback = error_trace
                raise error

        try:
            # 执行带有重试功能的任务
            result = _execute_task()
            self.result = result
            self.end_time = time.time()

            # 根据结果设置状态
            if result.success:
                self.status = TaskStatus.COMPLETED
                # 记录执行成功
                elapsed_time = self.end_time - self.start_time
                system_logger.debug(
                    f"任务执行成功：task_id={self.task_id}, 耗时={elapsed_time:.3f}秒"
                )
            else:
                self.status = TaskStatus.FAILED
                self.error = result.error or "未知错误"
                if hasattr(result, "error_trace"):
                    self.error_trace = result.error_trace
                # 记录执行失败
                elapsed_time = self.end_time - self.start_time
                error_log = f"任务执行失败：task_id={self.task_id}, error={self.error}, 耗时={elapsed_time:.3f}秒"
                if self.error_trace:
                    error_log += f"\n{self.error_trace}"
                system_logger.error(error_log)

            return result

        except TaskExecutionError as e:
            self.status = TaskStatus.FAILED
            self.error = e.args[0] if e.args else str(e)
            # 获取异常中的跟踪信息
            if hasattr(e, "traceback"):
                self.error_trace = e.traceback
            else:
                self.error_trace = traceback.format_exc()
            self.end_time = time.time()

            # 创建失败结果对象
            failure_result = Result.failure(self.error)
            # 传递错误跟踪信息
            failure_result.error_trace = self.error_trace
            self.result = failure_result

            # 记录执行失败
            elapsed_time = self.end_time - self.start_time
            system_logger.error(
                f"任务执行失败：task_id={self.task_id}, error={self.error}, 耗时={elapsed_time:.3f}秒\n{self.error_trace}"
            )

            return failure_result
        except Exception as e:
            # 捕获所有其他可能的异常，确保能返回Result对象
            self.status = TaskStatus.FAILED
            self.error = f"任务执行异常: {str(e)}"
            self.error_trace = traceback.format_exc()
            self.end_time = time.time()

            # 创建失败结果对象
            failure_result = Result.failure(self.error)
            failure_result.error_trace = self.error_trace
            self.result = failure_result

            # 记录执行失败
            elapsed_time = self.end_time - self.start_time
            system_logger.error(
                f"任务执行意外异常：task_id={self.task_id}, error={self.error}, 耗时={elapsed_time:.3f}秒\n{self.error_trace}"
            )

            return failure_result

    def to_dict(self) -> Dict[str, Any]:
        """将任务转换为字典表示

        Returns:
            Dict[str, Any]: 任务的字典表示
        """
        execution_time = 0
        if self.start_time and self.end_time:
            execution_time = self.end_time - self.start_time

        result = {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "params": self.params,
            "status": self.status.value,
            "error": self.error,
            "error_trace": self.error_trace,  # 添加错误跟踪信息到字典
            "create_time": self.create_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": execution_time,
        }

        if self.batch_id:
            result["batch_id"] = self.batch_id

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务对象

        Args:
            data: 包含任务信息的字典

        Returns:
            Task: 创建的任务对象
        """
        # 创建一个空的任务对象
        task = cls(
            task_type=data.get("task_type", "default"),
            params=data.get("params", {}),
            task_func=lambda **kwargs: None,  # 设置一个空函数，因为实际函数无法序列化
            task_id=data.get("task_id"),
        )

        # 设置其他属性
        if "status" in data:
            task.status = data["status"]
        if "error" in data:
            task.error = data["error"]
        if "error_trace" in data:
            task.error_trace = data["error_trace"]
        if "start_time" in data:
            task.start_time = data["start_time"]
        if "end_time" in data:
            task.end_time = data["end_time"]
        if "batch_id" in data:
            task.batch_id = data["batch_id"]

        return task
