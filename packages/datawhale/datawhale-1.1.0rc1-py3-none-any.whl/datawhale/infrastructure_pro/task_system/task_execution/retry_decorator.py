#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TypeVar, Callable, Any, Optional
import time
import traceback
from datetime import datetime
from functools import wraps
import logging
from datawhale.infrastructure_pro.logging.logger import (
    get_system_logger,
    get_user_logger,
)
from ...exceptions import TaskExecutionError
from .result import Result

# 创建系统和用户日志记录器
system_logger = get_system_logger(__name__)
user_logger = get_user_logger(__name__)

T = TypeVar("T")


class RetryDecorator:
    """重试装饰器

    负责为任务提供重试机制，通过装饰器方式应用于任务执行函数。
    作为task_system的核心组件，提供灵活可配置的重试策略。
    """

    def __init__(
        self,
        max_retries: Optional[int] = None,
        retry_interval: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ):
        """初始化重试装饰器

        Args:
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            backoff_factor: 重试间隔递增因子
        """
        # 设置默认值
        self.max_retries = max_retries if max_retries is not None else 0
        self.retry_interval = retry_interval if retry_interval is not None else 0
        self.backoff_factor = backoff_factor if backoff_factor is not None else 1.5
        self.retry_count = 0  # 初始化重试计数器

    def _calculate_retry_interval(self, attempt: int, error: Exception) -> float:
        """计算下一次重试的间隔时间

        根据重试次数和错误类型动态调整重试间隔

        Args:
            attempt: 当前重试次数
            error: 异常对象

        Returns:
            float: 重试间隔时间（秒）
        """
        # 基础重试间隔
        base_interval = self.retry_interval

        # 根据重试次数递增间隔
        interval = base_interval * (self.backoff_factor**attempt)

        return interval

    def get_retry_interval(self) -> float:
        """获取当前重试间隔时间

        根据当前的重试次数计算重试间隔

        Returns:
            float: 当前重试间隔时间（秒）
        """
        return self.retry_interval * (self.backoff_factor**self.retry_count)

    def reset(self) -> None:
        """重置重试计数器

        将重试计数器重置为0
        """
        self.retry_count = 0

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """将装饰器应用于函数

        Args:
            func: 需要添加重试功能的函数

        Returns:
            装饰后的函数
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self.retry_count = 0  # 重置重试计数器

            # 首先尝试初始执行（不计入重试次数）
            try:
                result = func(*args, **kwargs)
                context = {
                    "operation": (
                        func.__name__ if hasattr(func, "__name__") else "unknown"
                    ),
                    "attempt": 0,
                    "timestamp": datetime.now().isoformat(),
                }
                # 初始执行成功，直接返回结果
                system_logger.info(
                    f"操作首次尝试成功",
                    extra={"retry_context": context},
                )
                return result
            except Exception as initial_error:
                # 获取完整的异常追踪信息
                error_trace = traceback.format_exc()

                # 初始执行失败，记录错误并准备重试
                context = {
                    "operation": (
                        func.__name__ if hasattr(func, "__name__") else "unknown"
                    ),
                    "attempt": 0,
                    "error": str(initial_error),
                    "error_type": initial_error.__class__.__name__,
                    "error_trace": error_trace,
                    "timestamp": datetime.now().isoformat(),
                }

                # 如果不允许重试，直接失败
                if self.max_retries <= 0:
                    error_msg = f"操作失败，不允许重试: {str(initial_error)}"
                    system_logger.error(
                        f"{error_msg}\n{error_trace}",
                        extra={"retry_context": context},
                        exc_info=True,
                    )
                    if isinstance(initial_error, TaskExecutionError):
                        # 确保TaskExecutionError包含完整的跟踪信息
                        if (
                            not hasattr(initial_error, "traceback")
                            or not initial_error.traceback
                        ):
                            initial_error.traceback = error_trace
                        raise initial_error
                    else:
                        error = TaskExecutionError(error_msg)
                        error.traceback = error_trace
                        raise error from initial_error

                # 准备进行重试
                system_logger.warning(
                    f"操作首次尝试失败: {str(initial_error)}，将开始重试\n{error_trace}",
                    extra={"retry_context": context},
                )

                # 执行重试逻辑
                last_error = initial_error
                last_error_trace = error_trace

                for retry_attempt in range(self.max_retries):
                    self.retry_count = retry_attempt + 1  # 更新重试计数

                    # 计算当前重试的等待时间
                    retry_interval = self._calculate_retry_interval(
                        retry_attempt, initial_error
                    )
                    if retry_interval > 0:
                        time.sleep(retry_interval)

                    try:
                        # 执行重试
                        system_logger.info(
                            f"正在进行第{retry_attempt + 1}次重试（总共第{retry_attempt + 2}次尝试）"
                        )
                        result = func(*args, **kwargs)

                        # 重试成功
                        context = {
                            "operation": (
                                func.__name__
                                if hasattr(func, "__name__")
                                else "unknown"
                            ),
                            "attempt": retry_attempt + 1,
                            "timestamp": datetime.now().isoformat(),
                        }
                        system_logger.info(
                            f"重试成功，在第{retry_attempt + 1}次重试后成功（总共第{retry_attempt + 2}次尝试）",
                            extra={"retry_context": context},
                        )
                        return result
                    except Exception as retry_error:
                        # 获取完整的异常跟踪信息
                        retry_error_trace = traceback.format_exc()
                        last_error = retry_error
                        last_error_trace = retry_error_trace

                        # 重试失败
                        context = {
                            "operation": (
                                func.__name__
                                if hasattr(func, "__name__")
                                else "unknown"
                            ),
                            "attempt": retry_attempt + 1,
                            "error": str(retry_error),
                            "error_type": retry_error.__class__.__name__,
                            "error_trace": retry_error_trace,
                            "timestamp": datetime.now().isoformat(),
                        }

                        # 判断是否还有重试机会
                        if retry_attempt < self.max_retries - 1:
                            system_logger.warning(
                                f"第{retry_attempt + 1}次重试失败: {str(retry_error)}，"
                                f"将进行第{retry_attempt + 2}次重试\n{retry_error_trace}",
                                extra={"retry_context": context},
                            )
                            if retry_attempt >= 1:  # 只在多次重试时通知用户
                                user_logger.warning(
                                    f"操作失败，正在进行第{retry_attempt + 2}次重试"
                                )
                        else:
                            # 所有重试都失败
                            error_msg = f"操作失败: {str(retry_error)}"
                            system_logger.error(
                                f"所有重试尝试都失败(共{self.max_retries}次重试): {error_msg}\n{retry_error_trace}",
                                extra={"retry_context": context},
                                exc_info=True,
                            )
                            user_logger.error(f"操作失败，已重试{self.max_retries}次")

                            # 抛出最终异常，包含详细的跟踪信息
                            if isinstance(retry_error, TaskExecutionError):
                                # 确保TaskExecutionError包含完整的跟踪信息
                                if (
                                    not hasattr(retry_error, "traceback")
                                    or not retry_error.traceback
                                ):
                                    retry_error.traceback = retry_error_trace
                                raise retry_error
                            else:
                                error = TaskExecutionError(error_msg)
                                error.traceback = retry_error_trace
                                raise error from retry_error

                # 这里不应该执行到，因为循环中所有情况都已处理
                # 但以防万一，仍然抛出异常并附带最后一次的错误信息
                error = TaskExecutionError("意外的执行路径")
                error.traceback = last_error_trace
                raise error from last_error

        return wrapper


def with_retry(
    max_retries: Optional[int] = None,
    retry_interval: Optional[int] = None,
    backoff_factor: Optional[float] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """便捷的重试装饰器工厂函数

    Args:
        max_retries: 最大重试次数，默认为0（不重试）
        retry_interval: 重试间隔（秒），默认为0（无等待）
        backoff_factor: 重试间隔递增因子，默认为1.5

    Returns:
        RetryDecorator实例
    """
    return RetryDecorator(
        max_retries=max_retries,
        retry_interval=retry_interval,
        backoff_factor=backoff_factor,
    )


# 为了保持兼容性，将RetryManager作为RetryDecorator的别名
RetryManager = RetryDecorator
