#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, Dict, Any, Union
import pandas as pd


class Layer:
    """文件层对象

    用于实现多层文件夹的管理机制，每一层负责一级目录结构。

    属性:
        level: 层级编号，从0开始递增
        field: 用于生成路径的字段名，None表示固定层
        prev_layer: 前一层对象的引用
        next_layer: 后一层对象的引用
    """

    def __init__(
        self,
        level: int,
        field: Optional[str] = None,
        prev_layer: Optional["Layer"] = None,
        next_layer: Optional["Layer"] = None,
    ):
        """初始化文件层对象

        Args:
            level: 层级编号，从0开始递增
            field: 用于生成路径的字段名，None表示固定层
            prev_layer: 前一层对象
            next_layer: 后一层对象
        """
        self.level = level
        self.field = field
        self.prev_layer = prev_layer
        self.next_layer = next_layer

    def __str__(self) -> str:
        """返回层的字符串表示

        Returns:
            层级和字段的字符串表示
        """
        return f"Layer(level={self.level}, field={self.field})"

    def __repr__(self) -> str:
        """返回层的详细字符串表示

        Returns:
            包含所有主要属性的字符串表示
        """
        return (
            f"Layer(level={self.level}, field={self.field}, "
            f"prev_layer={self.prev_layer.level if self.prev_layer else None}, "
            f"next_layer={self.next_layer.level if self.next_layer else None})"
        )

    def link_next(self, next_layer: "Layer") -> None:
        """链接到下一层

        Args:
            next_layer: 下一层对象
        """
        self.next_layer = next_layer
        next_layer.prev_layer = self

    def link_prev(self, prev_layer: "Layer") -> None:
        """链接到上一层

        Args:
            prev_layer: 上一层对象
        """
        self.prev_layer = prev_layer
        prev_layer.next_layer = self
