#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional
import time
from datawhale.infrastructure_pro.logging import get_system_logger, get_user_logger
from .batch_status import BatchStatus

# 创建系统和用户日志记录器
system_logger = get_system_logger(__name__)
user_logger = get_user_logger(__name__)


class BatchTask:
    """批次任务类

    用于管理和跟踪批量任务的执行情况
    """

    def __init__(self, batch_id: Optional[str] = None, task_type: str = "default"):
        """初始化批次任务

        Args:
            batch_id: 批次ID，如果为None则自动生成
            task_type: 任务类型
        """
        self.batch_id = batch_id or f"{int(time.time())}"
        self.task_type = task_type
        self.status = BatchStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.total_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.paused_time = None  # 记录暂停时间
        self.total_pause_duration = 0  # 记录总暂停时长

        # 同时记录到系统日志和用户日志
        system_logger.info(
            f"创建批次任务：batch_id={self.batch_id}, task_type={self.task_type}"
        )
        user_logger.info(f"创建{self.task_type}类型的批次任务")

    def pause(self) -> None:
        """暂停批次任务"""
        if self.status == BatchStatus.RUNNING:
            self.paused_time = time.time()
            self.status = BatchStatus.PAUSED

            # 关键操作，记录到用户日志
            user_logger.info(f"批次任务已暂停")
            # 详细信息记录到系统日志
            system_logger.info(f"暂停批次任务：batch_id={self.batch_id}")

    def resume(self) -> None:
        """恢复批次任务"""
        if self.status == BatchStatus.PAUSED:
            if self.paused_time:
                self.total_pause_duration += time.time() - self.paused_time
            self.paused_time = None
            self.status = BatchStatus.RUNNING

            # 关键操作，记录到用户日志
            user_logger.info(f"批次任务已恢复运行")
            # 详细信息记录到系统日志
            system_logger.info(
                f"恢复批次任务：batch_id={self.batch_id}, 总暂停时长={self.total_pause_duration:.2f}秒"
            )

    def get_execution_time(self) -> Optional[float]:
        """获取执行时间（不包括暂停时间）

        Returns:
            float: 执行时间（秒），如果任务未完成则返回None
        """
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            return total_time - self.total_pause_duration
        return None

    def start(self) -> None:
        """开始执行批次任务"""
        self.start_time = time.time()
        self.status = BatchStatus.RUNNING

        # 关键操作，记录到用户日志
        user_logger.info(f"开始执行{self.task_type}批次任务")
        # 详细信息记录到系统日志
        system_logger.info(
            f"开始执行批次任务：batch_id={self.batch_id}, 开始时间={self.start_time}"
        )

    def complete(self) -> None:
        """完成批次任务"""
        self.end_time = time.time()
        self.status = BatchStatus.COMPLETED
        execution_time = self.get_execution_time() or 0

        # 关键操作，记录到用户日志，包含完成情况
        user_logger.info(
            f"批次任务已完成，成功{self.success_count}项，失败{self.failed_count}项，耗时{execution_time:.2f}秒"
        )
        # 详细信息记录到系统日志
        system_logger.info(
            f"完成批次任务：batch_id={self.batch_id}, "
            f"成功率={self.success_count/self.total_count*100:.1f}%, "
            f"执行时间={execution_time:.2f}秒"
        )

    def fail(self) -> None:
        """批次任务失败"""
        self.end_time = time.time()
        self.status = BatchStatus.FAILED
        execution_time = self.get_execution_time() or 0

        # 错误情况，记录到用户日志，提醒用户
        user_logger.error(
            f"批次任务执行失败，已处理{self.success_count + self.failed_count}/{self.total_count}项"
        )
        # 详细错误信息记录到系统日志
        system_logger.error(
            f"批次任务失败：batch_id={self.batch_id}, "
            f"成功={self.success_count}, 失败={self.failed_count}, "
            f"执行时间={execution_time:.2f}秒"
        )

    def cancel(self) -> None:
        """取消批次任务"""
        self.end_time = time.time()
        self.status = BatchStatus.CANCELLED
        execution_time = self.get_execution_time() or 0

        # 主动取消，记录到用户日志
        user_logger.warning(
            f"批次任务已取消，已处理{self.success_count + self.failed_count}/{self.total_count}项"
        )
        # 详细信息记录到系统日志
        system_logger.warning(
            f"取消批次任务：batch_id={self.batch_id}, "
            f"已处理={self.success_count + self.failed_count}/{self.total_count}, "
            f"执行时间={execution_time:.2f}秒"
        )

    def interrupt(self) -> None:
        """中断批次任务"""
        self.end_time = time.time()
        self.status = BatchStatus.INTERRUPTED
        execution_time = self.get_execution_time() or 0

        # 系统中断，记录到用户日志
        user_logger.warning(
            f"批次任务被中断，已处理{self.success_count + self.failed_count}/{self.total_count}项"
        )
        # 详细信息记录到系统日志
        system_logger.warning(
            f"中断批次任务：batch_id={self.batch_id}, "
            f"已处理={self.success_count + self.failed_count}/{self.total_count}, "
            f"执行时间={execution_time:.2f}秒"
        )

    def set_status(self, status: BatchStatus) -> None:
        """设置批次任务状态

        Args:
            status: 批次状态
        """
        self.status = status
        # 仅记录到系统日志，这是内部操作
        system_logger.debug(
            f"设置批次任务状态：batch_id={self.batch_id}, status={status.value}"
        )

    def set_total_count(self, count: int) -> None:
        """设置总任务数

        Args:
            count: 总任务数
        """
        self.total_count = count
        # 记录到用户日志，总任务数是重要信息
        user_logger.info(f"批次任务包含{count}个子任务")
        # 详细信息记录到系统日志
        system_logger.debug(
            f"设置总任务数：batch_id={self.batch_id}, total_count={count}"
        )

    def increment_success_count(self) -> None:
        """增加成功任务数"""
        self.success_count += 1
        # 细节操作，只记录到系统日志
        system_logger.debug(
            f"增加成功任务数：batch_id={self.batch_id}, success_count={self.success_count}"
        )

        # 每处理10%的任务记录一次进度到用户日志
        if (
            self.total_count > 0
            and self.success_count % max(1, int(self.total_count * 0.1)) == 0
        ):
            progress = (self.success_count + self.failed_count) / self.total_count * 100
            user_logger.info(
                f"批次任务进度：{progress:.1f}%，成功：{self.success_count}，失败：{self.failed_count}"
            )

    def increment_failed_count(self) -> None:
        """增加失败任务数"""
        self.failed_count += 1
        # 记录到系统日志
        system_logger.debug(
            f"增加失败任务数：batch_id={self.batch_id}, failed_count={self.failed_count}"
        )

        # 对于失败，可能需要更及时地通知用户
        # 失败过多时，记录警告到用户日志
        if (
            self.total_count > 0
            and self.failed_count > 0
            and (self.failed_count % max(1, int(self.total_count * 0.05)) == 0)
        ):
            failure_rate = (
                self.failed_count / (self.success_count + self.failed_count) * 100
            )
            if failure_rate > 20:  # 如果失败率超过20%，发出警告
                user_logger.warning(
                    f"批次任务失败率较高：{failure_rate:.1f}%，请注意检查"
                )

    def set_end_time(self, end_time: Optional[float] = None) -> None:
        """设置结束时间

        Args:
            end_time: 结束时间，默认为当前时间
        """
        self.end_time = end_time or time.time()
        # 内部操作，只记录到系统日志
        system_logger.debug(
            f"设置结束时间：batch_id={self.batch_id}, end_time={self.end_time}"
        )

    def get_status_dict(self) -> Dict[str, Any]:
        """获取批次状态信息

        Returns:
            Dict[str, Any]: 批次状态信息
        """
        return {
            "batch_id": self.batch_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.get_execution_time(),
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "success_rate": (
                self.success_count / self.total_count if self.total_count > 0 else 0
            ),
            "batch_mode": "new",  # 默认为new模式
        }
