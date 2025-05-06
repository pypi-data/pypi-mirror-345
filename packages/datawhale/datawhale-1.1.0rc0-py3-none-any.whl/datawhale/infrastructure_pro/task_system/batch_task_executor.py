#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, TypeVar, Callable, Literal, Optional, Union
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    Future,
    TimeoutError,
)
import time
import traceback
import multiprocessing
from tqdm import tqdm

# 跨模块的导入使用绝对导入，优先从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger

# 从task_execution模块导入
from .task_execution.task import Task, TaskStatus
from .task_execution.result import Result

# 从batch_task模块导入
from .batch_task.batch_task import BatchTask
from .batch_task.batch_status import BatchStatus
from .batch_task.batch_task_failure_manager import BatchTaskFailureManager
from .batch_task.batch_task_unfinished_manager import BatchTaskUnfinishedManager

# 创建用户日志和系统日志
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")

# 定义执行模式类型
ExecutionMode = Literal["thread", "process"]


class BatchTaskExecutor:
    """批量任务执行器

    负责执行批量任务，管理任务的生命周期和状态转换。
    支持多线程和多进程两种执行模式。
    """

    # 进度条描述的默认值
    DEFAULT_PROGRESS_DESC = "进度"

    def __init__(
        self,
        task_type: str = "default",
        max_workers: int = None,  # 默认值为None，将根据CPU核心数自动设置
        task_interval: float = 0,  # 默认值
        task_timeout: int = 300,  # 默认值
        record_failed: bool = True,
        max_retries: int = None,
        retry_interval: float = None,
        backoff_factor: float = None,
        failed_task_storage_dir: str = None,
        unfinished_task_storage_dir: str = None,
        execution_mode: ExecutionMode = "thread",  # 默认使用线程模式
        process_initialization_timeout: int = 60,  # 进程初始化超时时间（秒）
        show_progress: bool = True,  # 是否显示进度条
    ):
        """初始化批量任务执行器

        Args:
            task_type: 任务类型，用于区分不同类型的任务
            max_workers: 最大工作线程/进程数，默认为None（将根据CPU核心数自动设置）
            task_interval: 任务提交间隔（秒），默认为0（无间隔）
            task_timeout: 单个任务超时时间（秒），默认为300秒（5分钟）
            record_failed: 是否记录失败任务，默认为True
            max_retries: 最大重试次数，如果为None则不重试
            retry_interval: 重试间隔（秒），如果为None则使用默认间隔
            backoff_factor: 重试间隔的退避因子，如果为None则使用默认因子
            failed_task_storage_dir: 失败任务管理器的存储目录，如果为None则使用默认目录
            unfinished_task_storage_dir: 未完成任务管理器的存储目录，如果为None则使用默认目录
            execution_mode: 执行模式，可选值为"thread"（多线程）和"process"（多进程），默认为"thread"
            process_initialization_timeout: 进程初始化超时时间（秒），仅在多进程模式下有效
            show_progress: 是否显示进度条，默认为True
        """
        # 直接使用传入的参数，不再从配置文件读取
        # 如果max_workers为None，则根据CPU核心数自动设置
        if max_workers is None:
            if execution_mode == "thread":
                # 线程模式下，默认使用CPU核心数的2倍作为最大线程数
                max_workers = multiprocessing.cpu_count() * 2
            else:
                # 进程模式下，默认使用CPU核心数作为最大进程数
                max_workers = multiprocessing.cpu_count()

        self.max_workers = max_workers
        self.task_interval = task_interval
        self.task_timeout = task_timeout
        self.record_failed = record_failed

        # 初始化重试相关参数
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.backoff_factor = backoff_factor

        # 初始化执行模式相关参数
        self.execution_mode = execution_mode
        self.process_initialization_timeout = process_initialization_timeout
        self.show_progress = show_progress

        # 初始化任务类型和管理器
        self.task_type = task_type
        self.failed_task_manager = BatchTaskFailureManager(
            task_type, storage_dir=failed_task_storage_dir
        )
        self.unfinished_task_manager = BatchTaskUnfinishedManager(
            task_type, storage_dir=unfinished_task_storage_dir
        )

        # 使用系统日志记录初始化信息
        system_logger.info(
            f"初始化批量任务执行器：task_type={self.task_type}, max_workers={self.max_workers}, "
            f"task_interval={self.task_interval}, task_timeout={self.task_timeout}, "
            f"record_failed={self.record_failed}, execution_mode={self.execution_mode}"
        )
        # 使用用户日志记录简明的初始化信息
        user_logger.info(
            f"批量任务执行器初始化完成：{self.task_type}，执行模式：{self.execution_mode}"
        )

        # 检查并警告多进程模式的限制
        if self.execution_mode == "process":
            system_logger.warning(
                "使用多进程模式执行任务可能会受到以下限制：\n"
                "1. 任务函数必须是可序列化的（不可使用lambda或内部函数）\n"
                "2. 任务函数必须是可被pickle模块序列化的\n"
                "3. 任务函数的参数和返回值也必须是可序列化的\n"
                "如果遇到序列化错误，请考虑使用多线程模式"
            )

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

            # 处理错误跟踪信息
            if hasattr(result, "error_trace") and result.error_trace:
                task.error_trace = result.error_trace

                # 失败信息同时记录在系统日志和用户日志中
                system_logger.error(
                    f"任务执行失败：task_id={task.task_id}, error={task.error}\n{task.error_trace}"
                )
            else:
                system_logger.error(
                    f"任务执行失败：task_id={task.task_id}, error={task.error}"
                )

            user_logger.warning(f"任务失败：{task.task_id} - {task.error}")

            if self.record_failed:
                # 在记录失败任务时也包含错误跟踪信息
                self.failed_task_manager.record_failed_task(task)

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

        # 获取详细的错误跟踪信息
        error_trace = ""
        if hasattr(error, "traceback"):
            error_trace = error.traceback
        else:
            error_trace = traceback.format_exc()

        # 根据错误类型设置任务状态和错误信息
        if isinstance(error, TimeoutError):
            error_msg = "任务执行超时"
            task.status = TaskStatus.FAILED
            system_logger.error(f"任务执行超时：task_id={task.task_id}\n{error_trace}")
            user_logger.warning(f"任务超时：{task.task_id}")
        elif isinstance(error, KeyboardInterrupt):
            error_msg = "任务被中断"
            task.status = TaskStatus.FAILED
            batch_task.set_status(BatchStatus.INTERRUPTED)
            system_logger.warning(f"任务被中断：task_id={task.task_id}\n{error_trace}")
            user_logger.warning(f"任务被中断：{task.task_id}")
        else:
            error_msg = f"错误：{str(error)}\n堆栈：{error_trace}"
            task.status = TaskStatus.FAILED
            # 详细错误信息记录到系统日志，简略信息记录到用户日志
            system_logger.error(
                f"任务执行出错：task_id={task.task_id}, error={str(error)}\n{error_trace}"
            )
            user_logger.error(f"任务出错：{task.task_id} - {str(error)}")

        task.error = error_msg
        task.error_trace = error_trace

        # 记录失败任务到缓存
        if self.record_failed:
            self.failed_task_manager.record_failed_task(
                task.task_id, task.params, error_msg, error_trace=error_trace
            )

        # 记录任务状态
        self.unfinished_task_manager.record_task_status(task)

        if future:
            future.cancel()

    def _create_executor(
        self, max_workers: int, execution_mode: Optional[ExecutionMode] = None
    ) -> Union[ThreadPoolExecutor, ProcessPoolExecutor]:
        """创建线程池或进程池执行器

        Args:
            max_workers: 最大工作线程/进程数
            execution_mode: 执行模式，如果为None则使用实例的执行模式

        Returns:
            ThreadPoolExecutor或ProcessPoolExecutor实例
        """
        mode = execution_mode or self.execution_mode
        if mode == "thread":
            return ThreadPoolExecutor(max_workers=max_workers)
        elif mode == "process":
            return ProcessPoolExecutor(
                max_workers=max_workers,
                initializer=self._process_initializer,
                initargs=(self.process_initialization_timeout,),
            )
        else:
            raise ValueError(f"不支持的执行模式: {mode}")

    def _process_initializer(self, timeout: int = 60):
        """进程初始化函数

        在多进程模式下，每个子进程启动时都会调用此函数
        用于初始化进程环境，如设置日志等

        Args:
            timeout: 初始化超时时间（秒）
        """
        try:
            # 在这里进行子进程的初始化工作
            # 例如重新配置日志等，确保在子进程中也能正常工作
            import logging
            from datawhale.logging import get_user_logger, get_system_logger

            # 重新初始化日志
            global user_logger, system_logger
            user_logger = get_user_logger(__name__)
            system_logger = get_system_logger(__name__)

            system_logger.debug(
                f"子进程初始化完成，进程ID: {multiprocessing.current_process().pid}"
            )
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"子进程初始化失败: {str(e)}\n{error_trace}")
            # 这里无法使用日志，因为日志可能尚未初始化
            raise RuntimeError(f"子进程初始化失败: {str(e)}")

    def _handle_interruption(
        self,
        executor: Union[ThreadPoolExecutor, ProcessPoolExecutor],
        futures: List[Future],
    ) -> None:
        """处理任务中断

        取消所有未完成的任务，关闭线程池或进程池。

        Args:
            executor: 线程池或进程池执行器
            futures: 待处理的Future对象列表
        """
        for future in futures:
            if not future.done():
                future.cancel()

        # 根据不同执行模式处理关闭操作
        if isinstance(executor, ThreadPoolExecutor):
            executor.shutdown(wait=False)
        else:
            # ProcessPoolExecutor 关闭
            try:
                executor.shutdown(wait=False)
            except Exception as e:
                system_logger.error(f"关闭进程池时出错: {str(e)}")

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
        execution_mode: ExecutionMode = None,  # 新增参数：执行模式
        show_progress: bool = None,  # 新增参数：是否显示进度条
    ) -> BatchTask:
        """执行批量任务

        Args:
            task_func: 任务执行函数
            task_params_list: 任务参数列表
            task_timeout: 单个任务超时时间（秒）
            task_interval: 任务提交间隔（秒）
            max_workers: 最大工作线程/进程数
            batch_id: 批次ID
            task_max_retries: 最大重试次数
            task_retry_interval: 重试间隔（秒）
            backoff_factor: 重试间隔的退避因子
            batch_mode: 批次模式，可选值为"new"、"resume"和"retry"
            execution_mode: 执行模式，可选值为"thread"和"process"，如果为None则使用实例的执行模式
            show_progress: 是否显示进度条，如果为None则使用实例的设置

        Returns:
            BatchTask: 批次任务对象
        """
        # 参数验证
        if batch_mode not in ["new", "resume", "retry"]:
            raise ValueError(
                f"不支持的批次模式: {batch_mode}，可选值为'new'、'resume'和'retry'"
            )

        if task_func is None:
            raise ValueError("必须提供任务执行函数(task_func)")

        # 检查执行模式
        if execution_mode is not None and execution_mode not in ["thread", "process"]:
            raise ValueError(
                f"不支持的执行模式: {execution_mode}，可选值为'thread'和'process'"
            )

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
        # 设置执行模式和进度条显示
        execution_mode = execution_mode or self.execution_mode
        show_progress = self.show_progress if show_progress is None else show_progress

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
                if "error_trace" in task_info:
                    task.error_trace = task_info["error_trace"]
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
                # 从失败任务信息中获取错误信息
                if "error" in task_info:
                    task.error = task_info["error"]
                if "error_trace" in task_info:
                    task.error_trace = task_info["error_trace"]
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
            f"max_workers={max_workers}, task_interval={task_interval}, "
            f"execution_mode={execution_mode}"
        )
        user_logger.info(
            f"开始执行批量任务：共{batch_task.total_count}个任务，模式：{batch_mode}，执行方式：{execution_mode}"
        )

        executor = None
        task_error_occurred = False
        futures = []

        try:
            # 创建线程池或进程池执行器
            executor = self._create_executor(max_workers, execution_mode)

            # 定义进度条上下文管理器
            progress_context = (
                tqdm(total=len(tasks), desc=self.DEFAULT_PROGRESS_DESC)
                if show_progress
                else DummyTqdm(total=len(tasks))
            )

            with executor, progress_context as pbar:
                futures = []

                # 先记录所有任务的初始状态
                for task in tasks:
                    if task.status != TaskStatus.COMPLETED:  # 跳过已完成的任务
                        task.status = TaskStatus.PENDING
                        self.unfinished_task_manager.record_task_status(task)

                # 提交所有任务到执行器
                for task in tasks:
                    future = executor.submit(task.execute)
                    futures.append((future, task))

                # 等待所有任务完成
                for future, task in futures:
                    try:
                        result = future.result(timeout=task_timeout)
                        self._handle_task_result(batch_task, batch_mode, task, result)
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
                        system_logger.warning(f"用户中断任务执行：batch_id={batch_id}")
                        user_logger.warning("任务执行已被中断")
                        raise  # 重新抛出KeyboardInterrupt以进入外层异常处理
                    except Exception as e:
                        # 捕获详细的错误跟踪信息
                        error_trace = traceback.format_exc()
                        if not hasattr(e, "traceback"):
                            e.traceback = error_trace
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
            # 确保取消所有未完成的任务并关闭线程池或进程池
            if executor is not None:
                try:
                    # 过滤出未完成的future
                    pending_futures = [f for f, _ in futures if not f.done()]
                    if pending_futures:
                        system_logger.debug(
                            f"正在取消{len(pending_futures)}个未完成的任务"
                        )
                        self._handle_interruption(executor, pending_futures)
                except Exception as shutdown_error:
                    system_logger.error(f"关闭执行器时出错: {str(shutdown_error)}")

        except Exception as e:
            # 捕获详细的错误跟踪信息
            error_trace = traceback.format_exc()

            batch_task.set_status(BatchStatus.FAILED)
            batch_task.set_end_time()
            error_msg = f"批量任务执行过程中发生错误：{str(e)}\n{error_trace}"
            system_logger.error(error_msg)
            user_logger.error(f"批量任务执行失败：{str(e)}")

            # 如果是进程模式特有的错误，提供更详细的错误信息
            if execution_mode == "process" and (
                "pickle" in str(e).lower()
                or "serializ" in str(e).lower()
                or "multiprocessing" in str(e).lower()
            ):
                user_logger.error(
                    "这可能是由于多进程模式的序列化限制导致的。请考虑：\n"
                    "1. 将执行模式切换为'thread'（多线程模式）\n"
                    "2. 确保任务函数及其参数和返回值都是可序列化的\n"
                    "3. 避免使用lambda函数或内部函数作为任务函数"
                )

        finally:
            # 无论如何都要确保保存任务状态
            if batch_id:
                try:
                    self.unfinished_task_manager.flush_batch_tasks(batch_id)
                    self.failed_task_manager.flush_batch_tasks(batch_id)
                    system_logger.debug(f"成功保存任务状态：batch_id={batch_id}")
                except Exception as flush_error:
                    # 捕获并记录详细错误信息
                    error_trace = traceback.format_exc()
                    system_logger.error(
                        f"保存任务状态失败：{str(flush_error)}\n{error_trace}"
                    )
                    user_logger.error("保存任务状态失败")

        return batch_task


# 定义一个空的进度条用于不显示进度条的情况
class DummyTqdm:
    def __init__(self, total=None):
        self.total = total
        self.n = 0

    def update(self, n=1):
        self.n += n

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
