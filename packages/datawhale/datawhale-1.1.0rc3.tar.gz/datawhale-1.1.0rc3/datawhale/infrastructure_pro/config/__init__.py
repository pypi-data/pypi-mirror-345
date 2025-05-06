#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 从本模块导入组件
from .config_manager import ConfigManager
from .decorators import config, get_config

# 保持向后兼容性的导出
__all__ = ["ConfigManager", "config", "get_config"]
