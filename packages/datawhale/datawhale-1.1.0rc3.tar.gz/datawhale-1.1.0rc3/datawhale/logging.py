#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志接口模块

提供用户日志和系统日志接口
"""

# 从logging模块导入
from datawhale.infrastructure_pro.logging import get_user_logger, get_system_logger

__all__ = [
    "get_user_logger",
    "get_system_logger",
]
