#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DataWhale 异常类模块

提供各种模块使用的异常类
"""

# 从infrastructure_pro模块导入
from datawhale.infrastructure_pro.exceptions import (
    TaskExecutionError,
    StorageError,
    BatchDownloadError,
)

__all__ = ["TaskExecutionError", "StorageError", "BatchDownloadError"]
