#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""任务阶段模块，提供Graph的批量执行和阶段管理功能"""

# 从本模块导入组件
from .stage import Stage, StageStatus

__all__ = ["Stage", "StageStatus"]
