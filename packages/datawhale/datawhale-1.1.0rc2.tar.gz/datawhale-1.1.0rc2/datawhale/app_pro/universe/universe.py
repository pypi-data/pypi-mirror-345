#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
证券代码过滤器类的实现

提供基于各种条件筛选证券代码的功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Set
from datetime import datetime, timedelta

# 导入相关模块
from datawhale.domain_pro.panel_trading_status import (
    TRADING_STATUS_PANEL_NAME,
    TRADING_STATUS_NOT_LISTED,
    TRADING_STATUS_TRADING,
    TRADING_STATUS_SUSPENDED,
    TRADING_STATUS_DELISTED,
)
from datawhale.domain_pro.panel_st.st_panel import (
    ST_STATUS_NORMAL,
    ST_STATUS_ST,
    ST_PANEL_NAME,
)
from datawhale.domain_pro.panel_new_stock import (
    NEW_STOCK_PANEL_NAME,
    NEW_STOCK_STATUS_NORMAL,
    NEW_STOCK_STATUS_NEW,
)
from datawhale.domain_pro.field_standard import StandardFields
from datawhale.infrastructure_pro.storage import dw_panel_exists, dw_panel_query

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)


class Universe:
    """
    证券代码过滤器类

    根据各种条件过滤证券代码，提供链式调用接口
    """

    def __init__(self, security_types: List[str] = None):
        """
        初始化证券代码过滤器

        Args:
            security_types: 证券类型列表，如果为None则包括所有类型
        """
        self.security_types = security_types
        self.filter_conditions = {}

        # 加载当前月份的交易状态数据
        self._preload_current_month_trading_status()

    def _preload_current_month_trading_status(self):
        """
        加载当前月份的交易状态数据
        """
        try:
            # 获取当前日期并计算当前月份
            current_date = datetime.now()
            current_year_month = current_date.strftime("%Y-%m")

            # 检查交易状态面板是否存在
            if not dw_panel_exists(TRADING_STATUS_PANEL_NAME):
                logger.error(f"交易状态面板数据不存在: {TRADING_STATUS_PANEL_NAME}")
                self.trading_status_df = pd.DataFrame()
                return

            # 准备查询参数
            query_params = {
                "panel_name": TRADING_STATUS_PANEL_NAME,
                "field_values": {"year_month": current_year_month},
                "sort_by": StandardFields.TRADE_DATE,  # 按日期排序
            }

            # 如果指定了证券类型，添加到field_values中
            if self.security_types and len(self.security_types) > 0:
                query_params["field_values"][StandardFields.SECURITY_TYPE] = (
                    self.security_types[0]
                )

            # 从面板数据中加载当前月份的交易状态数据
            self.trading_status_df = dw_panel_query(**query_params)

            # 确保交易状态DataFrame不为None
            if self.trading_status_df is None:
                logger.warning("当前月份的交易状态数据为空")
                self.trading_status_df = pd.DataFrame()
                return

            # 如果DataFrame为空，说明该月份没有数据
            if self.trading_status_df.empty:
                logger.warning(f"当前月份({current_year_month})没有交易状态数据")
                return

            # 记录加载的数据情况
            rows_count = len(self.trading_status_df)
            if StandardFields.TRADE_DATE in self.trading_status_df.columns:
                unique_dates = len(
                    self.trading_status_df[StandardFields.TRADE_DATE].unique()
                )
                logger.info(
                    f"成功加载当前月份({current_year_month})交易状态数据: {rows_count}行, {unique_dates}个交易日"
                )
            else:
                logger.warning(
                    f"交易状态数据中缺少日期字段: {StandardFields.TRADE_DATE}"
                )

        except Exception as e:
            logger.error(f"加载当前月份交易状态数据失败: {str(e)}")
            self.trading_status_df = pd.DataFrame()

    def filter(
        self,
        trading_status: str = None,
        exclude_st: bool = True,
        exclude_new_stock: bool = False,
    ) -> "Universe":
        """
        根据交易状态、ST状态和次新股状态过滤证券

        Args:
            trading_status: 交易状态，默认为None(不进行交易状态过滤)
                           可选值: None(不过滤), U(未上市), T(正常交易), S(停牌), D(退市)
            exclude_st: 是否排除ST股票，默认为True，表示排除ST股票
            exclude_new_stock: 是否排除次新股，默认为False，表示不排除次新股

        Returns:
            Universe: 当前对象，支持链式调用
        """
        # 验证交易状态参数
        valid_statuses = [
            None,
            TRADING_STATUS_NOT_LISTED,
            TRADING_STATUS_TRADING,
            TRADING_STATUS_SUSPENDED,
            TRADING_STATUS_DELISTED,
        ]
        if trading_status not in valid_statuses:
            logger.error(
                f"无效的交易状态值: {trading_status}，使用默认值: None (不过滤)"
            )
            trading_status = None

        # 保存过滤条件
        self.filter_conditions["trading_status"] = trading_status
        self.filter_conditions["exclude_st"] = exclude_st
        self.filter_conditions["exclude_new_stock"] = exclude_new_stock

        return self

    def _load_trading_status_for_date(self, trading_date: str) -> pd.DataFrame:
        """
        加载指定日期的交易状态数据

        如果预加载的数据中已包含该日期，则直接使用预加载数据
        否则从存储中加载数据
        如果指定日期在未来，则尝试使用当前月份的最新数据

        Args:
            trading_date: 交易日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 包含指定日期交易状态的DataFrame
        """
        try:
            # 从日期计算所属年月
            date_obj = datetime.strptime(trading_date, "%Y-%m-%d")
            year_month = date_obj.strftime("%Y-%m")

            # 检查是否为未来日期
            current_date = datetime.now()

            if date_obj > current_date:
                logger.warning(
                    f"请求的日期({trading_date})在未来，将尝试使用当前月份的最新数据"
                )
                current_year_month = current_date.strftime("%Y-%m")
                # 修改year_month为当前月份，便于后续处理
                year_month = current_year_month

            # 检查预加载数据是否已包含该日期
            if (
                not self.trading_status_df.empty
                and StandardFields.TRADE_DATE in self.trading_status_df.columns
            ):
                # 如果预加载数据包含该日期，则直接使用
                date_mask = (
                    self.trading_status_df[StandardFields.TRADE_DATE] == trading_date
                )
                if date_mask.any():
                    logger.debug(f"使用预加载数据获取{trading_date}的交易状态")
                    return self.trading_status_df[date_mask]

                # 如果是未来日期，尝试获取预加载数据中的最新日期
                if date_obj > current_date:
                    latest_date = self.trading_status_df[
                        StandardFields.TRADE_DATE
                    ].max()
                    if latest_date:
                        logger.info(
                            f"使用预加载数据中的最新日期({latest_date})代替未来日期({trading_date})"
                        )
                        latest_mask = (
                            self.trading_status_df[StandardFields.TRADE_DATE]
                            == latest_date
                        )
                        return self.trading_status_df[latest_mask]

            # 检查是否存在交易状态面板
            if not dw_panel_exists(TRADING_STATUS_PANEL_NAME):
                logger.error(f"交易状态面板数据不存在: {TRADING_STATUS_PANEL_NAME}")
                return pd.DataFrame()

            # 准备查询参数
            query_params = {
                "panel_name": TRADING_STATUS_PANEL_NAME,
                "field_values": {"year_month": year_month},
                "sort_by": StandardFields.TRADE_DATE,
            }

            # 如果指定了证券类型，添加到field_values中
            if self.security_types and len(self.security_types) > 0:
                query_params["field_values"][StandardFields.SECURITY_TYPE] = (
                    self.security_types[0]
                )

            # 查询月度交易状态数据
            month_status_df = dw_panel_query(**query_params)

            if month_status_df is None or month_status_df.empty:
                logger.warning(f"月份{year_month}的交易状态数据为空")
                # 如果是未来月份且数据为空，尝试查询当前月份的数据
                if date_obj > current_date and year_month != current_date.strftime(
                    "%Y-%m"
                ):
                    current_year_month = current_date.strftime("%Y-%m")
                    logger.info(f"尝试获取当前月份({current_year_month})的数据")
                    query_params["field_values"]["year_month"] = current_year_month
                    month_status_df = dw_panel_query(**query_params)

                    if month_status_df is None or month_status_df.empty:
                        logger.warning(
                            f"当前月份({current_year_month})的交易状态数据也为空"
                        )
                        return pd.DataFrame()
                else:
                    return pd.DataFrame()

            # 检查日期字段是否存在
            if StandardFields.TRADE_DATE in month_status_df.columns:
                # 如果是未来日期，找到最新的可用交易日
                if date_obj > current_date:
                    latest_date = month_status_df[StandardFields.TRADE_DATE].max()
                    if latest_date:
                        logger.info(
                            f"使用最新的交易日期({latest_date})代替未来日期({trading_date})"
                        )
                        date_status_df = month_status_df[
                            month_status_df[StandardFields.TRADE_DATE] == latest_date
                        ]
                        if not date_status_df.empty:
                            return date_status_df

                # 过滤出特定日期的数据
                date_status_df = month_status_df[
                    month_status_df[StandardFields.TRADE_DATE] == trading_date
                ]

                if date_status_df.empty:
                    # 如果没有精确匹配的日期，查找最近的交易日
                    valid_dates = [
                        d
                        for d in month_status_df[StandardFields.TRADE_DATE].unique()
                        if d <= trading_date
                    ]
                    if valid_dates:
                        nearest_date = max(valid_dates)
                        logger.warning(f"使用最近的交易日期: {nearest_date}")
                        date_status_df = month_status_df[
                            month_status_df[StandardFields.TRADE_DATE] == nearest_date
                        ]

                if not date_status_df.empty:
                    logger.info(f"成功加载日期{trading_date}的交易状态数据")
                    return date_status_df

            logger.error(f"无法获取日期{trading_date}的交易状态数据")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"加载日期{trading_date}的交易状态数据失败: {str(e)}")
            return pd.DataFrame()

    def _load_st_status_for_date(self, trading_date: str) -> pd.DataFrame:
        """
        加载指定日期的ST状态数据

        Args:
            trading_date: 交易日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 包含指定日期ST状态的DataFrame，如果数据不存在则返回空DataFrame
        """
        try:
            # 检查ST面板是否存在
            if not dw_panel_exists(ST_PANEL_NAME):
                logger.error(f"ST状态面板数据不存在: {ST_PANEL_NAME}")
                return pd.DataFrame()

            # 准备查询参数
            query_params = {
                "panel_name": ST_PANEL_NAME,
                "field_values": None,  # ST面板按日期索引，不用额外指定field_values
                "sort_by": StandardFields.TRADE_DATE,
            }

            # 从面板数据中查询ST状态
            st_df = dw_panel_query(**query_params)

            if st_df is None or st_df.empty:
                logger.warning("ST状态面板数据为空")
                return pd.DataFrame()

            # 过滤出特定日期的ST状态数据
            if StandardFields.TRADE_DATE in st_df.columns:
                date_st_df = st_df[st_df[StandardFields.TRADE_DATE] == trading_date]

                if date_st_df.empty:
                    # 如果没有精确匹配的日期，查找最近的交易日
                    valid_dates = [
                        d
                        for d in st_df[StandardFields.TRADE_DATE].unique()
                        if d <= trading_date
                    ]
                    if valid_dates:
                        nearest_date = max(valid_dates)
                        logger.warning(f"使用最近的ST状态日期: {nearest_date}")
                        date_st_df = st_df[
                            st_df[StandardFields.TRADE_DATE] == nearest_date
                        ]

                if not date_st_df.empty:
                    logger.info(f"成功加载日期{trading_date}的ST状态数据")
                    return date_st_df

            logger.error(f"无法获取日期{trading_date}的ST状态数据")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"加载日期{trading_date}的ST状态数据失败: {str(e)}")
            return pd.DataFrame()

    def _load_new_stock_status_for_date(self, trading_date: str) -> pd.DataFrame:
        """
        加载指定日期的次新股状态数据

        Args:
            trading_date: 交易日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 包含指定日期次新股状态的DataFrame，如果数据不存在则返回空DataFrame
        """
        try:
            # 检查次新股面板是否存在
            if not dw_panel_exists(NEW_STOCK_PANEL_NAME):
                logger.error(f"次新股状态面板数据不存在: {NEW_STOCK_PANEL_NAME}")
                return pd.DataFrame()

            # 从日期获取年份
            year = trading_date.split("-")[0]

            # 准备查询参数
            query_params = {
                "panel_name": NEW_STOCK_PANEL_NAME,
                "field_values": {"year": year},
                "sort_by": StandardFields.TRADE_DATE,
            }

            # 从面板数据中查询次新股状态
            new_stock_df = dw_panel_query(**query_params)

            if new_stock_df is None or new_stock_df.empty:
                logger.warning(f"年份{year}的次新股状态面板数据为空")
                return pd.DataFrame()

            # 过滤出特定日期的次新股状态数据
            if StandardFields.TRADE_DATE in new_stock_df.columns:
                date_new_stock_df = new_stock_df[
                    new_stock_df[StandardFields.TRADE_DATE] == trading_date
                ]

                if date_new_stock_df.empty:
                    # 如果没有精确匹配的日期，查找最近的交易日
                    valid_dates = [
                        d
                        for d in new_stock_df[StandardFields.TRADE_DATE].unique()
                        if d <= trading_date
                    ]
                    if valid_dates:
                        nearest_date = max(valid_dates)
                        logger.warning(f"使用最近的次新股状态日期: {nearest_date}")
                        date_new_stock_df = new_stock_df[
                            new_stock_df[StandardFields.TRADE_DATE] == nearest_date
                        ]

                if not date_new_stock_df.empty:
                    logger.info(f"成功加载日期{trading_date}的次新股状态数据")
                    return date_new_stock_df

            logger.error(f"无法获取日期{trading_date}的次新股状态数据")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"加载日期{trading_date}的次新股状态数据失败: {str(e)}")
            return pd.DataFrame()

    def get(self, trading_date: str = None) -> List[str]:
        """
        根据过滤条件获取符合条件的证券代码列表

        Args:
            trading_date: 交易日期，格式为YYYY-MM-DD，如果为None则使用当前日期

        Returns:
            List[str]: 符合条件的证券代码列表
        """
        # 如果未指定日期，使用当前日期
        if trading_date is None:
            trading_date = datetime.now().strftime("%Y-%m-%d")

        # 获取过滤条件
        trading_status = self.filter_conditions.get("trading_status", None)
        exclude_st = self.filter_conditions.get("exclude_st", True)
        exclude_new_stock = self.filter_conditions.get("exclude_new_stock", False)

        # 获取指定日期的交易状态数据
        date_panel = self._load_trading_status_for_date(trading_date)

        if date_panel.empty:
            logger.warning(f"日期{trading_date}没有交易状态数据")
            return []

        # 列名是股票代码，值是交易状态(T/S/U/D)
        # 需要去掉日期和security_type列
        columns_to_drop = [
            col
            for col in date_panel.columns
            if col
            in [StandardFields.TRADE_DATE, StandardFields.SECURITY_TYPE, "year_month"]
        ]
        status_df = date_panel.drop(columns=columns_to_drop)

        # 将DataFrame转为宽格式，行索引为股票代码，值为交易状态
        # 在宽格式下，我们可以用矩阵操作找到所有符合特定交易状态的股票
        result_codes = []

        # 扁平化处理第一行数据
        if len(status_df) > 0:
            first_row = status_df.iloc[0]
            # 如果trading_status为None，不进行交易状态过滤，获取所有股票
            if trading_status is None:
                result_codes = list(first_row.index)
            else:
                # 否则只获取符合指定交易状态的股票
                for stock_code, status in first_row.items():
                    if status == trading_status:
                        result_codes.append(stock_code)

        # 如果需要排除ST股票，加载ST状态数据并过滤
        if exclude_st and result_codes:
            st_panel = self._load_st_status_for_date(trading_date)

            if not st_panel.empty:
                # 去掉日期列，只保留股票代码列
                columns_to_drop = [
                    col
                    for col in st_panel.columns
                    if col in [StandardFields.TRADE_DATE]
                ]
                st_status_df = st_panel.drop(columns=columns_to_drop)

                if len(st_status_df) > 0:
                    # 获取第一行数据，包含所有股票的ST状态
                    st_row = st_status_df.iloc[0]

                    # 过滤掉ST股票
                    non_st_codes = []
                    for stock_code in result_codes:
                        # 只有在ST面板中且状态为非ST的股票才会被保留
                        # 注意：如果股票未出现在ST面板中，说明该股票从未被ST过，应该被保留
                        if (
                            stock_code not in st_row
                            or st_row[stock_code] == ST_STATUS_NORMAL
                        ):
                            non_st_codes.append(stock_code)

                    st_count = len(result_codes) - len(non_st_codes)
                    logger.info(f"过滤掉{st_count}只ST股票")
                    result_codes = non_st_codes

        # 如果需要排除次新股，加载次新股状态数据并过滤
        if exclude_new_stock and result_codes:
            new_stock_panel = self._load_new_stock_status_for_date(trading_date)

            if not new_stock_panel.empty:
                # 去掉日期列，只保留股票代码列
                columns_to_drop = [
                    col
                    for col in new_stock_panel.columns
                    if col in [StandardFields.TRADE_DATE, "year"]
                ]
                new_stock_status_df = new_stock_panel.drop(columns=columns_to_drop)

                if len(new_stock_status_df) > 0:
                    # 获取第一行数据，包含所有股票的次新股状态
                    new_stock_row = new_stock_status_df.iloc[0]

                    # 过滤掉次新股
                    non_new_stock_codes = []
                    for stock_code in result_codes:
                        # 如果股票不在次新股面板中或者状态为非次新股，则保留
                        if (
                            stock_code not in new_stock_row.index
                            or new_stock_row[stock_code] == NEW_STOCK_STATUS_NORMAL
                        ):
                            non_new_stock_codes.append(stock_code)

                    new_stock_count = len(result_codes) - len(non_new_stock_codes)
                    logger.info(f"过滤掉{new_stock_count}只次新股")
                    result_codes = non_new_stock_codes

        logger.info(f"找到{len(result_codes)}只符合条件的证券")
        return result_codes
