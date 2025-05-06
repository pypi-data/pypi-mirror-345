#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional, Callable, TypeVar
import time
import os
from uuid import uuid4
import copy

# 跨模块的导入使用绝对导入，从顶层模块导入
from datawhale.graph import Graph, NamespaceRegistry
from datawhale.tasks import execute_batch_tasks, BatchTask
from datawhale.logging import get_user_logger, get_system_logger

# 创建用户和系统日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")


class StageStatus:
    """阶段执行状态常量"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    PARTIAL = "partial"  # 部分完成（有些任务失败）


class Stage:
    """任务阶段对象

    管理一个Graph的多次执行，每次执行使用不同的启动参数。

    属性:
        name: 阶段名称
        graph: 要执行的任务图
        params_list: 参数列表，每个元素是一个字典，用作graph执行时的start_params
        status: 阶段的当前执行状态
        cache_registry: 是否缓存每次执行的注册表
        registries: 保存每次执行后的注册表副本列表
    """

    def __init__(
        self,
        name: str,
        graph: Graph,
        params_list: List[Dict[str, Any]],
        runtime_dir: str = None,
        cache_registry: bool = False,
    ):
        """初始化阶段对象

        Args:
            name: 阶段名称
            graph: 要执行的任务图
            params_list: 参数列表，每个元素是一个字典，用作graph执行时的start_params
            runtime_dir: 运行时文件目录，如果为None则在当前工作目录创建
            cache_registry: 是否缓存每次执行的注册表，默认为False
        """
        self.stage_id = f"stage_{name}_{uuid4().hex[:8]}"
        self.name = name
        self.graph = graph
        self.params_list = params_list
        self.status = StageStatus.PENDING
        self.create_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.cache_registry = cache_registry
        self.registries: List[NamespaceRegistry] = []

        # 设置运行时目录
        if runtime_dir is None:
            self.runtime_dir = os.path.join(
                os.getcwd(), f"stage_runtime_{self.stage_id}"
            )
        else:
            self.runtime_dir = runtime_dir

        # 创建运行时目录结构
        os.makedirs(self.runtime_dir, exist_ok=True)

        # 创建失败任务和未完成任务的存储目录
        self.failed_tasks_dir = os.path.join(self.runtime_dir, "failed_tasks")
        self.unfinished_tasks_dir = os.path.join(self.runtime_dir, "unfinished_tasks")
        os.makedirs(self.failed_tasks_dir, exist_ok=True)
        os.makedirs(self.unfinished_tasks_dir, exist_ok=True)

        system_logger.debug(
            f"[Stage][{self.stage_id}]：创建任务阶段，name={self.name}，params数量={len(self.params_list)}，runtime_dir={self.runtime_dir}，cache_registry={self.cache_registry}"
        )

    def execute(
        self,
        max_workers: int = None,
        task_timeout: float = None,
        task_interval: float = None,
        task_max_retries: int = None,
        task_retry_interval: float = None,
        backoff_factor: float = None,
        record_failed: bool = True,
    ) -> BatchTask:
        """执行阶段中的所有任务

        使用execute_new_batch_tasks批量执行图，每个任务使用params_list中的一个参数集。

        Args:
            max_workers: 最大并行执行的工作线程数
            task_timeout: 每个任务的超时时间（秒）
            task_interval: 任务间隔时间（秒）
            task_max_retries: 任务最大重试次数
            task_retry_interval: 任务重试间隔时间（秒）
            backoff_factor: 重试退避因子
            record_failed: 是否记录失败的任务

        Returns:
            BatchTask: 批次任务对象
        """
        # 记录执行开始时间
        self.start_time = time.time()
        self.status = StageStatus.RUNNING
        batch_task = None

        system_logger.info(
            f"[Stage][{self.stage_id}]：开始执行阶段，name={self.name}，任务数量={len(self.params_list)}"
        )

        try:
            # 定义单个任务执行函数
            def execute_graph_task(params: Dict[str, Any]) -> Dict[str, Any]:
                # 重置图状态，以便可以重新执行
                self.graph.reset()
                # 执行图并返回结果
                result = self.graph.execute(start_params=params)

                # 如果启用了registry缓存，则保存注册表的深拷贝
                if self.cache_registry:
                    try:
                        registry_copy = copy.deepcopy(self.graph.namespace_registry)
                        self.registries.append(registry_copy)
                        system_logger.debug(
                            f"[Stage][{self.stage_id}]：缓存了图 {self.graph.graph_id} 的注册表"
                        )
                    except Exception as e:
                        system_logger.error(
                            f"[Stage][{self.stage_id}]：无法缓存图 {self.graph.graph_id} 的注册表: {str(e)}"
                        )

                return {
                    "graph_id": self.graph.graph_id,
                    "graph_name": self.graph.name,
                    "status": self.graph.status,
                    "params": params,
                    "nodes_status": result,
                    "start_time": self.graph.start_time,
                    "end_time": self.graph.end_time,
                }

            # 使用execute_batch_tasks执行批量任务
            batch_task = execute_batch_tasks(
                task_func=execute_graph_task,
                task_params_list=[{"params": params} for params in self.params_list],
                batch_id=self.stage_id,
                task_type=f"stage_{self.name}",
                max_workers=max_workers,
                task_timeout=task_timeout,
                task_interval=task_interval,
                task_max_retries=task_max_retries,
                task_retry_interval=task_retry_interval,
                backoff_factor=backoff_factor,
                record_failed=record_failed,
                failed_task_storage_dir=self.failed_tasks_dir,
                unfinished_task_storage_dir=self.unfinished_tasks_dir,
                batch_mode="new",
            )

            # 直接使用batch_task中的结果统计，无需调用wait()

            # 设置阶段的最终状态
            if batch_task.failed_count == 0:
                self.status = StageStatus.COMPLETED
            elif batch_task.success_count == 0:
                self.status = StageStatus.FAILED
            else:
                self.status = StageStatus.PARTIAL

        except Exception as e:
            self.status = StageStatus.FAILED
            system_logger.error(
                f"[Stage][{self.stage_id}]：执行阶段失败，name={self.name}，error={str(e)}"
            )
            raise

        finally:
            # 记录执行结束时间
            self.end_time = time.time()
            elapsed_time = self.end_time - self.start_time

            if batch_task:
                success_count = batch_task.success_count
                failed_count = batch_task.failed_count
            else:
                success_count = 0
                failed_count = len(self.params_list)

            system_logger.info(
                f"[Stage][{self.stage_id}]：执行完成，name={self.name}，"
                f"总任务={len(self.params_list)}，成功={success_count}，"
                f"失败={failed_count}，"
                f"状态={self.status}，耗时={elapsed_time:.3f}秒，"
                f"缓存的注册表数量={len(self.registries)}"
            )

        return batch_task

    def __str__(self) -> str:
        """返回阶段的字符串表示

        Returns:
            阶段的字符串表示
        """
        return f"Stage(id={self.stage_id}, name={self.name}, tasks={len(self.params_list)})"

    def __repr__(self) -> str:
        """返回阶段的详细字符串表示

        Returns:
            阶段的详细字符串表示
        """
        return f"Stage(id={self.stage_id}, name={self.name}, tasks={len(self.params_list)}, status={self.status})"
