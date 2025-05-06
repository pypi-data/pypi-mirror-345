#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DataWhale本地存储接口模块

提供DataWhale本地数据集和面板数据的存储、查询、删除等操作
"""

# 从infrastructure_pro.storage模块导入本地存储相关接口
from datawhale.infrastructure_pro.storage import (
    dw_create_dataset,
    dw_save,
    dw_query,
    dw_delete,
    dw_exists,
    dw_query_last_line,
    dw_query_last_n_lines,
    # DataWhale本地面板数据接口
    dw_create_panel,
    dw_panel_save,
    dw_panel_query,
    dw_panel_delete,
    dw_panel_exists,
    dw_panel_get,
    dw_panel_read_last_line,
    dw_panel_read_last_n_lines,
)

__all__ = [
    "dw_create_dataset",
    "dw_save",
    "dw_query",
    "dw_delete",
    "dw_exists",
    "dw_query_last_line",
    "dw_query_last_n_lines",
    # DataWhale本地面板数据接口
    "dw_create_panel",
    "dw_panel_save",
    "dw_panel_query",
    "dw_panel_delete",
    "dw_panel_exists",
    "dw_panel_get",
    "dw_panel_read_last_line",
    "dw_panel_read_last_n_lines",
]
