#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存储服务接口模块

提供数据集和面板数据的存储、查询、删除等基础操作
"""

# 从infrastructure_pro.storage模块导入
from datawhale.infrastructure_pro.storage import (
    Dataset,
    create_dataset,
    save,
    query,
    delete,
    exists,
    infer_dtypes,
    query_last_line,
    query_last_n_lines,
    Panel,
    PanelMetaInfo,
    # 面板数据基础接口
    panel_create,
    panel_save,
    panel_query,
    panel_delete,
    panel_exists,
    panel_get_all_entities,
    panel_get_entity_data,
    panel_get_date_data,
    panel_get_stats,
    panel_read_last_line,
    panel_read_last_n_lines,
)

__all__ = [
    "Dataset",
    "create_dataset",
    "save",
    "query",
    "delete",
    "exists",
    "query_last_line",
    "query_last_n_lines",
    "infer_dtypes",
    "Panel",
    "PanelMetaInfo",
    # 面板数据基础接口
    "panel_create",
    "panel_save",
    "panel_query",
    "panel_delete",
    "panel_exists",
    "panel_get_all_entities",
    "panel_get_entity_data",
    "panel_get_date_data",
    "panel_get_stats",
    "panel_read_last_line",
    "panel_read_last_n_lines",
]
