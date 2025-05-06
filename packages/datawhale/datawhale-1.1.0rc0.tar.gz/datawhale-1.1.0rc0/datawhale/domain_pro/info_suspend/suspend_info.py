#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
停复牌信息模块

提供获取和更新停复牌信息的功能
"""

import pandas as pd
import tushare as ts
from typing import Optional
from datetime import datetime, timedelta
import os

from datawhale.domain_pro.field_standard import StandardFields, get_fields_type
from datawhale.domain_pro import standardize_dataframe
from datawhale.domain_pro.datetime_standard import to_standard_date
from datawhale.infrastructure_pro.storage import (
    dw_create_dataset,
    dw_save,
    dw_exists,
    dw_query,
    dw_query_last_line,
)

# 导入TuShare配置
from datawhale.domain_pro.tushare_config import get_pro_api

# 获取用户日志记录器
from datawhale.infrastructure_pro.logging import get_user_logger

logger = get_user_logger(__name__)

# TuShare数据源名称
TUSHARE_SOURCE = "tushare"

# 需要排除的特殊股票代码列表
EXCLUDED_STOCK_CODES = ["T00018.SH"]

# 停复牌信息数据集名称
SUSPEND_INFO_DATASET = "suspend_info"

# 需要保留的标准字段列表
REQUIRED_COLUMNS = [
    StandardFields.STOCK_CODE,  # 股票代码
    StandardFields.TRADE_DATE,  # 交易日期
    StandardFields.SUSPEND_TYPE,  # 停复牌类型
    StandardFields.SUSPEND_TIMING,  # 日内停牌时间段
]

# 日期字段列表
DATE_COLUMNS = [StandardFields.TRADE_DATE]

# 排序字段
SORT_BY_FIELD = StandardFields.TRADE_DATE  # 按交易日期字段排序


def fetch_suspend_info(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ts_code: Optional[str] = None,
    suspend_type: str = "S",
) -> pd.DataFrame:
    """
    从远程数据源获取停复牌信息

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
        ts_code: 股票代码，默认为None获取所有股票
        suspend_type: 停复牌类型，S-停牌，R-复牌，默认为S

    Returns:
        pd.DataFrame: 包含停复牌信息的DataFrame

    Notes:
        TuShare API在单次调用中限制最多返回5000条记录。对于大量数据（如60万条），
        本函数应进一步优化为分批次获取数据，例如按周或按月划分时间区间进行多次请求，
        并合并结果返回。
    """
    # 如果未指定日期，则默认获取近30天的数据
    if not start_date or not end_date:
        today = datetime.now()
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        if not start_date:
            # 默认获取30天的数据
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    # 标准化日期
    start_date = to_standard_date(start_date)
    end_date = to_standard_date(end_date)
    if not start_date or not end_date:
        logger.error(f"日期格式无效: start_date={start_date}, end_date={end_date}")
        return pd.DataFrame()

    logger.info(
        f"开始从远程接口获取停复牌信息: start_date={start_date}, end_date={end_date}, suspend_type={suspend_type}"
    )

    # TODO: 这里可以优化为分批获取数据的实现
    # 例如：
    # 1. 计算start_date和end_date之间的时间跨度
    # 2. 如果跨度较大（如超过30天），按周或按月拆分为多个时间区间
    # 3. 对每个时间区间分别调用_fetch_suspend_info_from_remote
    # 4. 合并多次请求的结果

    # 直接从远程接口获取
    return _fetch_suspend_info_from_remote(start_date, end_date, ts_code, suspend_type)


def _fetch_suspend_info_from_remote(
    start_date: str,
    end_date: str,
    ts_code: Optional[str] = None,
    suspend_type: str = "S",
) -> pd.DataFrame:
    """
    从远程接口获取停复牌信息

    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
        ts_code: 股票代码，默认为None获取所有股票
        suspend_type: 停复牌类型，S-停牌，R-复牌，默认为S

    Returns:
        pd.DataFrame: 包含停复牌信息的DataFrame

    Notes:
        TuShare API在单次调用中限制最多返回5000条记录。当需要获取大量数据（如60万条）时，
        需要采用分批下载策略：
        1. 按时间区间拆分请求，确保每个请求返回的数据不超过5000条
        2. 对于大规模数据，建议按月或按周进行拆分请求
        3. 可以使用多线程或异步方式提高下载效率
        4. 注意控制请求频率，避免触发TuShare的频率限制
    """
    logger.info(
        f"从远程接口获取停复牌信息: start_date={start_date}, end_date={end_date}, suspend_type={suspend_type}"
    )

    try:
        # 转换日期格式为TuShare格式（YYYYMMDD）
        start_date_ts = start_date.replace("-", "")
        end_date_ts = end_date.replace("-", "")

        # 获取TuShare接口对象
        pro = get_pro_api()
        if not pro:
            logger.error("获取TuShare API失败")
            return pd.DataFrame()

        # 查询停复牌信息
        result = pro.suspend_d(
            ts_code=ts_code,
            start_date=start_date_ts,
            end_date=end_date_ts,
            suspend_type=suspend_type,
        )

        if result is None or result.empty:
            logger.warning(
                f"未查询到停复牌信息: start_date={start_date}, end_date={end_date}"
            )
            return pd.DataFrame()

        # 过滤掉特殊证券代码
        original_size = len(result)
        if "ts_code" in result.columns:
            # 先输出特殊代码记录的详细信息
            special_records = result[result["ts_code"].isin(EXCLUDED_STOCK_CODES)]
            if not special_records.empty:
                logger.info(f"发现特殊证券代码记录:\n{special_records}")

            # 执行过滤
            result = result[~result["ts_code"].isin(EXCLUDED_STOCK_CODES)]
            filtered_size = len(result)
            if original_size != filtered_size:
                logger.info(
                    f"已过滤掉 {original_size - filtered_size} 条特殊证券代码记录"
                )

        # 标准化处理
        result = standardize_dataframe(
            df=result,
            source=TUSHARE_SOURCE,
            code_field="ts_code",  # TuShare中的证券代码字段名
            date_fields=DATE_COLUMNS,
            required_columns=REQUIRED_COLUMNS,
            sort_by=SORT_BY_FIELD,  # 使用标准化后的字段名
            ascending=True,  # 升序排序
        )

        logger.info(f"从远程接口获取停复牌信息完成: 共{len(result)}条记录")

        # 保存到本地存储以便下次使用
        try:
            save_suspend_info(result)
        except Exception as e:
            logger.warning(f"保存停复牌信息到本地存储失败: {str(e)}")

        return result

    except Exception as e:
        logger.error(f"从远程接口获取停复牌信息失败: {str(e)}")
        return pd.DataFrame()


def save_suspend_info(data: pd.DataFrame) -> bool:
    """
    保存停复牌信息到数据集

    Args:
        data: 停复牌信息DataFrame

    Returns:
        bool: 保存是否成功
    """
    logger.info(f"开始保存停复牌信息: 共{len(data)}条记录")

    if data.empty:
        logger.warning("没有数据需要保存")
        return True

    # 确保有交易日期字段
    if StandardFields.TRADE_DATE not in data.columns:
        logger.error(f"数据中缺少交易日期字段: {StandardFields.TRADE_DATE}")
        return False

    # 添加年份字段
    data["year"] = pd.to_datetime(data[StandardFields.TRADE_DATE]).dt.year
    years = data["year"].unique()
    logger.info(f"数据包含以下年份: {years}")

    # 检查数据集是否存在，不存在则创建
    if not dw_exists(SUSPEND_INFO_DATASET):
        # 获取字段类型信息（不包含year列）
        fields_to_save = [col for col in data.columns if col != "year"]
        dtypes = get_fields_type(fields_to_save)

        # 创建数据集，使用单个structure_field
        dw_create_dataset(
            name=SUSPEND_INFO_DATASET,
            dtypes=dtypes,
            update_mode="update",  # 采用更新模式，以便智能更新
            structure_fields=["year"],  # 使用year作为结构字段，注意这里是列表
        )
        logger.info(f"创建停复牌信息数据集: {SUSPEND_INFO_DATASET}，结构字段为year")

    try:
        # 按年份分组保存数据
        success = True
        for year in years:
            # 提取当年数据
            year_data = data[data["year"] == year].copy()

            # 设置结构字段的值
            field_values = {"year": str(year)}

            # 移除year列后再保存
            if "year" in year_data.columns:
                year_data.drop("year", axis=1, inplace=True)

            # 保存数据到对应年份的数据文件
            result = dw_save(
                data=year_data,
                data_name=SUSPEND_INFO_DATASET,
                field_values=field_values,  # 提供field_values参数指定结构字段值
                mode="update",  # 使用更新模式
                update_key=StandardFields.TRADE_DATE,  # 使用交易日期作为更新键
            )

            if result:
                logger.info(f"保存{year}年停复牌信息成功")
            else:
                logger.error(f"保存{year}年停复牌信息失败")
                success = False

        return success
    except Exception as e:
        logger.error(f"保存停复牌信息失败: {str(e)}")
        return False


def check_update_needed(last_date: str) -> bool:
    """
    检查是否需要更新数据

    比较最后一条记录的日期与当前日期，判断是否需要更新数据。
    如果最后一条记录的日期等于或晚于当前日期，则不需要更新。

    Args:
        last_date: 最后一条记录的日期，格式为YYYY-MM-DD

    Returns:
        bool: 是否需要更新数据
    """
    try:
        # 解析最后一条记录的日期
        last_date_obj = datetime.strptime(last_date, "%Y-%m-%d")

        # 获取当前日期（仅保留年月日部分）
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 如果最后一条记录的日期等于或晚于当前日期，则不需要更新
        if last_date_obj >= current_date:
            logger.info(
                f"最后一条记录的日期({last_date})已是最新或超过当前日期({current_date.strftime('%Y-%m-%d')})，无需更新"
            )
            return False

        return True
    except Exception as e:
        logger.warning(f"检查更新状态时发生错误: {str(e)}")
        # 出错时默认需要更新
        return True


def update_suspend_info(days: int = 30) -> bool:
    """
    更新停复牌信息

    Args:
        days: 更新的天数，默认为30天，当无法获取最近记录时使用此参数向前推算

    Returns:
        bool: 更新是否成功

    Notes:
        考虑到TuShare API单次请求上限为5000条记录，此函数在更新大量历史数据时可能需要多次请求。
        当需要更新的时间跨度较大时（如超过30天），建议采用分批更新策略：
        1. 将大的时间区间拆分为多个较小的区间（如按周或按月）
        2. 对每个小区间单独调用fetch_suspend_info获取数据
        3. 将每个区间的数据合并后再统一保存
    """
    # 设置默认的结束日期
    end_date = datetime.now().strftime("%Y-%m-%d")

    # 尝试获取最近的数据记录来确定开始日期
    start_date = None
    last_date = None

    # 获取当前年份
    current_year = datetime.now().year

    # 检查最近三年的数据，从当前年份开始往前查
    for year in range(current_year, current_year - 3, -1):
        field_values = {"year": str(year)}

        # 检查该年份的数据是否存在
        if dw_exists(SUSPEND_INFO_DATASET, field_values=field_values):
            try:
                # 读取该年份最后一行数据
                last_row = dw_query_last_line(
                    SUSPEND_INFO_DATASET, field_values=field_values
                )
                if last_row is not None and not last_row.empty:
                    # 获取最后一条记录的日期
                    last_date = last_row[SORT_BY_FIELD].iloc[0]
                    logger.info(f"找到{year}年的最后一条记录，日期为: {last_date}")

                    # 检查是否需要更新
                    if not check_update_needed(last_date):
                        logger.info("数据已是最新，无需更新")
                        return True

                    # 将开始日期设为最后记录日期的后一天
                    start_date_obj = datetime.strptime(
                        last_date, "%Y-%m-%d"
                    ) + timedelta(days=1)
                    start_date = start_date_obj.strftime("%Y-%m-%d")
                    logger.info(f"根据最后一条记录设置开始日期: {start_date}")
                    break
            except Exception as e:
                logger.warning(f"获取{year}年最后一条记录失败: {str(e)}")

    # 如果未找到最近记录，使用默认开始日期
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        logger.info(f"未找到最近记录，使用默认开始日期: {start_date}")

    # 检查开始日期是否晚于结束日期
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    if start_date_obj > end_date_obj:
        logger.warning(
            f"开始日期({start_date})晚于结束日期({end_date})，无有效数据可更新"
        )
        return True  # 返回True因为这不是错误，而是没有需要更新的数据

    logger.info(f"开始更新停复牌信息: start_date={start_date}, end_date={end_date}")

    # 从远程接口获取数据
    data = fetch_suspend_info(start_date, end_date, None, None)

    if data.empty:
        logger.warning("未获取到停复牌信息，更新完成")
        return True  # 返回True因为这是正常情况，只是没有新数据

    # 保存到本地存储
    try:
        result = save_suspend_info(data)
        logger.info(f"更新停复牌信息完成: 共{len(data)}条记录")
        return result
    except Exception as e:
        logger.error(f"更新停复牌信息失败: {str(e)}")
        return False


def get_suspend_stocks(date: str, suspend_type: str = "S") -> list:
    """
    获取指定日期的停牌或复牌股票列表

    Args:
        date: 日期，格式为YYYY-MM-DD
        suspend_type: 停复牌类型，S-停牌，R-复牌，默认为S

    Returns:
        list: 股票代码列表
    """
    # 标准化日期
    std_date = to_standard_date(date)
    if not std_date:
        logger.error(f"日期格式无效: date={date}")
        return []

    logger.info(f"获取{std_date}的{suspend_type}股票列表")

    # 获取指定日期的年份，用于获取对应年份的数据
    date_obj = datetime.strptime(std_date, "%Y-%m-%d")
    year = date_obj.year
    field_values = {"year": str(year)}

    # 优先从本地数据集获取
    if dw_exists(SUSPEND_INFO_DATASET, field_values=field_values):
        try:
            # 查询指定年份的数据
            df = dw_query(SUSPEND_INFO_DATASET, field_values=field_values)

            if df is not None and not df.empty:
                # 过滤出符合条件的记录
                if StandardFields.TRADE_DATE in df.columns:
                    df = df[df[StandardFields.TRADE_DATE] == std_date]

                if suspend_type and StandardFields.SUSPEND_TYPE in df.columns:
                    df = df[df[StandardFields.SUSPEND_TYPE] == suspend_type]

                if not df.empty:
                    stock_codes = df[StandardFields.STOCK_CODE].unique().tolist()
                    logger.info(
                        f"从本地数据集获取到{std_date}的{suspend_type}股票列表: 共{len(stock_codes)}只股票"
                    )
                    return stock_codes
                else:
                    logger.warning(
                        f"本地数据集中未找到{std_date}的{suspend_type}股票记录"
                    )
            else:
                logger.warning(f"{year}年数据集为空或不存在")
        except Exception as e:
            logger.warning(f"从本地数据集获取数据失败: {str(e)}")
    else:
        logger.warning(f"{year}年数据集不存在，尝试更新数据")

    # 从本地未获取到数据，尝试从远程获取
    try:
        # 只获取指定日期当天的数据
        data = fetch_suspend_info(std_date, std_date, None, suspend_type)

        if not data.empty:
            # 保存到本地数据集
            save_suspend_info(data)

            # 提取股票代码
            stock_codes = data[StandardFields.STOCK_CODE].unique().tolist()
            logger.info(
                f"从远程获取到{std_date}的{suspend_type}股票列表: 共{len(stock_codes)}只股票"
            )
            return stock_codes
    except Exception as e:
        logger.error(f"从远程获取{std_date}的{suspend_type}股票列表失败: {str(e)}")

    logger.warning(f"未能获取到{std_date}的{suspend_type}股票列表")
    return []
