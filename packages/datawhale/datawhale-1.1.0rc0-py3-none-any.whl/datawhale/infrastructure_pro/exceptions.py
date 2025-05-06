#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提供infrastructure_pro模块的异常类
"""


class TaskExecutionError(Exception):
    """任务执行异常"""

    def __init__(self, message="任务执行错误", traceback=None):
        super().__init__(message)
        self.traceback = traceback


class StorageError(Exception):
    """存储服务异常"""

    pass


class BatchDownloadError(Exception):
    """批量下载异常"""

    pass
