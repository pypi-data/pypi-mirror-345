#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
领域层模块

包含数据标准化、字段标准化、代码标准化和日期标准化等功能
"""

# 从data_standard模块导入标准化函数
from datawhale.domain_pro.data_standard import standardize_dataframe

# 导入交易日历信息模块（为了方便直接从domain_pro中访问）
from datawhale.domain_pro.info_trade_calendar import (
    fetch_trade_calendar,
    save_trade_calendar_info,
    update_trade_calendar_info,
    is_trading_day,
    get_prev_trading_day,
    get_next_trading_day,
    TRADE_CALENDAR_DATASET,
)

# 导入信息模块
from datawhale.domain_pro.info_listing_and_delisting import (
    fetch_listing_delisting_info,
    fetch_all_listing_delisting_info,
    update_listing_delisting_info,
)

from datawhale.domain_pro.info_suspend import (
    fetch_suspend_info,
    update_suspend_info,
    get_suspend_stocks,
)

# 导入面板数据模块
from datawhale.domain_pro.panel_trading_status import (
    create_trading_status_panel,
    update_trading_status_panel,
    get_trading_status,
)

__all__ = [
    # 数据标准化功能
    "standardize_dataframe",
    # 上市退市信息
    "fetch_listing_delisting_info",
    "fetch_all_listing_delisting_info",
    "update_listing_delisting_info",
    # 交易日历信息功能
    "fetch_trade_calendar",
    "save_trade_calendar_info",
    "update_trade_calendar_info",
    "is_trading_day",
    "get_prev_trading_day",
    "get_next_trading_day",
    "TRADE_CALENDAR_DATASET",
    # 停复牌信息
    "fetch_suspend_info",
    "update_suspend_info",
    "get_suspend_stocks",
    # 交易状态面板
    "create_trading_status_panel",
    "update_trading_status_panel",
    "get_trading_status",
]
