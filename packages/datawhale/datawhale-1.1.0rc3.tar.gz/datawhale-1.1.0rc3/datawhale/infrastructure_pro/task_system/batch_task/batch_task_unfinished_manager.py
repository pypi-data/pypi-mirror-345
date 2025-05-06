#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any
import time
import csv
import os
from pathlib import Path
from ...logging import get_system_logger, get_user_logger
from ..task_execution.task import Task, TaskStatus
from .todo_task import TodoTask, TodoReason
from datetime import datetime

# 创建系统和用户日志记录器
system_logger = get_system_logger(__name__)
user_logger = get_user_logger(__name__)


class BatchTaskUnfinishedManager:
    """批量任务未完成管理器

    负责管理批量任务中未完成的子任务，包括记录和管理功能。
    """

    # 设置默认的存储目录
    DEFAULT_STORAGE_DIR = "unfinished_tasks"

    def __init__(self, task_type: str = "default", storage_dir: str = None):
        """初始化未完成任务管理器

        Args:
            task_type: 任务类型，用于区分不同类型的任务
            storage_dir: 存储目录，如果为None则使用默认目录
        """
        self.task_type = task_type
        self._init_storage_params(storage_dir)
        self.current_batch_id = None
        self._unfinished_tasks = {}  # {batch_id: {task_id: TodoTask}}
        self._cache_dirty = {}  # 记录缓存是否被修改

        # 向用户记录初始化信息
        user_logger.info(f"初始化{self.task_type}类型的任务恢复管理器")

    def _init_storage_params(self, storage_dir: str = None) -> None:
        """初始化存储参数

        Args:
            storage_dir: 存储目录

        Raises:
            ValueError: 当必要的存储目录未设置时抛出
        """
        # 使用提供的存储目录或默认目录
        self.storage_dir = storage_dir or self.DEFAULT_STORAGE_DIR

        # 确保存储目录存在
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            system_logger.info(
                f"初始化任务恢复管理器：task_type={self.task_type}, storage_dir={self.storage_dir}"
            )
        except OSError as e:
            system_logger.error(f"创建恢复任务存储目录失败: {str(e)}")
            user_logger.error(f"无法创建任务恢复目录: {str(e)}")
            raise

    def _get_batch_file_path(self, batch_id: str) -> Path:
        """获取指定批次的文件路径

        Args:
            batch_id: 批次ID

        Returns:
            Path: 文件路径
        """
        return (
            Path(self.storage_dir) / f"{self.task_type}_{batch_id}_recovery_tasks.csv"
        )

    def set_batch_id(self, batch_id: str) -> None:
        """设置当前批次ID

        Args:
            batch_id: 批次ID
        """
        self.current_batch_id = batch_id
        if batch_id not in self._unfinished_tasks:
            self._unfinished_tasks[batch_id] = {}
            self._cache_dirty[batch_id] = False

        system_logger.info(f"设置当前批次ID：batch_id={batch_id}")

    def flush_batch_tasks(self, batch_id: str) -> None:
        """将内存缓存中的指定批次任务保存到文件

        Args:
            batch_id: 批次ID

        Raises:
            ValueError: 当批次不存在于缓存中时抛出
        """
        if batch_id not in self._unfinished_tasks:
            error_msg = f"批次{batch_id}不存在于缓存中"
            system_logger.error(error_msg)
            raise ValueError(error_msg)

        fieldnames = [
            "task_id",
            "batch_id",
            "task_type",
            "task_params",
            "status",
            "record_time",
            "error_msg",
            "todo_reason",
            "stack_trace",
        ]

        file_path = self._get_batch_file_path(batch_id)

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for task in self._unfinished_tasks[batch_id].values():
                    writer.writerow(task.to_dict())

            self._cache_dirty[batch_id] = False

            unfinished_count = len(self._unfinished_tasks[batch_id])
            system_logger.info(
                f"将批次任务从缓存写入文件：batch_id={batch_id}, 未完成任务数={unfinished_count}"
            )

            # 只有当有未完成任务时才通知用户
            if unfinished_count > 0:
                user_logger.info(f"已保存{unfinished_count}个未完成任务的状态")
        except Exception as e:
            system_logger.error(
                f"保存未完成任务到文件时出错: {str(e)}, 文件路径: {file_path}"
            )
            user_logger.error("保存任务状态时出错，请检查文件权限")
            raise

    def load_batch_tasks(self, batch_id: str) -> None:
        """从文件加载指定批次的任务到内存缓存

        Args:
            batch_id: 批次ID
        """
        file_path = self._get_batch_file_path(batch_id)
        self._unfinished_tasks[batch_id] = {}

        if not file_path.exists():
            system_logger.debug(f"未完成任务文件不存在: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    task_id = row["task_id"]
                    # 转换为TodoTask对象
                    self._unfinished_tasks[batch_id][task_id] = TodoTask.from_dict(row)

            self._cache_dirty[batch_id] = False

            unfinished_count = len(self._unfinished_tasks[batch_id])
            system_logger.info(
                f"从文件加载批次任务到缓存：batch_id={batch_id}, 未完成任务数={unfinished_count}"
            )

            # 只有当有未完成任务时才通知用户
            if unfinished_count > 0:
                user_logger.info(f"已加载{unfinished_count}个未完成任务的状态")

                # 提供任务状态分布信息
                status_counts = {}
                for task in self._unfinished_tasks[batch_id].values():
                    status = task.status
                    status_counts[status] = status_counts.get(status, 0) + 1

                status_info = ", ".join(
                    [f"{status}: {count}" for status, count in status_counts.items()]
                )
                system_logger.info(f"任务状态分布：{status_info}")
        except Exception as e:
            system_logger.error(
                f"加载未完成任务时出错: {str(e)}, 文件路径: {file_path}"
            )
            user_logger.warning("加载任务状态时出错，将使用空记录")

    def record_task_status(self, task: Task) -> None:
        """记录任务状态

        Args:
            task: 任务对象

        Raises:
            ValueError: 当未设置batch_id时抛出
        """
        if self.current_batch_id is None:
            error_msg = "未设置batch_id，请先调用set_batch_id方法设置当前批次ID"
            system_logger.error(error_msg)
            raise ValueError(error_msg)

        # 确保当前批次的未完成任务字典存在
        if self.current_batch_id not in self._unfinished_tasks:
            self._unfinished_tasks[self.current_batch_id] = {}

        # 如果任务已完成，从未完成任务中删除
        if task.status == TaskStatus.COMPLETED:
            if task.task_id in self._unfinished_tasks[self.current_batch_id]:
                del self._unfinished_tasks[self.current_batch_id][task.task_id]
                self._cache_dirty[self.current_batch_id] = True
                system_logger.debug(
                    f"任务已完成，从未完成任务中删除：task_id={task.task_id}"
                )
            return

        # 创建TodoTask对象（使用NoRun类型）
        todo_task = TodoTask.create_norun_task(
            task_id=task.task_id,
            batch_id=self.current_batch_id,
            task_params=task.params,
            task_type=self.task_type,
        )

        # 如果有错误信息，则添加到todo_task中
        if task.error:
            todo_task.error_msg = task.error

        # 根据任务状态设置todo_task的状态
        todo_task.status = task.status.value

        # 记录未完成任务状态
        self._unfinished_tasks[self.current_batch_id][task.task_id] = todo_task
        self._cache_dirty[self.current_batch_id] = True

        # 系统日志记录详细任务状态
        system_logger.debug(
            f"记录任务状态：task_id={task.task_id}, status={task.status.value}"
        )

        # 只有在任务失败时才在用户日志中记录
        if task.status == TaskStatus.FAILED and task.error:
            error_msg = task.error
            if len(error_msg) > 100:
                error_msg = error_msg[:97] + "..."
            user_logger.debug(f"标记未完成任务：{error_msg}")

    def get_unfinished_tasks(self, batch_id: str = None) -> List[TodoTask]:
        """获取未完成的任务列表

        Args:
            batch_id: 批次ID，如果为None则返回当前批次的未完成任务

        Returns:
            List[TodoTask]: 未完成的任务列表
        """
        if batch_id is None:
            batch_id = self.current_batch_id
            if batch_id is None:
                system_logger.debug(
                    "获取未完成任务列表：未指定批次ID且当前批次ID为None"
                )
                return []

        if batch_id not in self._unfinished_tasks:
            system_logger.debug(f"获取未完成任务列表：批次{batch_id}不存在于缓存中")
            return []

        unfinished_tasks = list(self._unfinished_tasks[batch_id].values())
        system_logger.debug(
            f"获取未完成任务列表：batch_id={batch_id}, count={len(unfinished_tasks)}"
        )

        # 任务数量较多时向用户提供简要信息
        if len(unfinished_tasks) > 10:
            user_logger.info(f"找到{len(unfinished_tasks)}个未完成任务需要处理")

        return unfinished_tasks

    def delete_task(self, task_id: str, batch_id: str = None) -> None:
        """删除指定的任务记录

        Args:
            task_id: 任务ID
            batch_id: 批次ID，如果为None则使用当前批次ID

        Raises:
            ValueError: 当batch_id为None且当前批次ID也为None时抛出
        """
        if batch_id is None:
            batch_id = self.current_batch_id
            if batch_id is None:
                error_msg = "必须指定batch_id或设置当前批次ID"
                system_logger.error(error_msg)
                raise ValueError(error_msg)

        if (
            batch_id in self._unfinished_tasks
            and task_id in self._unfinished_tasks[batch_id]
        ):
            del self._unfinished_tasks[batch_id][task_id]
            self._cache_dirty[batch_id] = True

            system_logger.info(f"删除任务记录：task_id={task_id}, batch_id={batch_id}")
            user_logger.debug(f"已删除未完成任务记录：{task_id}")
        else:
            system_logger.warning(
                f"要删除的任务记录不存在：task_id={task_id}, batch_id={batch_id}"
            )

    def get_task_counts_by_status(self, batch_id: str = None) -> Dict[str, int]:
        """获取各状态的任务数量

        Args:
            batch_id: 批次ID，如果为None则使用当前批次ID

        Returns:
            Dict[str, int]: 各状态的任务数量
        """
        if batch_id is None:
            batch_id = self.current_batch_id
            if batch_id is None:
                return {}

        if batch_id not in self._unfinished_tasks:
            return {}

        # 统计各状态任务数量
        status_counts = {}
        for task in self._unfinished_tasks[batch_id].values():
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1

        system_logger.debug(
            f"任务状态统计：batch_id={batch_id}, counts={status_counts}"
        )
        return status_counts

    def is_batch_recoverable(self, batch_id: str) -> bool:
        """检查批次是否可恢复

        Args:
            batch_id: 批次ID

        Returns:
            bool: 如果批次有未完成任务且可以恢复则返回True
        """
        if not batch_id:
            return False

        # 检查文件是否存在
        file_path = self._get_batch_file_path(batch_id)
        if not file_path.exists():
            system_logger.debug(f"批次不可恢复：文件不存在 {file_path}")
            return False

        # 尝试加载任务
        try:
            self.load_batch_tasks(batch_id)
            has_tasks = len(self._unfinished_tasks.get(batch_id, {})) > 0

            if has_tasks:
                system_logger.info(
                    f"批次可恢复：batch_id={batch_id}, 未完成任务数={len(self._unfinished_tasks[batch_id])}"
                )
                return True
            else:
                system_logger.debug(f"批次不可恢复：无未完成任务 batch_id={batch_id}")
                return False
        except Exception as e:
            system_logger.error(f"检查批次可恢复性时出错：{str(e)}")
            return False
