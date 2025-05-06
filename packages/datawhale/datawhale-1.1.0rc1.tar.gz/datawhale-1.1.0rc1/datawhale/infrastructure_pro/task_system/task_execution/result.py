#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TypeVar, Generic, Optional, Dict, Any

T = TypeVar("T")


class Result(Generic[T]):
    """结果封装类

    用于统一封装操作结果，包含成功/失败状态及相关数据/错误信息。
    作为基础设施层的核心组件，为上层应用提供一致的结果处理机制。
    遵循函数式编程的Result模式，避免异常传播，提高代码可读性。
    """

    def __init__(
        self,
        success: bool,
        data: Optional[T] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """初始化结果对象

        Args:
            success: 是否成功
            data: 成功时的数据
            error: 失败时的错误信息
            metadata: 与结果相关的元数据
        """
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata

    @classmethod
    def success(cls, data: T, metadata: Optional[Dict[str, Any]] = None) -> "Result[T]":
        """创建成功结果

        Args:
            data: 结果数据
            metadata: 与结果相关的元数据

        Returns:
            Result[T]: 成功的结果对象
        """
        return cls(True, data, metadata=metadata)

    @classmethod
    def failure(
        cls, error: str, metadata: Optional[Dict[str, Any]] = None
    ) -> "Result[T]":
        """创建失败结果

        Args:
            error: 错误信息
            metadata: 与结果相关的元数据

        Returns:
            Result[T]: 失败的结果对象
        """
        return cls(False, error=error, metadata=metadata)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Result":
        """从字典创建结果对象

        Args:
            data: 包含结果信息的字典

        Returns:
            Result: 结果对象
        """
        success = data.get("success", False)
        result_data = data.get("data")
        error = data.get("error")
        metadata = data.get("metadata")

        return cls(success=success, data=result_data, error=error, metadata=metadata)

    def __str__(self) -> str:
        """字符串表示

        Returns:
            str: 结果的字符串表示
        """
        if self.success:
            return f"Success: {self.data}"
        return f"Failure: {self.error}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        用于序列化和日志记录

        Returns:
            Dict[str, Any]: 结果的字典表示
        """
        result = {"success": self.success}
        if self.success and self.data is not None:
            result["data"] = self.data
        if not self.success and self.error is not None:
            result["error"] = self.error
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result
