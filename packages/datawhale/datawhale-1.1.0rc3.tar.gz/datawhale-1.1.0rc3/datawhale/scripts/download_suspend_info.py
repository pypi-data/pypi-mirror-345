#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载停复牌信息脚本

此脚本用于下载指定日期范围内的股票停复牌信息，并保存到指定的数据存储中。
可以作为定时任务运行，以定期获取停复牌信息。
脚本会自动检测已下载的最后日期，并从该日期后一天开始增量下载直到当前日期。
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta
import pandas as pd

# 导入停复牌信息模块
from datawhale.domain_pro.info_suspend import (
    fetch_suspend_info,
    save_suspend_info,
    update_suspend_info,
    SUSPEND_INFO_DATASET
)

# 导入日志模块
from datawhale.logging import get_user_logger

# 导入存储接口
from datawhale import dw_exists, dw_delete, dw_query_last_line

# 获取日志记录器
logger = get_user_logger("download_suspend_info")

def parse_args():
    """解析命令行参数"""
    # 计算默认的日期范围
    today = datetime.now()
    default_start_date = datetime(1990, 1, 1).strftime("%Y-%m-%d")  # 默认初始下载从1990年开始
    current_year = today.year
    
    parser = argparse.ArgumentParser(description="下载股票停复牌信息")
    parser.add_argument(
        "--initial-start-date", "-i",
        type=str,
        default=default_start_date,
        help=f"初始下载的开始日期（仅在数据集不存在时使用），格式为YYYY-MM-DD，默认为1990年1月1日 ({default_start_date})"
    )
    parser.add_argument(
        "--ts-code", "-t",
        type=str,
        help="股票代码，不指定则下载所有股票停复牌信息"
    )
    parser.add_argument(
        "--suspend-type", "-p",
        type=str,
        choices=['S', 'R'],
        default=None,
        help="停复牌类型，S-停牌，R-复牌，不指定则下载所有类型"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="可选的输出CSV文件路径，如果不指定则只保存到默认数据存储"
    )
    parser.add_argument(
        "--force-delete", "-f",
        action="store_true",
        default=False,
        help="强制删除现有数据集并重新下载，默认为False"
    )
    parser.add_argument(
        "--sleep", "-s",
        type=int,
        default=3,
        help="每批次下载之间的休眠时间(秒)，默认为3秒"
    )
    parser.add_argument(
        "--delete-start-year", 
        type=int,
        default=None,
        help="强制删除的起始年份（包含该年份），默认为None"
    )
    parser.add_argument(
        "--delete-end-year", 
        type=int,
        default=None,
        help="强制删除的结束年份（包含该年份），默认为None"
    )
    return parser.parse_args()

def delete_years_range(start_year, end_year):
    """删除指定年份范围的数据"""
    if start_year is None or end_year is None:
        logger.warning("未指定删除年份范围，将不执行部分删除操作")
        return False
    
    if start_year > end_year:
        logger.error(f"删除年份范围无效：起始年份{start_year}大于结束年份{end_year}")
        return False
    
    success = True
    for year in range(start_year, end_year + 1):
        field_values = {'year': str(year)}
        if dw_exists(SUSPEND_INFO_DATASET, field_values=field_values):
            logger.info(f"删除{year}年的停复牌数据...")
            if dw_delete(SUSPEND_INFO_DATASET, field_values=field_values):
                logger.info(f"成功删除{year}年的停复牌数据")
            else:
                logger.error(f"删除{year}年的停复牌数据失败")
                success = False
        else:
            logger.info(f"{year}年的停复牌数据不存在，无需删除")
    
    return success

def main():
    """主函数"""
    args = parse_args()
    
    today = datetime.now().strftime("%Y-%m-%d")  # 当前日期作为结束日期
    start_time = datetime.now()
    
    try:
        # 确定起始日期
        start_date = args.initial_start_date
        
        # 检查数据集是否存在
        dataset_exists = dw_exists(SUSPEND_INFO_DATASET)
        
        # 如果指定了删除年份范围
        if args.delete_start_year is not None and args.delete_end_year is not None:
            logger.info(f"将删除{args.delete_start_year}年至{args.delete_end_year}年的停复牌数据...")
            delete_success = delete_years_range(args.delete_start_year, args.delete_end_year)
            if not delete_success:
                logger.warning("部分年份数据删除失败，请检查日志")
            
            # 重新检查数据集是否存在（可能全部被删除）
            dataset_exists = dw_exists(SUSPEND_INFO_DATASET)
        # 如果指定强制删除整个数据集
        elif dataset_exists and args.force_delete:
            logger.info(f"检测到数据集 {SUSPEND_INFO_DATASET} 已存在，将删除整个数据集...")
            if dw_delete(SUSPEND_INFO_DATASET):
                logger.info(f"成功删除数据集 {SUSPEND_INFO_DATASET}")
                dataset_exists = False
            else:
                logger.error(f"删除数据集 {SUSPEND_INFO_DATASET} 失败")
                return False

        # 如果数据集存在且不是强制删除模式，则读取最后一条记录确定开始日期
        if dataset_exists and not args.force_delete:
            try:
                # 获取当前年份，用于构建field_values参数
                current_year = datetime.now().year
                field_values = {'year': str(current_year)}
                
                # 读取最后一行数据，提供field_values参数
                last_row = dw_query_last_line(SUSPEND_INFO_DATASET, field_values=field_values)
                if last_row is not None and not last_row.empty:
                    # 使用最后一行的交易日期作为开始日期
                    last_date = last_row["trade_date"].iloc[0]
                    # 获取后一天作为开始日期（避免重复获取最后一天的数据）
                    start_date_obj = datetime.strptime(last_date, "%Y-%m-%d") + timedelta(days=1)
                    start_date = start_date_obj.strftime("%Y-%m-%d")
                    logger.info(f"根据已有数据集的最后记录设置开始日期: {start_date}")
                else:
                    # 如果当前年份没有数据，尝试查找前几年的记录
                    found_last_record = False
                    for prev_year in range(current_year-1, current_year-5, -1):
                        prev_field_values = {'year': str(prev_year)}
                        if dw_exists(SUSPEND_INFO_DATASET, field_values=prev_field_values):
                            prev_last_row = dw_query_last_line(SUSPEND_INFO_DATASET, field_values=prev_field_values)
                            if prev_last_row is not None and not prev_last_row.empty:
                                last_date = prev_last_row["trade_date"].iloc[0]
                                # 将开始日期设为下一年的1月1日
                                next_year = prev_year + 1
                                start_date = f"{next_year}-01-01"
                                logger.info(f"根据{prev_year}年最后一条记录设置开始日期: {start_date}")
                                found_last_record = True
                                break
                    
                    if not found_last_record:
                        logger.warning(f"未能找到任何年份的历史记录，使用初始开始日期: {args.initial_start_date}")
                        start_date = args.initial_start_date
            except Exception as e:
                logger.warning(f"获取最后一条记录失败，使用初始开始日期 {args.initial_start_date}: {str(e)}")
                start_date = args.initial_start_date
        
        logger.info(f"开始下载停复牌信息: 日期范围 {start_date} 至 {today}")
        if args.ts_code:
            logger.info(f"指定股票代码: {args.ts_code}")
        if args.suspend_type:
            logger.info(f"指定停复牌类型: {args.suspend_type}")
        
        # 将起始日期和结束日期转换为datetime对象
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(today, "%Y-%m-%d")
        
        # 如果起始日期晚于或等于结束日期，说明数据已经是最新的
        if start_date_obj >= end_date_obj:
            logger.info(f"当前数据已经是最新的，无需下载。最后记录日期: {start_date}")
            return True
        
        # 使用分批下载的方式获取停复牌信息
        # 固定每批次下载最大90天数据，避免请求过大
        FIXED_BATCH_DAYS = 365*3  
        
        total_records = 0
        suspend_count = 0
        resume_count = 0
        batch_count = 0
        current_start_date = start_date_obj
        
        # 循环下载数据，直到达到结束日期
        while current_start_date <= end_date_obj:
            # 计算当前批次的结束日期
            # 使用固定的批次天数下载
            current_end_date = min(current_start_date + timedelta(days=FIXED_BATCH_DAYS), end_date_obj)
            
            batch_count += 1
            logger.info(f"开始下载第{batch_count}批数据: {current_start_date.strftime('%Y-%m-%d')} - {current_end_date.strftime('%Y-%m-%d')}")
            
            # 下载当前批次数据
            df = fetch_suspend_info(
                start_date=current_start_date.strftime("%Y-%m-%d"),
                end_date=current_end_date.strftime("%Y-%m-%d"),
                ts_code=args.ts_code,
                suspend_type=args.suspend_type
            )
            
            # 如果没有获取到数据，可能是API限制或者该时间段没有数据
            if df.empty:
                logger.warning(f"未获取到第{batch_count}批数据，继续下一批")
                # 更新开始日期为当前结束日期的后一天
                current_start_date = current_end_date + timedelta(days=1)
                # 休眠一段时间，避免频繁请求API
                logger.info(f"休眠{args.sleep}秒后继续下一批下载")
                time.sleep(args.sleep)
                continue
            
            # 保存这一批数据
            success = save_suspend_info(df)
            if not success:
                logger.error(f"保存第{batch_count}批停复牌信息失败")
                # 继续尝试下一批
                current_start_date = current_end_date + timedelta(days=1)
                continue
            
            # 统计数据
            total_records += len(df)
            if "suspend_type" in df.columns:
                suspend_count += len(df[df["suspend_type"] == "S"])
                resume_count += len(df[df["suspend_type"] == "R"])
            
            logger.info(f"第{batch_count}批数据下载完成，共{len(df)}条记录，当前累计下载{total_records}条记录")
            
            # 读取最后保存的数据行，用于确定下一批的开始日期
            try:
                # 从最后保存的数据中提取年份
                if df.empty:
                    logger.warning("当前批次没有获取到数据，使用当前批次的结束日期加一天作为下一批次的开始日期")
                    current_start_date = current_end_date + timedelta(days=1)
                    continue
                
                # 获取最后一条记录的交易日期，并提取其年份
                last_record = df.sort_values(by="trade_date").iloc[-1]
                last_date_str = last_record["trade_date"]
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
                last_date_year = last_date.year
                
                field_values = {'year': str(last_date_year)}
                
                # 检查年份数据是否存在
                year_dataset_exists = dw_exists(SUSPEND_INFO_DATASET, field_values=field_values)
                
                # 使用field_values参数读取最后一行
                if year_dataset_exists:
                    last_row = dw_query_last_line(SUSPEND_INFO_DATASET, field_values=field_values)
                    if last_row is not None and not last_row.empty:
                        last_date_str = last_row["trade_date"].iloc[0]
                        logger.info(f"当前数据集最后日期: {last_date_str}")
                        
                        # 更新开始日期为最后日期的后一天
                        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
                        current_start_date = last_date + timedelta(days=1)
                    else:
                        # 如果读取失败，使用当前批次的结束日期加一天作为下一批次的开始日期
                        current_start_date = current_end_date + timedelta(days=1)
                else:
                    logger.info(f"未找到{last_date_year}年的数据文件，使用当前批次的结束日期加一天作为下一批次的开始日期")
                    current_start_date = current_end_date + timedelta(days=1)
            except Exception as e:
                logger.warning(f"读取最后一行数据失败: {str(e)}")
                # 如果读取失败，使用当前批次的结束日期加一天作为下一批次的开始日期
                current_start_date = current_end_date + timedelta(days=1)
            
            # 如果当前开始日期已经超过结束日期，结束循环
            if current_start_date > end_date_obj:
                logger.info(f"已达到目标结束日期 {today}，停止下载")
                break
            
            # 休眠一段时间，避免频繁请求API
            logger.info(f"休眠{args.sleep}秒后继续下一批下载")
            time.sleep(args.sleep)
        
        # 如果指定了输出文件，则同时将全部数据保存到CSV
        if args.output:
            try:
                output_dir = os.path.dirname(args.output)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                # 从数据集中读取全部数据
                from datawhale.infrastructure_pro.storage import dw_query
                
                # 初始化一个空的DataFrame用于存储所有年份的数据
                all_data = pd.DataFrame()
                
                # 获取所有存在的年份
                if not df.empty:
                    # 从刚获取的数据中提取所有年份
                    years = sorted(pd.to_datetime(df['trade_date']).dt.year.unique())
                    logger.info(f"数据包含以下年份: {years}")
                else:
                    # 如果当前没有获取到数据，尝试获取当前年份及之前几年的数据
                    current_year = datetime.now().year
                    years = list(range(current_year-10, current_year+1))
                    logger.info(f"尝试查询最近几年的数据: {years}")
                
                # 查询每个年份的数据
                for year in years:
                    field_values = {'year': str(year)}
                    if dw_exists(SUSPEND_INFO_DATASET, field_values=field_values):
                        year_data = dw_query(SUSPEND_INFO_DATASET, field_values=field_values)
                        if not year_data.empty:
                            logger.info(f"获取到{year}年的数据：{len(year_data)}条记录")
                            all_data = pd.concat([all_data, year_data], ignore_index=True)
                
                if not all_data.empty:
                    # 按日期排序
                    if "trade_date" in all_data.columns:
                        all_data = all_data.sort_values(by="trade_date")
                    
                    all_data.to_csv(args.output, index=False, encoding="utf-8")
                    logger.info(f"全部停复牌信息已保存到: {args.output}，共{len(all_data)}条记录")
                else:
                    logger.warning("未能从数据集中获取任何数据")
            except Exception as e:
                logger.error(f"保存停复牌信息到CSV文件失败: {str(e)}")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"下载停复牌信息完成，共下载{batch_count}批次，{total_records}条记录，其中停牌{suspend_count}条，复牌{resume_count}条")
        logger.info(f"耗时{duration:.2f}秒")
        return True
    
    except Exception as e:
        logger.error(f"下载停复牌信息失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 