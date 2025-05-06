#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""命名空间模块"""

from typing import Dict, Any, List, Set, Optional
from uuid import uuid4

# 从顶层模块导入
from datawhale.logging import get_user_logger, get_system_logger

# 创建日志记录器
system_logger = get_system_logger(__name__)


class Namespace:
    """命名空间类

    用于存储节点输出值，支持节点间数据传递

    属性:
        namespace_id: 命名空间唯一标识
        node_name: 关联的节点名称
        value: 节点返回的值
        cache_path: 缓存路径，用于存储节点结果的临时文件或数据集路径
    """

    def __init__(
        self, node_name: str, value: Any = None, cache_path: Optional[str] = None
    ):
        """初始化命名空间

        Args:
            node_name: 关联的节点名称
            value: 节点返回的值，默认为None
            cache_path: 缓存路径，默认为None
        """
        self.namespace_id = f"namespace_{node_name}_{uuid4().hex[:8]}"
        self.node_name = node_name
        self.value = value
        self.cache_path = cache_path

        system_logger.debug(
            f"[Namespace][{self.namespace_id}]：创建命名空间，node_name={self.node_name}"
        )

    def set_value(self, value: Any) -> None:
        """设置值

        Args:
            value: 节点返回的值
        """
        self.value = value
        system_logger.debug(
            f"[Namespace][{self.namespace_id}]：设置值，node_name={self.node_name}"
        )

    def get_value(self) -> Any:
        """获取值

        Returns:
            节点返回的值
        """
        return self.value

    def set_cache_path(self, cache_path: str) -> None:
        """设置缓存路径

        Args:
            cache_path: 缓存文件或数据集的路径
        """
        self.cache_path = cache_path
        system_logger.debug(
            f"[Namespace][{self.namespace_id}]：设置缓存路径，node_name={self.node_name}, cache_path={cache_path}"
        )

    def get_cache_path(self) -> Optional[str]:
        """获取缓存路径

        Returns:
            缓存文件或数据集的路径，如果没有则返回None
        """
        return self.cache_path

    def __str__(self) -> str:
        """字符串表示

        Returns:
            命名空间的字符串表示
        """
        return f"Namespace(id={self.namespace_id}, name={self.node_name})"


class NamespaceRegistry:
    """命名空间注册表

    管理多个命名空间，支持节点间数据传递

    属性:
        registry_id: 注册表唯一标识
        namespaces: 命名空间映射表，键为节点名称，值为对应的命名空间
    """

    def __init__(self):
        """初始化命名空间注册表"""
        self.registry_id = f"registry_{uuid4().hex[:8]}"
        self.namespaces: Dict[str, Namespace] = {}

        system_logger.debug(f"[Registry][{self.registry_id}]：创建命名空间注册表")

    def get_namespace(self, node_name: str) -> Namespace:
        """获取或创建节点的命名空间

        Args:
            node_name: 节点名称

        Returns:
            节点对应的命名空间
        """
        if node_name not in self.namespaces:
            self.namespaces[node_name] = Namespace(node_name)
            system_logger.debug(
                f"[Registry][{self.registry_id}]：创建命名空间，node_name={node_name}"
            )
        return self.namespaces[node_name]

    def set_value(self, node_name: str, value: Any) -> None:
        """设置节点命名空间的值

        Args:
            node_name: 节点名称
            value: 值
        """
        namespace = self.get_namespace(node_name)
        namespace.set_value(value)
        system_logger.debug(
            f"[Registry][{self.registry_id}]：设置命名空间值，node_name={node_name}"
        )

    def get_value(self, node_name: str, default: Any = None) -> Any:
        """获取节点命名空间的值

        Args:
            node_name: 节点名称
            default: 默认值，如果节点不存在则返回此值

        Returns:
            节点返回的值，如果节点不存在则返回默认值
        """
        if node_name not in self.namespaces:
            system_logger.debug(
                f"[Registry][{self.registry_id}]：获取不存在的命名空间，node_name={node_name}"
            )
            return default
        system_logger.debug(
            f"[Registry][{self.registry_id}]：获取命名空间值，node_name={node_name}"
        )
        return self.namespaces[node_name].get_value()

    def set_cache_path(self, node_name: str, cache_path: str) -> None:
        """设置节点命名空间的缓存路径

        Args:
            node_name: 节点名称
            cache_path: 缓存文件或数据集的路径
        """
        namespace = self.get_namespace(node_name)
        namespace.set_cache_path(cache_path)
        system_logger.debug(
            f"[Registry][{self.registry_id}]：设置命名空间缓存路径，node_name={node_name}, cache_path={cache_path}"
        )

    def get_cache_path(
        self, node_name: str, default: Optional[str] = None
    ) -> Optional[str]:
        """获取节点命名空间的缓存路径

        Args:
            node_name: 节点名称
            default: 默认值，如果节点不存在则返回此值

        Returns:
            缓存文件或数据集的路径，如果节点不存在或没有缓存路径则返回默认值
        """
        if node_name not in self.namespaces:
            system_logger.debug(
                f"[Registry][{self.registry_id}]：获取不存在的命名空间的缓存路径，node_name={node_name}"
            )
            return default
        system_logger.debug(
            f"[Registry][{self.registry_id}]：获取命名空间缓存路径，node_name={node_name}"
        )
        return self.namespaces[node_name].get_cache_path()

    def clear(self) -> None:
        """清空所有命名空间"""
        self.namespaces.clear()
        system_logger.debug(f"[Registry][{self.registry_id}]：清空命名空间注册表")

    def clear_namespace_value(self, node_name: str) -> None:
        """清空特定节点命名空间的值，但保留命名空间

        Args:
            node_name: 节点名称
        """
        if node_name in self.namespaces:
            self.namespaces[node_name].set_value(None)
            system_logger.debug(
                f"[Registry][{self.registry_id}]：清空命名空间值，node_name={node_name}"
            )
        else:
            system_logger.debug(
                f"[Registry][{self.registry_id}]：尝试清空不存在的命名空间值，node_name={node_name}"
            )

    def __str__(self) -> str:
        """字符串表示

        Returns:
            注册表的字符串表示
        """
        return f"NamespaceRegistry(id={self.registry_id}, namespaces={len(self.namespaces)})"
