#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置系统接口模块

提供配置管理和配置加载的功能接口
"""

# 从config模块导入
from datawhale.infrastructure_pro.config import (
    ConfigManager,
    config,
    get_config,
)

__all__ = [
    "ConfigManager",
    "config",
    "get_config",
]
