#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional, Callable, Set, TypeVar, Union
from uuid import uuid4
import time
import inspect
import functools
from collections import deque

# 从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger

# 同一模块内的导入使用相对导入
from .status import NodeStatus
from .node import Node

# 从上级模块导入
from ..namespace import NamespaceRegistry

# 创建用户和系统日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")


def decision_node(
    name: str = None,
    default_params: Dict[str, Any] = None,
    cache_result: bool = False,
    remove_from_namespace_after_execution: bool = False,
    save_to_namespace: bool = True,
):
    """判断节点装饰器

    将函数包装为DecisionNode对象，用于构建包含判断逻辑的任务图
    """

    def decorator(func: Callable[..., Union[str, List[str]]]) -> "DecisionNode":
        # 获取函数的参数规范
        sig = inspect.signature(func)

        # 使用函数名作为节点名称（如果未指定）
        node_name = name or func.__name__

        # 创建决策节点对象
        node_obj = DecisionNode(
            name=node_name,
            task_func=func,
            inputs={},
            default_params=default_params or {},
            cache_result=cache_result,
            remove_from_namespace_after_execution=remove_from_namespace_after_execution,
            save_to_namespace=save_to_namespace,
        )

        # 复制原函数的元数据
        functools.update_wrapper(node_obj, func)

        return node_obj

    # 支持直接使用@decision_node语法
    if callable(name):
        func, name = name, None
        return decorator(func)

    return decorator


class DecisionNode(Node):
    """判断节点对象

    一种特殊的节点，支持一对多的链接方式，可以根据节点执行结果决定后续执行哪些分支。
    判断节点的task_func需要返回一个字符串或字符串列表，表示要执行的下游路径名称。
    """

    def __init__(
        self,
        name: str,
        task_func: Callable[..., Union[str, List[str]]],
        inputs: Dict[str, str] = None,
        default_params: Dict[str, Any] = None,
        node_id: str = None,
        cache_result: bool = False,
        remove_from_namespace_after_execution: bool = True,
        save_to_namespace: bool = True,
    ):
        """初始化判断节点对象"""
        super().__init__(
            name=name,
            task_func=task_func,
            inputs=inputs,
            default_params=default_params,
            node_id=node_id or f"decision_{name}_{uuid4().hex[:8]}",
            cache_result=cache_result,
            remove_from_namespace_after_execution=remove_from_namespace_after_execution,
            save_to_namespace=save_to_namespace,
        )

        # 用于存储路径名称到下游节点的映射关系
        self.path_routes: Dict[str, List[Node]] = {}

        system_logger.debug(
            f"[DecisionNode][{self.node_id}]：创建判断节点，name={self.name}"
        )

    def add_path(
        self, path_name: str, downstream_node: Node, param_name: Optional[str] = None
    ) -> "DecisionNode":
        """添加决策路径

        Args:
            path_name: 路径名称，与task_func的返回值对应
            downstream_node: 该路径对应的下游节点
            param_name: 参数名称，用于设置下游节点的输入参数

        Returns:
            判断节点自身，用于链式调用
        """
        # 首先添加下游节点（标准连接）
        self._add_downstream(downstream_node, param_name)

        # 将下游节点添加到对应路径的映射中
        if path_name not in self.path_routes:
            self.path_routes[path_name] = []

        if downstream_node not in self.path_routes[path_name]:
            self.path_routes[path_name].append(downstream_node)
            system_logger.debug(
                f"[DecisionNode][{self.node_id}]：添加路径，path={path_name}，"
                f"target={downstream_node.name}"
            )

        return self

    def _collect_inputs(self, namespace_registry):
        """收集执行任务所需的输入参数

        Args:
            namespace_registry: 命名空间注册表

        Returns:
            包含所有输入参数的字典
        """
        # 准备函数输入参数
        func_params = self.params.copy()

        # 如果提供了命名空间注册表，从命名空间获取输入参数
        if self.inputs:
            for param_name, node_name in self.inputs.items():
                # 处理参数名可能是列表的情况
                if isinstance(node_name, list):
                    # 从多个上游节点获取值并组成列表
                    param_values = []
                    for n_name in node_name:
                        value = namespace_registry.get_value(n_name)
                        if value is not None:
                            param_values.append(value)
                    if param_values:
                        func_params[param_name] = param_values
                else:
                    # 从单个上游节点获取值
                    value = namespace_registry.get_value(node_name)
                    if value is not None:
                        func_params[param_name] = value
                        system_logger.debug(
                            f"[DecisionNode][{self.node_id}]：获取输入参数，name={self.name}，"
                            f"param={param_name}，from={node_name}，value={value}"
                        )

        return func_params

    def _mark_node_and_downstream_as_skipped(
        self, node, namespace_registry=None, visited=None
    ):
        """递归地将节点及其所有下游节点标记为跳过状态

        Args:
            node: 要标记的节点
            namespace_registry: 命名空间注册表，用于设置节点默认值
            visited: 已访问过的节点集合，避免循环依赖
        """
        if visited is None:
            visited = set()

        # 如果节点已经被访问过，直接返回
        if node in visited:
            return

        # 将节点添加到已访问集合
        visited.add(node)

        # 标记当前节点为跳过
        if node.status == NodeStatus.PENDING:
            node.status = NodeStatus.SKIPPED
            system_logger.info(f"[DecisionNode]：标记节点为跳过状态，node={node.name}")

            # 如果需要保存到命名空间，设置默认值
            if namespace_registry and node.save_to_namespace:
                namespace_registry.set_value(node.name, None)
                system_logger.debug(
                    f"[DecisionNode]：为跳过节点设置默认值，node={node.name}"
                )

        # 递归标记所有下游节点
        for edge in node.downstream_edges:
            self._mark_node_and_downstream_as_skipped(
                edge.target, namespace_registry, visited
            )

    def execute(
        self,
        namespace_registry: Dict[str, NamespaceRegistry],
        cache_dir: str = None,
        **kwargs,
    ):
        """执行决策节点并根据输出选择执行路径

        Args:
            namespace_registry: 命名空间注册表
            cache_dir: 缓存目录
            **kwargs: 额外的参数，会直接传递给task_func
        """
        # 检查节点是否已经执行完成，避免重复执行
        if self.status == NodeStatus.COMPLETED:
            return self.output_data

        # 检查节点是否可以执行
        if not self._can_execute():
            self.status = NodeStatus.PENDING
            return None

        # 更新状态
        self.status = NodeStatus.RUNNING
        self.start_time = time.time()

        # 记录开始执行
        system_logger.info(f"[DecisionNode]：开始执行决策节点，node={self.name}")

        # 获取输入数据
        input_data = self._collect_inputs(namespace_registry)

        # 合并额外的参数
        input_data.update(kwargs)

        try:
            # 执行任务函数并获取结果
            result = self.task_func(**input_data)

            # 更新节点状态和结果
            self.output_data = result
            self.status = NodeStatus.COMPLETED
            self.end_time = time.time()

            # 根据结果确定后续路径
            if isinstance(result, list):
                # 多路径结果
                selected_paths = result
            else:
                # 单路径结果
                selected_paths = [result]

            # 获取所有决策路径名
            all_paths = set(self.path_routes.keys())

            # 获取已选择的路径名
            selected_path_names = set(selected_paths)

            # 获取未选择的路径名
            unselected_path_names = all_paths - selected_path_names

            # 记录已选择的路径
            system_logger.info(
                f"[DecisionNode]：决策节点选择路径，node={self.name}，paths={selected_paths}"
            )

            # 收集所有选中路径的直接节点
            active_nodes = set()
            for path_name in selected_path_names:
                if path_name in self.path_routes:
                    active_nodes.update(self.path_routes[path_name])

            # 标记未选择路径的直接节点为跳过状态（如果它们不是活跃节点）
            for path_name in unselected_path_names:
                if path_name in self.path_routes:
                    for node in self.path_routes[path_name]:
                        if node not in active_nodes:
                            # 递归标记节点及其下游节点为跳过状态
                            self._mark_node_and_downstream_as_skipped(
                                node, namespace_registry
                            )

            # 保存结果到命名空间（如果需要保存）
            if self.save_to_namespace:
                # 设置结果值
                namespace_registry.set_value(self.name, result)
                system_logger.debug(
                    f"[DecisionNode][{self.node_id}]：结果已保存到命名空间，name={self.name}, value={result}"
                )

            return self.output_data

        except Exception as e:
            # 更新节点状态和错误信息
            self.status = NodeStatus.FAILED
            self.error = str(e)
            self.end_time = time.time()

            # 记录节点执行失败
            system_logger.error(
                f"[DecisionNode]：决策节点执行失败，node={self.name}，error={str(e)}"
            )

            # 抛出异常
            raise e

    def __str__(self) -> str:
        """返回判断节点的字符串表示"""
        return f"DecisionNode(name={self.name}, id={self.node_id})"

    def __repr__(self) -> str:
        """返回判断节点的详细字符串表示"""
        try:
            paths = {
                path: [node.name for node in nodes]
                for path, nodes in self.path_routes.items()
            }
            upstream = [edge.source.name for edge in self.upstream_edges]
            downstream = [edge.target.name for edge in self.downstream_edges]

            return (
                f"DecisionNode(name={self.name}, id={self.node_id}, "
                f"status={self.status}, paths={paths}, "
                f"upstream={upstream}, downstream={downstream})"
            )
        except Exception as e:
            return f"DecisionNode(name={self.name}, id={self.node_id}, error={str(e)})"
