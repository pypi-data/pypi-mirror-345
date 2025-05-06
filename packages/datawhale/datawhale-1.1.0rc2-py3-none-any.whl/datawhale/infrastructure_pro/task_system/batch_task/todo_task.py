#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, Any, Literal
from datetime import datetime
from enum import Enum


class TodoReason(str, Enum):
    """待处理任务原因枚举"""

    FAILED = "Failed"  # 任务执行失败
    NO_RUN = "NoRun"  # 任务未运行

    def __str__(self) -> str:
        return self.value


@dataclass
class TodoTask:
    """待处理任务数据类

    用于规范化待处理任务的信息存储，包含任务的基本信息。
    这是一个纯数据容器，不包含任务执行逻辑。
    可以表示两种类型的待处理任务：执行失败的任务和未运行的任务。
    """

    task_id: str
    batch_id: str
    task_params: Dict[str, Any]
    task_type: str
    record_time: str
    todo_reason: str  # TodoReason.FAILED 或 TodoReason.NO_RUN
    error_msg: str = ""
    stack_trace: str = ""
    status: str = "todo"

    @classmethod
    def create_failed_task(
        cls,
        task_id: str,
        batch_id: str,
        task_params: Dict[str, Any],
        error_msg: str,
        task_type: str,
        stack_trace: str = "",
    ) -> "TodoTask":
        """创建失败的待处理任务实例

        Args:
            task_id: 任务ID
            batch_id: 批次ID
            task_params: 任务参数
            error_msg: 错误信息
            task_type: 任务类型
            stack_trace: 堆栈信息

        Returns:
            TodoTask: 失败的待处理任务实例
        """
        return cls(
            task_id=task_id,
            batch_id=batch_id,
            record_time=datetime.now().isoformat(),
            task_params=task_params,
            error_msg=error_msg,
            task_type=task_type,
            todo_reason=TodoReason.FAILED,
            stack_trace=stack_trace,
            status="failed",
        )

    @classmethod
    def create_norun_task(
        cls,
        task_id: str,
        batch_id: str,
        task_params: Dict[str, Any],
        task_type: str,
    ) -> "TodoTask":
        """创建未运行的待处理任务实例

        Args:
            task_id: 任务ID
            batch_id: 批次ID
            task_params: 任务参数
            task_type: 任务类型

        Returns:
            TodoTask: 未运行的待处理任务实例
        """
        return cls(
            task_id=task_id,
            batch_id=batch_id,
            record_time=datetime.now().isoformat(),
            task_params=task_params,
            error_msg="",
            task_type=task_type,
            todo_reason=TodoReason.NO_RUN,
            stack_trace="",
            status="pending",
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于存储和CSV写入

        Returns:
            Dict[str, Any]: 字典格式的待处理任务信息
        """
        return {
            "task_id": self.task_id,
            "batch_id": self.batch_id,
            "record_time": self.record_time,
            "task_params": str(self.task_params),
            "error_msg": self.error_msg,
            "task_type": self.task_type,
            "todo_reason": self.todo_reason,
            "status": self.status,
            "stack_trace": self.stack_trace,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoTask":
        """从字典创建实例

        Args:
            data: 字典格式的待处理任务信息

        Returns:
            TodoTask: 待处理任务实例
        """
        # 将字符串形式的task_params转换回字典
        try:
            task_params = eval(data["task_params"])
        except Exception:
            task_params = data["task_params"]

        # 检查错误信息
        error_msg = data.get("error_msg", data.get("error", ""))

        return cls(
            task_id=data["task_id"],
            batch_id=data["batch_id"],
            record_time=data.get(
                "record_time", data.get("timestamp", datetime.now().isoformat())
            ),
            task_params=task_params,
            error_msg=error_msg,
            task_type=data["task_type"],
            todo_reason=data.get(
                "todo_reason", TodoReason.FAILED if error_msg else TodoReason.NO_RUN
            ),
            status=data.get("status", "todo"),
            stack_trace=data.get("stack_trace", ""),
        )

    @classmethod
    def from_task(cls, task, batch_id: str, is_failed: bool = True) -> "TodoTask":
        """从Task对象创建TodoTask实例

        Args:
            task: Task对象
            batch_id: 批次ID
            is_failed: 是否是失败任务，True表示Failed类型，False表示NoRun类型

        Returns:
            TodoTask: 待处理任务实例
        """
        if is_failed:
            return cls(
                task_id=task.task_id,
                batch_id=batch_id,
                record_time=datetime.now().isoformat(),
                task_params=task.params,
                error_msg=task.error or "",
                task_type=task.task_type,
                todo_reason=TodoReason.FAILED,
                status=task.status.value,
                stack_trace="",
            )
        else:
            return cls(
                task_id=task.task_id,
                batch_id=batch_id,
                record_time=datetime.now().isoformat(),
                task_params=task.params,
                error_msg="",
                task_type=task.task_type,
                todo_reason=TodoReason.NO_RUN,
                status="pending",
                stack_trace="",
            )
