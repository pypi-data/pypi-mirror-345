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


class BatchTaskFailureManager:
    """批量任务失败管理器

    负责管理批量任务中失败的子任务，包括记录和管理功能。
    """

    # 设置默认的存储目录
    DEFAULT_STORAGE_DIR = "failed_tasks"

    def __init__(self, task_type: str = "default", storage_dir: str = None):
        """初始化失败任务管理器

        Args:
            task_type: 任务类型，用于区分不同类型的任务
            storage_dir: 存储目录，如果为None则使用默认目录
        """
        self.task_type = task_type
        self._init_storage_params(storage_dir)
        self.current_batch_id = None
        self._failed_tasks = {}  # {batch_id: {task_id: TodoTask}}
        self._cache_dirty = {}  # 记录缓存是否被修改

        # 只需向用户记录失败管理器的初始化
        user_logger.info(f"初始化{self.task_type}类型的失败任务管理器")

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
                f"初始化失败任务管理器：task_type={self.task_type}, storage_dir={self.storage_dir}"
            )
        except OSError as e:
            system_logger.error(f"创建失败任务存储目录失败: {str(e)}")
            user_logger.error(f"无法创建失败任务存储目录: {str(e)}")
            raise

    def _get_batch_file_path(self, batch_id: str) -> Path:
        """获取指定批次的文件路径

        Args:
            batch_id: 批次ID

        Returns:
            Path: 文件路径
        """
        return Path(self.storage_dir) / f"{self.task_type}_{batch_id}_failed_tasks.csv"

    def set_batch_id(self, batch_id: str) -> None:
        """设置当前批次ID

        Args:
            batch_id: 批次ID
        """
        self.current_batch_id = batch_id
        if batch_id not in self._failed_tasks:
            self._failed_tasks[batch_id] = {}
            self._cache_dirty[batch_id] = False

        system_logger.info(f"设置当前批次ID：batch_id={batch_id}")

    def flush_batch_tasks(self, batch_id: str) -> None:
        """将内存缓存中的指定批次任务保存到文件

        Args:
            batch_id: 批次ID

        Raises:
            ValueError: 当批次不存在于缓存中时抛出
        """
        if batch_id not in self._failed_tasks:
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
                for task in self._failed_tasks[batch_id].values():
                    writer.writerow(task.to_dict())

            self._cache_dirty[batch_id] = False

            failed_count = len(self._failed_tasks[batch_id])
            system_logger.info(
                f"将批次任务从缓存写入文件：batch_id={batch_id}, 失败任务数={failed_count}"
            )

            # 只有当有失败任务时才通知用户
            if failed_count > 0:
                user_logger.info(f"已保存{failed_count}个失败任务的记录")
        except Exception as e:
            system_logger.error(
                f"保存失败任务到文件时出错: {str(e)}, 文件路径: {file_path}"
            )
            user_logger.error("保存失败任务记录时出错，请检查文件权限")
            raise

    def load_batch_tasks(self, batch_id: str) -> None:
        """从文件加载指定批次的任务到内存缓存

        Args:
            batch_id: 批次ID
        """
        file_path = self._get_batch_file_path(batch_id)
        self._failed_tasks[batch_id] = {}

        if not file_path.exists():
            system_logger.debug(f"失败任务文件不存在: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    task_id = row["task_id"]
                    # 转换为TodoTask对象
                    self._failed_tasks[batch_id][task_id] = TodoTask.from_dict(row)

            self._cache_dirty[batch_id] = False

            failed_count = len(self._failed_tasks[batch_id])
            system_logger.info(
                f"从文件加载批次任务到缓存：batch_id={batch_id}, 失败任务数={failed_count}"
            )

            # 只有当有失败任务时才通知用户
            if failed_count > 0:
                user_logger.info(f"已加载{failed_count}个失败任务的记录")
        except Exception as e:
            system_logger.error(f"加载失败任务时出错: {str(e)}, 文件路径: {file_path}")
            user_logger.warning("加载失败任务记录时出错，将使用空记录")

    def record_failed_task(self, task: Task) -> None:
        """记录任务失败

        Args:
            task: 任务对象

        Raises:
            ValueError: 当未设置batch_id时抛出
        """
        if self.current_batch_id is None:
            error_msg = "未设置batch_id，请先调用set_batch_id方法设置当前批次ID"
            system_logger.error(error_msg)
            raise ValueError(error_msg)

        # 确保当前批次的失败任务字典存在
        if self.current_batch_id not in self._failed_tasks:
            self._failed_tasks[self.current_batch_id] = {}

        # 只记录状态为失败的任务
        if task.status != TaskStatus.FAILED:
            system_logger.debug(
                f"跳过非失败任务：task_id={task.task_id}, status={task.status.value}"
            )
            return

        # 创建TodoTask对象
        todo_task = TodoTask.create_failed_task(
            task_id=task.task_id,
            batch_id=self.current_batch_id,
            task_params=task.params,
            error_msg=task.error or "",
            task_type=self.task_type,
            stack_trace="",
        )

        # 记录失败任务
        self._failed_tasks[self.current_batch_id][task.task_id] = todo_task
        self._cache_dirty[self.current_batch_id] = True

        # 记录到系统日志
        system_logger.info(f"记录任务失败：task_id={task.task_id}, error={task.error}")

        # 记录到用户日志，但使用更简洁的信息
        error_msg = task.error or "未知错误"
        if len(error_msg) > 100:
            error_msg = error_msg[:97] + "..."
        user_logger.warning(f"任务失败：{error_msg}")

    def get_failed_tasks(self, batch_id: str = None) -> List[TodoTask]:
        """获取失败的任务列表

        Args:
            batch_id: 批次ID，如果为None则返回当前批次的失败任务

        Returns:
            List[TodoTask]: 失败的任务列表
        """
        if batch_id is None:
            batch_id = self.current_batch_id
            if batch_id is None:
                system_logger.debug("获取失败任务列表：未指定批次ID且当前批次ID为None")
                return []

        if batch_id not in self._failed_tasks:
            system_logger.debug(f"获取失败任务列表：批次{batch_id}不存在于缓存中")
            return []

        failed_tasks = list(self._failed_tasks[batch_id].values())
        system_logger.debug(
            f"获取失败任务列表：batch_id={batch_id}, count={len(failed_tasks)}"
        )
        return failed_tasks

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

        if batch_id in self._failed_tasks and task_id in self._failed_tasks[batch_id]:
            del self._failed_tasks[batch_id][task_id]
            self._cache_dirty[batch_id] = True

            system_logger.info(f"删除任务记录：task_id={task_id}, batch_id={batch_id}")
            user_logger.debug(f"已删除失败任务记录：{task_id}")
        else:
            system_logger.warning(
                f"要删除的任务记录不存在：task_id={task_id}, batch_id={batch_id}"
            )

    def get_failure_stats(self, batch_id: str = None) -> Dict[str, Any]:
        """获取失败任务统计信息

        Args:
            batch_id: 批次ID，如果为None则使用当前批次ID

        Returns:
            Dict[str, Any]: 失败统计信息，包括总数、最早/最晚失败时间等
        """
        if batch_id is None:
            batch_id = self.current_batch_id
            if batch_id is None:
                return {"count": 0}

        if batch_id not in self._failed_tasks:
            return {"count": 0}

        failed_tasks = self._failed_tasks[batch_id].values()
        if not failed_tasks:
            return {"count": 0}

        # 统计失败信息
        count = len(failed_tasks)

        # 获取时间戳
        timestamps = []
        for task in failed_tasks:
            try:
                # 从record_time解析时间戳
                dt = datetime.fromisoformat(task.record_time)
                timestamps.append(dt.timestamp())
            except (ValueError, AttributeError):
                pass

        earliest = min(timestamps) if timestamps else 0
        latest = max(timestamps) if timestamps else 0

        # 统计错误类型
        error_types = {}
        for task in failed_tasks:
            error = task.error_msg

            # 简化错误消息用于分类
            error_type = error.split(":", 1)[0] if ":" in error else error[:20]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        stats = {
            "count": count,
            "earliest_failure": earliest,
            "latest_failure": latest,
            "error_types": error_types,
        }

        system_logger.debug(f"获取失败统计：batch_id={batch_id}, stats={stats}")
        return stats
