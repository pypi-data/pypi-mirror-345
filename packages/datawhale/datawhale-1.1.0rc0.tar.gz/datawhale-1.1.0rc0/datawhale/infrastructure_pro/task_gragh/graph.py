#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Set, Any, Optional, Callable, TypeVar
from collections import deque
import time
import os

# 从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger

# 同一模块内的导入使用相对导入
from .node.node import Node, Edge, NodeProxy
from .node.status import NodeStatus
from .namespace import Namespace, NamespaceRegistry
from uuid import uuid4
import graphviz

# 创建用户和系统日志记录器
user_logger = get_user_logger(__name__)
system_logger = get_system_logger(__name__)

T = TypeVar("T")

GRAPHVIZ_AVAILABLE = True


class GraphStatus:
    """图执行状态常量"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    PARTIAL = "partial"  # 部分完成（有些节点失败）


class Graph:
    """任务图对象

    管理Node节点组成的有向无环图(DAG)，负责按拓扑顺序执行节点。

    属性:
        name: 图名称
        nodes: 所有节点的集合
        status: 图的当前执行状态
        cache_dir: 缓存目录路径，用于存储节点执行结果的缓存
    """

    def __init__(
        self, name: str, nodes: List[Node] = None, cache_dir: Optional[str] = None
    ):
        """初始化图对象

        Args:
            name: 图名称
            nodes: 初始节点列表，默认为空列表
            cache_dir: 缓存目录路径，用于存储节点执行结果的缓存
                      如果为None，则不使用缓存目录
        """
        self.graph_id = f"graph_{name}_{uuid4().hex[:8]}"
        self.name = name
        self.nodes: Set[Node] = set()
        self.status = GraphStatus.PENDING
        self.results: Dict[str, str] = {}  # 节点名到状态的映射
        self.create_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # 缓存目录设置
        self.cache_dir = cache_dir

        # 如果指定了缓存目录，则确保缓存目录存在
        if self.cache_dir is not None:
            os.makedirs(self.cache_dir, exist_ok=True)
            system_logger.debug(
                f"[Graph][{self.graph_id}]：创建缓存目录，cache_dir={self.cache_dir}"
            )

        # 创建命名空间注册表，用于节点间参数传递
        self.namespace_registry = NamespaceRegistry()

        # 添加初始节点
        if nodes:
            for node in nodes:
                self.add_node(node)

        system_logger.debug(f"[Graph][{self.graph_id}]：创建任务图，name={self.name}")

    def add_node(self, node: Node) -> "Graph":
        """添加节点到图

        递归添加节点及其所有上下游节点。

        Args:
            node: 要添加的节点

        Returns:
            图对象自身，用于链式调用
        """
        # 处理NodeProxy对象

        if isinstance(node, NodeProxy):
            node = node.node

        if node in self.nodes:
            return self

        self.nodes.add(node)

        # 如果节点需要缓存且没有设置缓存目录，则创建一个与图ID相关的缓存目录
        if node.cache_result and self.cache_dir is None:
            self.cache_dir = os.path.join(os.getcwd(), f"cache_graph_{self.graph_id}")
            os.makedirs(self.cache_dir, exist_ok=True)

        # 递归添加所有上游节点
        for upstream_edge in node.upstream_edges:
            self.add_node(upstream_edge.source)

        # 递归添加所有下游节点
        for downstream_edge in node.downstream_edges:
            self.add_node(downstream_edge.target)

        return self

    def add_nodes(self, nodes: List[Node]) -> "Graph":
        """批量添加节点到图

        Args:
            nodes: 要添加的节点列表

        Returns:
            图对象自身，用于链式调用
        """
        for node in nodes:
            self.add_node(node)
        return self

    def add_node_after(
        self, target_node_name: str, new_node: Node, connect_downstream: bool = True
    ) -> Node:
        """在指定节点后添加一个新节点

        Args:
            target_node_name: 目标节点名称
            new_node: 要添加的新节点
            connect_downstream: 是否将新节点连接到目标节点的下游节点

        Returns:
            添加的节点对象

        Raises:
            ValueError: 如果目标节点不存在
        """
        # 检查目标节点是否存在
        target_node = self.get_node_by_name(target_node_name)
        if target_node is None:
            raise ValueError(f"目标节点 '{target_node_name}' 不存在于图中")

        system_logger.debug(
            f"[Graph][{self.graph_id}]：在节点 '{target_node_name}' 后添加节点 '{new_node.name}'"
        )

        # 添加新节点到图
        self.add_node(new_node)

        # 将目标节点连接到新节点
        target_node._add_downstream(new_node)

        if connect_downstream and target_node.downstream_edges:
            # 存储原始下游边以避免在迭代过程中修改集合
            original_downstream_edges = list(target_node.downstream_edges)

            # 断开目标节点与其下游节点的连接，并连接新节点到这些下游节点
            for edge in original_downstream_edges:
                downstream_node = edge.target

                # 跳过新添加的边
                if downstream_node == new_node:
                    continue

                # 移除原来的连接
                edge.remove()
                # 创建新连接
                new_node._add_downstream(downstream_node)
                system_logger.debug(
                    f"[Graph][{self.graph_id}]：将节点 '{new_node.name}' 连接到下游节点 '{downstream_node.name}'"
                )

        return new_node

    def add_node_before(
        self, target_node_name: str, new_node: Node, connect_upstream: bool = True
    ) -> Node:
        """在指定节点前添加一个新节点

        Args:
            target_node_name: 目标节点名称
            new_node: 要添加的新节点
            connect_upstream: 是否将目标节点的上游节点连接到新节点

        Returns:
            添加的节点对象

        Raises:
            ValueError: 如果目标节点不存在
        """
        # 检查目标节点是否存在
        target_node = self.get_node_by_name(target_node_name)
        if target_node is None:
            raise ValueError(f"目标节点 '{target_node_name}' 不存在于图中")

        system_logger.debug(
            f"[Graph][{self.graph_id}]：在节点 '{target_node_name}' 前添加节点 '{new_node.name}'"
        )

        # 添加新节点到图
        self.add_node(new_node)

        # 将新节点连接到目标节点
        new_node._add_downstream(target_node)

        if connect_upstream and target_node.upstream_edges:
            # 存储原始上游边以避免在迭代过程中修改集合
            original_upstream_edges = list(target_node.upstream_edges)

            # 断开目标节点与其上游节点的连接，并连接这些上游节点到新节点
            for edge in original_upstream_edges:
                upstream_node = edge.source

                # 跳过新添加的边
                if upstream_node == new_node:
                    continue

                # 移除原来的连接
                edge.remove()
                # 创建新连接
                upstream_node._add_downstream(new_node)
                system_logger.debug(
                    f"[Graph][{self.graph_id}]：将上游节点 '{upstream_node.name}' 连接到节点 '{new_node.name}'"
                )

        return new_node

    def get_node_by_name(self, name: str) -> Optional[Node]:
        """根据名称获取节点

        Args:
            name: 节点名称

        Returns:
            匹配的节点对象，如果未找到则返回None
        """
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_start_nodes(self) -> List[Node]:
        """获取所有起始节点（没有上游节点的节点）

        Returns:
            起始节点列表
        """
        return [node for node in self.nodes if not node.upstream_edges]

    def get_end_nodes(self) -> List[Node]:
        """获取所有终止节点（没有下游节点的节点）

        Returns:
            终止节点列表
        """
        return [node for node in self.nodes if not node.downstream_edges]

    def reset(self) -> None:
        """重置图的执行状态

        重置所有节点的状态和结果，准备重新执行
        """
        for node in self.nodes:
            node.status = NodeStatus.PENDING
            node.result = None
            node.error = None
            node.start_time = None
            node.end_time = None

        self.status = GraphStatus.PENDING
        self.results = {}
        self.start_time = None
        self.end_time = None

        # 清空命名空间注册表
        self.namespace_registry.clear()

        system_logger.debug(f"[Graph][{self.graph_id}]：重置图状态")

    def has_cycle(self) -> bool:
        """检测图中是否存在环（循环依赖）

        使用深度优先搜索算法检测有向图中的环

        Returns:
            bool: 如果图中存在环返回True，否则返回False
        """
        # 所有节点的访问状态
        # 0: 未访问, 1: 正在访问, 2: 已访问完成
        visit_status = {node: 0 for node in self.nodes}

        def dfs(node):
            # 标记为正在访问
            visit_status[node] = 1

            # 访问所有下游节点
            for edge in node.downstream_edges:
                downstream = edge.target
                if downstream in self.nodes:  # 只处理图中的节点
                    # 如果下游节点正在被访问，说明形成了环
                    if visit_status[downstream] == 1:
                        return True
                    # 如果下游节点未访问，递归检查
                    elif visit_status[downstream] == 0:
                        if dfs(downstream):
                            return True

            # 标记为已访问完成
            visit_status[node] = 2
            return False

        # 从所有未访问的节点开始DFS
        for node in self.nodes:
            if visit_status[node] == 0:
                if dfs(node):
                    return True

        return False

    def execute(
        self, start_params: Dict[str, Any] = None, check_dag: bool = False
    ) -> Dict[str, str]:
        """执行图中的所有节点

        首先检查图是否有环，然后获取拓扑排序的节点列表，按顺序执行各节点。

        Args:
            start_params: 开始节点的输入参数，默认为空字典
            check_dag: 是否检查DAG有效性，默认False

        Returns:
            图执行结果，键为节点名称，值为节点执行状态
        """
        # 初始化开始参数
        if start_params is None:
            start_params = {}

        # 重置状态
        self.reset()

        # 检查图是否有环
        if check_dag and self.has_cycle():
            system_logger.error(f"[Graph][{self.graph_id}]：图中存在环，无法执行")
            raise ValueError(f"图中存在环，无法执行: {self.name}")

        # 设置图状态
        self.status = GraphStatus.RUNNING
        self.start_time = time.time()

        # 记录开始执行
        system_logger.info(f"[Graph][{self.graph_id}]：开始执行图，name={self.name}")

        # 获取开始节点列表（没有上游节点的节点）
        start_nodes = self.get_start_nodes()

        if not start_nodes:
            if not self.nodes:
                system_logger.warning(f"[Graph][{self.graph_id}]：图为空")
                self.status = GraphStatus.COMPLETED
                return {}
            system_logger.warning(f"[Graph][{self.graph_id}]：没有找到起始节点")
            return {}

        # 设置开始节点的参数
        for start_node in start_nodes:
            if start_node.name in start_params:
                start_node.set_params(start_params[start_node.name])

        # 获取节点的执行顺序
        execution_order = self.get_execution_order()

        # 按顺序执行节点
        for node in execution_order:
            # 如果节点已被标记为跳过，则不执行
            if node.status == NodeStatus.SKIPPED:
                system_logger.info(
                    f"[Graph][{self.graph_id}]：节点已被标记为跳过，node={node.name}"
                )
                self.results[node.name] = node.status
                continue

            # 检查节点是否可以执行
            if node._can_execute():
                try:
                    # 执行节点
                    node.execute(self.namespace_registry, self.cache_dir)

                    # 更新结果
                    self.results[node.name] = node.status

                except Exception as e:
                    # 记录节点执行失败
                    node.status = NodeStatus.FAILED
                    node.error = str(e)
                    self.results[node.name] = node.status
                    system_logger.error(
                        f"[Graph][{self.graph_id}]：节点执行失败，node={node.name}，error={str(e)}"
                    )
            else:
                # 标记节点为失败状态
                node.status = NodeStatus.FAILED
                self.results[node.name] = node.status
                system_logger.warning(
                    f"[Graph][{self.graph_id}]：节点依赖未满足，无法执行，node={node.name}"
                )

        # 检查执行状态
        failed_nodes = [
            node.name for node in self.nodes if node.status == NodeStatus.FAILED
        ]

        if failed_nodes:
            if len(failed_nodes) == len(self.nodes):
                self.status = GraphStatus.FAILED
            else:
                self.status = GraphStatus.PARTIAL
                system_logger.warning(
                    f"[Graph][{self.graph_id}]：图执行部分失败，failed_nodes={failed_nodes}"
                )
        else:
            self.status = GraphStatus.COMPLETED
            system_logger.info(f"[Graph][{self.graph_id}]：图执行成功")

        # 记录执行完成
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        system_logger.info(
            f"[Graph][{self.graph_id}]：图执行完成，status={self.status}，耗时={elapsed_time:.3f}秒"
        )

        # 执行完成后清理不需要的命名空间数据
        for node in self.nodes:
            if node.remove_from_namespace_after_execution:
                # 清除命名空间中的节点数据
                self.namespace_registry.clear_namespace_value(node.name)

        return self.results

    def get_execution_order(self) -> List[Node]:
        """获取节点的执行顺序

        使用拓扑排序算法计算节点的执行顺序，确保上游节点先于下游节点执行。

        Returns:
            按拓扑顺序排列的节点列表
        """
        # 使用标准的拓扑排序
        visited: Set[Node] = set()  # 已经访问过的节点
        execution_order: List[Node] = []  # 执行顺序

        def dfs_topsort(node: Node):
            """深度优先搜索拓扑排序

            Args:
                node: 当前节点
            """
            visited.add(node)

            # 先遍历当前节点的所有下游节点
            for edge in node.downstream_edges:
                downstream = edge.target
                if downstream not in visited:
                    dfs_topsort(downstream)

            # 在回溯时将当前节点加入排序结果
            # 由于我们最终要的是按照拓扑顺序执行（从起始节点到终止节点），
            # 而DFS拓扑排序得到的是反向的，所以这里使用插入到列表开头的方式
            execution_order.insert(0, node)

        # 从所有节点出发进行DFS，确保处理所有可能的独立子图
        for node in self.nodes:
            if node not in visited:
                dfs_topsort(node)

        return execution_order

    def visualize(self, output_path=None) -> graphviz.Digraph:
        """可视化当前图结构，返回可视化对象

        Args:
            output_path: 可选，输出文件路径，不包含扩展名

        Returns:
            graphviz.Digraph 对象
        """
        if not GRAPHVIZ_AVAILABLE:
            system_logger.warning(
                f"[Graph][{self.graph_id}]：graphviz未安装，无法执行可视化"
            )
            return None

        # 初始化有向图对象
        dot = graphviz.Digraph(comment=f"Task Graph {self.graph_id}")

        # 添加节点
        node_status_colors = {
            NodeStatus.PENDING: "lightgrey",
            NodeStatus.RUNNING: "lightblue",
            NodeStatus.COMPLETED: "lightgreen",
            NodeStatus.FAILED: "salmon",
            NodeStatus.SKIPPED: "lightyellow",
        }

        for node in self.nodes:
            # 设置节点属性：填充颜色、形状、标签等
            label = f"{node.name}\n({node.status})"

            # 判断节点类型，为DecisionNode使用不同的形状
            from datawhale.infrastructure_pro.task_gragh.node.decision_node import (
                DecisionNode,
            )

            if isinstance(node, DecisionNode):
                shape = "diamond"  # 菱形用于决策节点
                label = f"{node.name}\n(决策节点)\n({node.status})"
            else:
                shape = "box"  # 矩形用于普通节点

            dot.node(
                node.name,
                label,
                style="filled",
                fillcolor=node_status_colors.get(node.status, "white"),
                shape=shape,
            )

        # 添加边
        for node in self.nodes:
            for edge in node.downstream_edges:
                # 如果源节点是决策节点，并且有路径信息，添加路径标签
                from datawhale.infrastructure_pro.task_gragh.node.decision_node import (
                    DecisionNode,
                )

                if isinstance(node, DecisionNode):
                    # 查找该目标节点属于哪个路径
                    path_labels = []
                    for path_name, nodes in node.path_routes.items():
                        if edge.target in nodes:
                            path_labels.append(path_name)

                    if path_labels:
                        label = ", ".join(path_labels)
                        dot.edge(node.name, edge.target.name, label=label)
                    else:
                        dot.edge(node.name, edge.target.name)
                else:
                    # 普通节点连接
                    if edge.param_name:
                        dot.edge(node.name, edge.target.name, label=edge.param_name)
                    else:
                        dot.edge(node.name, edge.target.name)

        # 如果指定了输出路径，则渲染并保存
        if output_path:
            try:
                dot.render(output_path, format="png", cleanup=True)
                system_logger.debug(
                    f"[Graph][{self.graph_id}]：图结构已保存到 {output_path}.png"
                )
            except Exception as e:
                system_logger.error(f"[Graph][{self.graph_id}]：保存图结构失败：{e}")

        return dot

    def get_node_value(self, node_name: str, default: Any = None) -> Any:
        """获取节点命名空间中存储的值

        Args:
            node_name: 节点名称
            default: 默认值，如果节点命名空间不存在则返回此值

        Returns:
            节点命名空间中存储的值，如果节点命名空间不存在则返回默认值
        """
        return self.namespace_registry.get_value(node_name, default)

    def __str__(self) -> str:
        """返回图的字符串表示

        Returns:
            图的字符串表示
        """
        return f"Graph(id={self.graph_id}, name={self.name}, nodes={len(self.nodes)})"

    def __repr__(self) -> str:
        """返回图的详细字符串表示

        Returns:
            图的详细字符串表示
        """
        return f"Graph(id={self.graph_id}, name={self.name}, nodes={len(self.nodes)}, status={self.status})"
