#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, TypeVar, Callable
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
import time
import traceback
from tqdm import tqdm

# 将旧的日志导入替换为新的日志模块
from ...logging import get_user_logger, get_system_logger
from ...config import config
from ..task_execution.task import Task, TaskStatus
from ..task_execution.result import Result

from .batch_task import BatchTask
from .batch_status import BatchStatus
from .batch_task_failure_manager import BatchTaskFailureManager
from .batch_task_unfinished_manager import BatchTaskUnfinishedManager

# 创建用户日志和系统日志
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")


class BatchTaskExecutor:
    """批量任务执行器

    负责执行批量任务，管理任务的生命周期和状态转换。
    """

    # 进度条描述的默认值
    DEFAULT_PROGRESS_DESC = "进度"

    def __init__(
        self,
        task_type: str = "default",
        max_workers: int = None,
        task_interval: float = None,
        task_timeout: int = None,
        record_failed: bool = True,
        max_retries: int = None,
        retry_interval: float = None,
        backoff_factor: float = None,
        failed_task_storage_dir: str = None,
        unfinished_task_storage_dir: str = None,
    ):
        """初始化批量任务执行器

        Args:
            task_type: 任务类型，用于区分不同类型的任务
            max_workers: 最大工作线程数，如果为None则从配置文件读取
            task_interval: 任务提交间隔（秒），如果为None则从配置文件读取
            task_timeout: 单个任务超时时间（秒），如果为None则从配置文件读取
            record_failed: 是否记录失败任务，默认为True
            max_retries: 最大重试次数，如果为None则不重试
            retry_interval: 重试间隔（秒），如果为None则使用默认间隔
            backoff_factor: 重试间隔的退避因子，如果为None则使用默认因子
            failed_task_storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录
            unfinished_task_storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录
        """
        config_max_workers = config("infrastructure.process.max_workers")
        if config_max_workers is None:
            raise ValueError(
                "配置文件中未设置最大工作线程数(infrastructure.process.max_workers)"
            )

        config_task_interval = config("infrastructure.process.task_interval")
        if config_task_interval is None:
            raise ValueError(
                "配置文件中未设置任务提交间隔(infrastructure.process.task_interval)"
            )

        config_task_timeout = config("infrastructure.process.task_timeout")
        if config_task_timeout is None:
            raise ValueError(
                "配置文件中未设置任务超时时间(infrastructure.process.task_timeout)"
            )

        # 使用传入的参数覆盖配置文件中的值
        self.max_workers = config_max_workers if max_workers is None else max_workers
        self.task_interval = (
            config_task_interval if task_interval is None else task_interval
        )
        self.task_timeout = (
            config_task_timeout if task_timeout is None else task_timeout
        )
        self.record_failed = record_failed

        # 初始化重试相关参数
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.backoff_factor = backoff_factor

        # 初始化任务类型和管理器
        self.task_type = task_type
        self.failed_task_manager = BatchTaskFailureManager(task_type, storage_dir=failed_task_storage_dir)
        self.unfinished_task_manager = BatchTaskUnfinishedManager(task_type, storage_dir=unfinished_task_storage_dir)

        # 使用系统日志记录初始化信息
        system_logger.info(
            f"初始化批量任务执行器：task_type={self.task_type}, max_workers={self.max_workers}, "
            f"task_interval={self.task_interval}, task_timeout={self.task_timeout}, "
            f"record_failed={self.record_failed}"
        )
        # 使用用户日志记录简明的初始化信息
        user_logger.info(f"批量任务执行器初始化完成：{self.task_type}")

    def _handle_task_result(
        self, batch_task: BatchTask, batch_mode: str, task: Task, result: Result[Any]
    ) -> None:
        """处理任务执行结果

        Args:
            batch_task: 批次任务对象
            batch_mode: 批次模式，可选值为"new"、"resume"和"retry"
            task: 任务对象
            result: 执行结果
        """
        task.result = result
        if result.success:
            batch_task.increment_success_count()
            task.status = TaskStatus.COMPLETED
            system_logger.debug(f"任务执行成功：task_id={task.task_id}")
            # 在retry模式下，成功后从失败列表中删除该任务
            if self.record_failed and batch_mode == "retry":
                self.failed_task_manager.delete_task(task.task_id, batch_task.batch_id)
        else:
            batch_task.increment_failed_count()
            task.status = TaskStatus.FAILED
            task.error = result.error or "未知错误"
            # 失败信息同时记录在系统日志和用户日志中
            system_logger.error(
                f"任务执行失败：task_id={task.task_id}, error={task.error}"
            )
            user_logger.warning(f"任务失败：{task.task_id} - {task.error}")

            if self.record_failed:
                self.failed_task_manager.record_failed_task(
                    task.task_id, task.params, task.error
                )

        # 记录任务状态
        self.unfinished_task_manager.record_task_status(task)

    def _handle_task_error(
        self, batch_task: BatchTask, task: Task, error: Exception, future: Future = None
    ) -> None:
        """处理任务执行异常

        Args:
            batch_task: 批次任务对象
            task: 任务对象
            error: 异常对象
            future: Future对象
        """
        batch_task.increment_failed_count()

        # 根据错误类型设置任务状态和错误信息
        if isinstance(error, TimeoutError):
            error_msg = "任务执行超时"
            task.status = TaskStatus.FAILED
            system_logger.error(f"任务执行超时：task_id={task.task_id}")
            user_logger.warning(f"任务超时：{task.task_id}")
        elif isinstance(error, KeyboardInterrupt):
            error_msg = "任务被中断"
            task.status = TaskStatus.FAILED
            batch_task.set_status(BatchStatus.INTERRUPTED)
            system_logger.warning(f"任务被中断：task_id={task.task_id}")
            user_logger.warning(f"任务被中断：{task.task_id}")
        else:
            error_msg = f"错误：{str(error)}\n堆栈：{traceback.format_exc()}"
            task.status = TaskStatus.FAILED
            # 详细错误信息记录到系统日志，简略信息记录到用户日志
            system_logger.error(
                f"任务执行出错：task_id={task.task_id}, error={error_msg}"
            )
            user_logger.error(f"任务出错：{task.task_id} - {str(error)}")

        task.error = error_msg

        # 记录失败任务到缓存
        if self.record_failed:
            self.failed_task_manager.record_failed_task(
                task.task_id, task.params, error_msg
            )

        # 记录任务状态
        self.unfinished_task_manager.record_task_status(task)

        if future:
            future.cancel()

    def _handle_interruption(
        self, executor: ThreadPoolExecutor, futures: List[Future]
    ) -> None:
        """处理任务中断

        取消所有未完成的任务，关闭线程池。

        Args:
            executor: 线程池执行器
            futures: 待处理的Future对象列表
        """
        for future in futures:
            if not future.done():
                future.cancel()
        executor.shutdown(wait=False)

        # 记录中断信息
        system_logger.warning("批量任务执行被中断，已取消所有未完成的任务")
        user_logger.warning("任务执行被中断")

    def execute_batch_tasks(
        self,
        task_func: Callable[[Dict[str, Any]], T],
        task_params_list: List[Dict[str, Any]] = None,
        task_timeout: float = None,
        task_interval: float = None,
        max_workers: int = None,
        batch_id: str = None,
        task_max_retries: int = None,
        task_retry_interval: float = None,
        backoff_factor: float = None,
        batch_mode: str = "new",
    ) -> BatchTask:
        """执行批量任务

        Args:
            task_func: 任务执行函数
            task_params_list: 任务参数列表
            task_timeout: 单个任务超时时间（秒）
            task_interval: 任务提交间隔（秒）
            max_workers: 最大工作线程数
            batch_id: 批次ID
            task_max_retries: 最大重试次数
            task_retry_interval: 重试间隔（秒）
            backoff_factor: 重试间隔的退避因子
            batch_mode: 批次模式，可选值为"new"、"resume"和"retry"

        Returns:
            BatchTask: 批次任务对象
        """
        # 参数验证
        if batch_mode not in ["new", "resume", "retry"]:
            raise ValueError(f"不支持的批次模式: {batch_mode}，可选值为'new'、'resume'和'retry'")
            
        if task_func is None:
            raise ValueError("必须提供任务执行函数(task_func)")
            
        # 使用实例属性作为默认值
        task_timeout = float(
            self.task_timeout if task_timeout is None else task_timeout
        )
        task_interval = float(
            self.task_interval if task_interval is None else task_interval
        )
        max_workers = int(self.max_workers if max_workers is None else max_workers)
        task_max_retries = (
            self.max_retries if task_max_retries is None else task_max_retries
        )
        task_retry_interval = (
            self.retry_interval if task_retry_interval is None else task_retry_interval
        )
        backoff_factor = (
            self.backoff_factor if backoff_factor is None else backoff_factor
        )

        # 根据batch_mode决定任务列表
        if batch_mode == "resume":
            # 恢复模式：从未完成任务中恢复执行
            if batch_id is None:
                raise ValueError("在恢复模式下，必须提供batch_id")

            # 创建批次任务实例
            batch_task = BatchTask(batch_id, self.task_type)

            # 设置batch_id
            self.unfinished_task_manager.set_batch_id(batch_id)
            self.failed_task_manager.set_batch_id(batch_id)

            # 先加载未完成任务和失败任务
            self.unfinished_task_manager.load_batch_tasks(batch_id)
            self.failed_task_manager.load_batch_tasks(batch_id)

            # 获取未完成的任务
            unfinished_tasks = self.unfinished_task_manager.get_unfinished_tasks(
                batch_id
            )

            # 创建任务对象列表
            tasks = []
            for task_info in unfinished_tasks:
                task = Task(
                    self.task_type,
                    task_info["task_params"],
                    task_func,
                    task_id=task_info["task_id"],
                    max_retries=task_max_retries,
                    retry_interval=task_retry_interval,
                    backoff_factor=backoff_factor,
                )
                task.status = TaskStatus(task_info["status"])
                task.error = task_info["error"]
                tasks.append(task)

            if not tasks:
                system_logger.warning(f"没有找到需要恢复的任务：batch_id={batch_id}")
                user_logger.warning(f"没有找到需要恢复的任务")
                batch_task.set_status(BatchStatus.COMPLETED)
                batch_task.set_end_time()
                return batch_task

        elif batch_mode == "retry":
            # 重试模式：重试失败任务
            if batch_id is None:
                raise ValueError("在重试模式下，必须提供batch_id")

            # 创建批次任务实例
            batch_task = BatchTask(batch_id, self.task_type)

            # 设置batch_id
            self.failed_task_manager.set_batch_id(batch_id)
            self.unfinished_task_manager.set_batch_id(batch_id)

            # 先加载失败任务
            self.failed_task_manager.load_batch_tasks(batch_id)

            # 获取失败任务
            failed_tasks = self.failed_task_manager.get_failed_tasks(batch_id)

            # 创建任务对象列表
            tasks = []
            for task_info in failed_tasks:
                task = Task(
                    self.task_type,
                    task_info["task_params"],
                    task_func,
                    task_id=task_info["task_id"],
                    max_retries=task_max_retries,
                    retry_interval=task_retry_interval,
                    backoff_factor=backoff_factor,
                )
                tasks.append(task)

            if not tasks:
                system_logger.warning(
                    f"没有找到需要重试的失败任务：batch_id={batch_id}"
                )
                user_logger.warning(f"没有找到需要重试的失败任务")
                batch_task.set_status(BatchStatus.COMPLETED)
                batch_task.set_end_time()
                return batch_task
        else:
            # 新建模式：执行新的批次任务
            # 如果没有提供batch_id，则生成新的
            if not batch_id:
                batch_id = f"{int(time.time())}"

            # 创建批次任务实例
            batch_task = BatchTask(batch_id, self.task_type)

            # 设置批次ID
            self.failed_task_manager.set_batch_id(batch_id)
            self.unfinished_task_manager.set_batch_id(batch_id)

            # 将任务参数列表转换为Task对象列表
            if task_params_list:
                tasks = [
                    Task(
                        self.task_type,
                        params,
                        task_func,
                        max_retries=task_max_retries,
                        retry_interval=task_retry_interval,
                        backoff_factor=backoff_factor,
                    )
                    for params in task_params_list
                ]
            else:
                tasks = [
                    Task(
                        self.task_type,
                        {},
                        task_func,
                        max_retries=task_max_retries,
                        retry_interval=task_retry_interval,
                        backoff_factor=backoff_factor,
                    )
                ]

        batch_task.set_total_count(len(tasks))
        batch_task.start()

        # 使用系统日志记录详细信息，用户日志记录关键信息
        system_logger.info(
            f"开始执行批量任务：batch_id={batch_id}, total={batch_task.total_count}, "
            f"task_timeout={task_timeout}秒, batch_mode={batch_mode}, "
            f"max_workers={max_workers}, task_interval={task_interval}"
        )
        user_logger.info(
            f"开始执行批量任务：共{batch_task.total_count}个任务，模式：{batch_mode}"
        )

        executor = None
        task_error_occurred = False
        futures = []

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []

                # 使用tqdm显示总体进度
                with tqdm(total=len(tasks), desc=self.DEFAULT_PROGRESS_DESC) as pbar:
                    # 先记录所有任务的初始状态
                    for task in tasks:
                        if task.status != TaskStatus.COMPLETED:  # 跳过已完成的任务
                            task.status = TaskStatus.PENDING
                            self.unfinished_task_manager.record_task_status(task)

                    # 提交所有任务到线程池
                    for task in tasks:
                        future = executor.submit(task.execute)
                        futures.append((future, task))

                    # 等待所有任务完成
                    for future, task in futures:
                        try:
                            result = future.result(timeout=task_timeout)
                            self._handle_task_result(
                                batch_task, batch_mode, task, result
                            )
                        except TimeoutError:
                            self._handle_task_error(
                                batch_task, task, TimeoutError("任务执行超时"), future
                            )
                            batch_task.set_status(BatchStatus.FAILED)
                            task_error_occurred = True
                        except KeyboardInterrupt as e:
                            self._handle_task_error(batch_task, task, e, future)
                            self._handle_interruption(executor, [f for f, _ in futures])
                            batch_task.set_status(BatchStatus.INTERRUPTED)
                            batch_task.set_end_time()
                            system_logger.warning(
                                f"用户中断任务执行：batch_id={batch_id}"
                            )
                            user_logger.warning("任务执行已被中断")
                            raise  # 重新抛出KeyboardInterrupt以进入外层异常处理
                        except Exception as e:
                            self._handle_task_error(batch_task, task, e, future)
                            batch_task.set_status(BatchStatus.FAILED)
                            task_error_occurred = True
                        finally:
                            pbar.update(1)
                            if task_interval > 0:
                                time.sleep(task_interval)

            # 正常结束批次任务处理
            # 设置批次任务的执行状态
            if batch_task.failed_count > 0:
                if batch_task.failed_count < batch_task.total_count:
                    batch_task.set_status(BatchStatus.PARTIALLY_COMPLETED)
                    status_msg = "部分完成"
                else:
                    batch_task.set_status(BatchStatus.FAILED)
                    status_msg = "全部失败"
            else:
                batch_task.set_status(BatchStatus.COMPLETED)
                status_msg = "全部完成"

            batch_task.set_end_time()

            # 记录批量任务的执行结果
            elapsed_time = batch_task.end_time - batch_task.start_time
            result_msg = (
                f"批量任务执行结束：batch_id={batch_id}, "
                f"状态={batch_task.status.value}, "
                f"总数={batch_task.total_count}, "
                f"成功={batch_task.success_count}, "
                f"失败={batch_task.failed_count}, "
                f"耗时={elapsed_time:.2f}秒"
            )
            system_logger.info(result_msg)

            # 用户日志显示更加简洁的结果
            user_result_msg = (
                f"批量任务执行结束：{status_msg}, "
                f"总数：{batch_task.total_count}, "
                f"成功：{batch_task.success_count}, "
                f"失败：{batch_task.failed_count}, "
                f"耗时：{elapsed_time:.2f}秒"
            )
            user_logger.info(user_result_msg)

        except KeyboardInterrupt:
            batch_task.set_status(BatchStatus.INTERRUPTED)
            batch_task.set_end_time()
            system_logger.warning(f"批量任务被中断：batch_id={batch_id}")
            user_logger.warning("批量任务被中断")
            # 确保取消所有未完成的任务并关闭线程池
            if executor is not None and not executor._shutdown:
                # 过滤出未完成的future
                pending_futures = [f for f, _ in futures if not f.done()]
                if pending_futures:
                    system_logger.debug(f"正在取消{len(pending_futures)}个未完成的任务")
                    self._handle_interruption(executor, pending_futures)

        except Exception as e:
            batch_task.set_status(BatchStatus.FAILED)
            batch_task.set_end_time()
            error_msg = (
                f"批量任务执行过程中发生错误：{str(e)}\n{traceback.format_exc()}"
            )
            system_logger.error(error_msg)
            user_logger.error(f"批量任务执行失败：{str(e)}")

        finally:
            # 无论如何都要确保保存任务状态
            if batch_id:
                try:
                    self.unfinished_task_manager.flush_batch_tasks(batch_id)
                    self.failed_task_manager.flush_batch_tasks(batch_id)
                    system_logger.debug(f"成功保存任务状态：batch_id={batch_id}")
                except Exception as flush_error:
                    system_logger.error(f"保存任务状态失败：{str(flush_error)}")
                    user_logger.error("保存任务状态失败")

        return batch_task
