#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional, Callable, Set, TypeVar, Tuple, Union
from uuid import uuid4
import time
import inspect
import functools
import os
import tempfile
import pickle
import pandas as pd
import copy

# 从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger
from datawhale.storage import create_dataset, save, infer_dtypes

# 同一模块内的导入使用相对导入
from .status import NodeStatus

# 从上级模块导入
from ..namespace import Namespace, NamespaceRegistry

# 创建用户和系统日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")


class Edge:
    """表示节点之间的连接关系

    存储源节点和目标节点之间的关系以及参数映射信息
    """

    def __init__(
        self, source: "Node", target: "Node", param_name: Optional[str] = None
    ):
        """初始化边对象"""
        self.source = source
        self.target = target
        self.param_name = param_name
        self.edge_id = f"edge_{source.node_id}_{target.node_id}_{uuid4().hex[:6]}"

        system_logger.debug(
            f"[Edge][{self.edge_id}]：创建边，source={source.name}，target={target.name}"
        )

    def __str__(self) -> str:
        """返回边的字符串表示"""
        param_info = f"({self.param_name})" if self.param_name else ""
        return f"Edge({self.source.name}{param_info} -> {self.target.name})"

    def __repr__(self) -> str:
        """返回边的详细字符串表示"""
        param_info = f"({self.param_name})" if self.param_name else ""
        return f"Edge({self.source.name}{param_info} -> {self.target.name}, id={self.edge_id})"

    def remove(self):
        """移除边，断开源节点和目标节点的连接"""
        if self in self.source.downstream_edges:
            self.source.downstream_edges.remove(self)
        if self in self.target.upstream_edges:
            self.target.upstream_edges.remove(self)


class NodeProxy:
    """节点代理对象，用于在连接操作中代理节点，避免直接复制节点"""

    def __init__(self, node: "Node", as_param: Optional[str] = None):
        """初始化节点代理"""
        self.node = node
        self.as_param = as_param

    def __call__(self, **kwargs):
        """支持链式调用设置参数"""
        return NodeProxy(self.node, kwargs.get("as_param", self.as_param))

    def __rshift__(self, other) -> "Node":
        """重载 >> 运算符"""
        # 处理将当前节点连接到多个下游节点的情况
        if isinstance(other, (list, tuple)):
            for downstream_node in other:
                self.__rshift__(downstream_node)
            return other

        # 获取实际节点对象
        if isinstance(other, NodeProxy):
            param_name = other.as_param
            other = other.node
        else:
            param_name = None

        # 处理将多个上游节点连接到当前节点的情况
        if isinstance(self.node, (list, tuple)):
            for upstream_node in self.node:
                NodeProxy(upstream_node, self.as_param).__rshift__(other)
            return other

        # 创建连接关系
        self.node._add_downstream(other, param_name or self.as_param)
        return other

    def __lshift__(self, other) -> "Node":
        """重载 << 运算符"""
        if isinstance(other, NodeProxy):
            node = other.node
            param_name = other.as_param
        else:
            node = other
            param_name = None

        # 创建连接关系（源节点和目标节点顺序与>>相反）
        node._add_downstream(self.node, param_name)
        return node


def node(
    name: str = None,
    default_params: Dict[str, Any] = None,
    cache_result: bool = False,
    remove_from_namespace_after_execution: bool = False,
    save_to_namespace: bool = True,
):
    """节点装饰器

    将函数包装为Node对象，用于构建任务图
    """

    def decorator(func: Callable[..., T]) -> Node:
        # 获取函数的参数规范
        sig = inspect.signature(func)

        # 使用函数名作为节点名称（如果未指定）
        node_name = name or func.__name__

        # 创建节点对象
        node_obj = Node(
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

    # 支持直接使用@node语法
    if callable(name):
        func, name = name, None
        return decorator(func)

    return decorator


class Node:
    """任务节点对象

    负责构建上下游节点的关联关系，并在执行时调用任务函数。
    节点可以通过依赖关系组成有向无环图(DAG)，实现任务的有序执行。
    """

    def __init__(
        self,
        name: str,
        task_func: Callable[..., T],
        inputs: Dict[str, str] = None,
        default_params: Dict[str, Any] = None,
        node_id: str = None,
        cache_result: bool = False,
        remove_from_namespace_after_execution: bool = True,
        save_to_namespace: bool = True,
    ):
        """初始化任务节点对象"""
        self.node_id = node_id or f"node_{name}_{uuid4().hex[:8]}"
        self.name = name
        self.task_func = task_func
        self.inputs = inputs or {}
        self.default_params = default_params or {}
        self.params = self.default_params.copy()

        # 使用边集合存储上下游关系
        self.upstream_edges: Set[Edge] = set()
        self.downstream_edges: Set[Edge] = set()

        self.status = NodeStatus.PENDING
        self.result = None
        self.error: Optional[str] = None
        self.create_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.cache_result = cache_result
        self.cache_path = None
        self.remove_from_namespace_after_execution = (
            remove_from_namespace_after_execution
        )
        self.save_to_namespace = save_to_namespace

        system_logger.debug(f"[Node][{self.node_id}]：创建节点，name={self.name}")

    def set_upstream(self, upstream_node: "Node") -> "Node":
        """设置上游节点"""
        upstream_node._add_downstream(self)
        return self

    def set_downstream(self, downstream_node: "Node") -> "Node":
        """设置下游节点"""
        self._add_downstream(downstream_node)
        return self

    def _add_downstream(
        self, downstream_node: "Node", param_name: Optional[str] = None
    ) -> "Node":
        """添加下游节点并创建边"""
        # 检查边是否已存在
        for edge in self.downstream_edges:
            if edge.target == downstream_node and edge.param_name == param_name:
                return self

        # 创建新边并添加到关系集合
        edge = Edge(self, downstream_node, param_name)
        self.downstream_edges.add(edge)
        downstream_node.upstream_edges.add(edge)

        # 更新输入参数映射
        if param_name:
            if not downstream_node.inputs:
                downstream_node.inputs = {}

            # 处理参数映射
            self._update_param_mapping(downstream_node, param_name)

        return self

    def _update_param_mapping(self, target_node: "Node", param_name: str):
        """更新参数映射"""
        # 判断是否为列表参数（通过命名约定）
        is_list_param = (
            param_name == "args"
            or param_name.endswith("[]")
            or param_name.endswith("_list")
        )
        base_param = param_name.rstrip("[]") if is_list_param else param_name

        if is_list_param and base_param in target_node.inputs:
            # 转换为列表或追加到现有列表
            if isinstance(target_node.inputs[base_param], list):
                if self.name not in target_node.inputs[base_param]:
                    target_node.inputs[base_param].append(self.name)
            else:
                # 如果是字符串，转换为列表
                target_node.inputs[base_param] = [
                    target_node.inputs[base_param],
                    self.name,
                ]
        else:
            # 普通参数，直接设置
            target_node.inputs[param_name] = self.name

    def get_upstream_nodes(self) -> List["Node"]:
        """获取所有上游节点"""
        return [edge.source for edge in self.upstream_edges]

    def get_downstream_nodes(self) -> List["Node"]:
        """获取所有下游节点"""
        return [edge.target for edge in self.downstream_edges]

    def set_params(self, params: Dict[str, Any]) -> "Node":
        """设置节点参数"""
        self.params.update(params)
        return self

    def _cache_result_to_file(self, result_value: Any, cache_dir: str) -> Optional[str]:
        """将结果缓存到文件"""
        if not self.cache_result:
            return None

        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)

        # 生成缓存文件路径
        cache_filename = f"{self.name}_{self.node_id}_{int(time.time())}.pkl"
        cache_path = os.path.join(cache_dir, cache_filename)

        try:
            # 序列化并保存结果
            with open(cache_path, "wb") as f:
                pickle.dump(result_value, f)
            system_logger.debug(
                f"[Node][{self.node_id}]：结果已缓存，path={cache_path}"
            )
            return cache_path
        except Exception as e:
            system_logger.error(f"[Node][{self.node_id}]：缓存结果失败，错误={str(e)}")
            return None

    def execute(
        self,
        namespace_registry: Optional[NamespaceRegistry] = None,
        cache_dir: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Any:
        """执行节点"""
        start_time = time.time()
        self.start_time = start_time
        self.status = NodeStatus.RUNNING

        system_logger.info(f"[Node][{self.node_id}]：开始执行，name={self.name}")

        # 准备函数输入参数
        func_params = self.params.copy()

        # 如果提供了命名空间注册表，从命名空间获取输入参数
        if namespace_registry and self.inputs:
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
                            f"[Node][{self.node_id}]：获取输入参数，name={self.name}，"
                            f"param={param_name}，from={node_name}，value={value}"
                        )
                    else:
                        # 如果从上游节点获取不到值(可能是跳过状态)，尝试从其他来源获取
                        # 收集所有可以提供同名参数的上游节点
                        alternative_sources = []
                        for edge in self.upstream_edges:
                            if (
                                edge.param_name == param_name
                                and edge.source.name != node_name
                            ):
                                # 把活动节点（已完成）放在列表前面
                                if edge.source.status == NodeStatus.COMPLETED:
                                    alternative_sources.insert(0, edge.source.name)
                                else:
                                    alternative_sources.append(edge.source.name)

                        # 尝试从备选上游节点获取参数值
                        for alt_source in alternative_sources:
                            alt_value = namespace_registry.get_value(alt_source)
                            if alt_value is not None:
                                func_params[param_name] = alt_value
                                system_logger.debug(
                                    f"[Node][{self.node_id}]：从备选上游节点获取输入参数，name={self.name}，"
                                    f"param={param_name}，alt_from={alt_source}，value={alt_value}"
                                )
                                break

        # 合并其他参数
        func_params.update(kwargs)

        try:
            # 执行节点处理函数
            result = self.task_func(**func_params)
            self.result = result
            self.status = NodeStatus.COMPLETED

            # 保存结果到命名空间（如果提供了命名空间注册表且需要保存）
            if namespace_registry and self.save_to_namespace:
                # 如果启用了结果缓存
                if self.cache_result and result is not None and cache_dir:
                    # 缓存结果到文件
                    cache_path = self._cache_result_to_file(result, cache_dir)

                    if cache_path:
                        # 设置结果值和缓存路径
                        namespace_registry.set_value(self.name, result)
                        namespace_registry.set_cache_path(self.name, cache_path)
                        self.cache_path = cache_path
                        system_logger.debug(
                            f"[Node][{self.node_id}]：设置命名空间缓存路径，cache_path={cache_path}"
                        )
                    else:
                        # 缓存失败，只保存原始结果
                        namespace_registry.set_value(self.name, result)
                else:
                    # 不需要缓存，直接更新命名空间
                    namespace_registry.set_value(self.name, result)
                    system_logger.debug(
                        f"[Node][{self.node_id}]：结果已保存到命名空间，name={self.name}, value={result}"
                    )
            elif not self.save_to_namespace:
                system_logger.debug(
                    f"[Node][{self.node_id}]：结果不保存到命名空间，save_to_namespace={self.save_to_namespace}"
                )

            return result

        except Exception as e:
            self.error = str(e)
            self.status = NodeStatus.FAILED
            system_logger.error(f"[Node][{self.node_id}]：执行失败，错误={str(e)}")
            raise
        finally:
            # 记录执行时间
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            system_logger.info(
                f"[Node][{self.node_id}]：执行完成，status={self.status}，耗时={execution_time:.2f}秒"
            )

    def _can_execute(self) -> bool:
        """检查节点是否可以执行"""
        # 如果没有上游节点或所有上游节点都已成功完成或被跳过，则可以执行
        if not self.upstream_edges:
            return True

        for edge in self.upstream_edges:
            # 上游节点完成或被跳过都视为有效状态
            if edge.source.status not in [NodeStatus.COMPLETED, NodeStatus.SKIPPED]:
                return False

        return True

    def __call__(self, **kwargs):
        """支持节点调用时设置参数"""
        return NodeProxy(self, kwargs.get("as_param"))

    def __str__(self) -> str:
        """返回节点的字符串表示"""
        return f"Node(name={self.name}, id={self.node_id})"

    def __repr__(self) -> str:
        """返回节点的详细字符串表示"""
        try:
            upstream = [edge.source.name for edge in self.upstream_edges]
            downstream = [edge.target.name for edge in self.downstream_edges]
            return (
                f"Node(name={self.name}, id={self.node_id}, "
                f"status={self.status}, "
                f"upstream={upstream}, downstream={downstream})"
            )
        except Exception as e:
            return f"Node(name={self.name}, id={self.node_id}, error={str(e)})"

    def __rshift__(self, other) -> "Node":
        """重载 >> 运算符，用于设置下游节点"""
        return NodeProxy(self) >> other

    def __lshift__(self, other) -> "Node":
        """重载 << 运算符，用于设置上游节点"""
        return NodeProxy(self) << other
