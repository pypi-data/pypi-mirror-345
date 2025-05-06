#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化配置接口模块

提供DataWhale数据目录和运行时目录的配置接口
"""

# 从init_config模块导入
from datawhale.infrastructure_pro.init_config import (
    set_data_dir,
    set_runtime_dir,
    get_data_dir,
    get_runtime_dir,
    set_user_log_level,
    set_system_log_level,
    get_user_log_level,
    get_system_log_level,
)

# 从tushare_config模块导入
from datawhale.domain_pro.tushare_config import (
    get_tushare_token,
    set_tushare_token,
    init_tushare_token,
    get_pro_api,
)

__all__ = [
    # 基础配置
    "set_data_dir",
    "set_runtime_dir",
    "get_data_dir",
    "get_runtime_dir",
    # 日志配置
    "set_user_log_level",
    "set_system_log_level",
    "get_user_log_level",
    "get_system_log_level",
    # TuShare配置
    "get_tushare_token",
    "set_tushare_token",
    "init_tushare_token",
    "get_pro_api",
]
