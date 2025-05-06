#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载交易日历信息脚本

此脚本用于下载股票市场的交易日历信息，并保存到指定的数据存储中。
可以作为定时任务运行，以定期更新交易日历信息。
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import pandas as pd

# 导入交易日历信息模块
from datawhale.domain_pro.info_trade_calendar import (
    fetch_trade_calendar,
    save_trade_calendar_info,
    TRADE_CALENDAR_DATASET
)

# 导入日志模块
from datawhale.logging import get_user_logger

# 导入存储接口
from datawhale import dw_exists, dw_delete

# 获取日志记录器
logger = get_user_logger("download_trade_calendar_info")

def parse_args():
    """解析命令行参数"""
    # 计算默认的日期范围
    today = datetime.now()
    default_end_date = today + timedelta(days=365)  # 默认下载未来一年
    default_start_date = datetime(1990, 1, 1)  # 默认从1990年开始下载
    
    parser = argparse.ArgumentParser(description="下载交易日历信息")
    parser.add_argument(
        "--start-date", "-s",
        type=str,
        default=default_start_date.strftime("%Y-%m-%d"),
        help=f"开始日期，格式为YYYY-MM-DD，默认为1990年1月1日 ({default_start_date.strftime('%Y-%m-%d')})"
    )
    parser.add_argument(
        "--end-date", "-e",
        type=str,
        default=default_end_date.strftime("%Y-%m-%d"),
        help=f"结束日期，格式为YYYY-MM-DD，默认为未来一年 ({default_end_date.strftime('%Y-%m-%d')})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="可选的输出CSV文件路径，如果不指定则只保存到默认数据存储"
    )
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    logger.info(f"开始下载交易日历信息: 日期范围 {args.start_date} 至 {args.end_date}")
    start_time = datetime.now()
    
    try:
        # 检查数据集是否存在，如果存在则删除
        if dw_exists(TRADE_CALENDAR_DATASET):
            logger.info(f"检测到数据集 {TRADE_CALENDAR_DATASET} 已存在，正在删除...")
            if dw_delete(TRADE_CALENDAR_DATASET):
                logger.info(f"成功删除数据集 {TRADE_CALENDAR_DATASET}")
            else:
                logger.error(f"删除数据集 {TRADE_CALENDAR_DATASET} 失败")
                return False
                
        # 获取指定日期范围的交易日历信息
        df = fetch_trade_calendar(start_date=args.start_date, end_date=args.end_date)
        
        if df.empty:
            logger.warning("未获取到有效的交易日历信息")
            return False
        
        # 保存到数据存储
        success = save_trade_calendar_info(df)
        if not success:
            logger.error("保存交易日历信息到数据存储失败")
            return False
        
        # 如果指定了输出文件，则同时保存到CSV
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            df.to_csv(args.output, index=False, encoding="utf-8")
            logger.info(f"交易日历信息已保存到: {args.output}")
        
        # 输出交易日统计信息
        trading_days = df[df["is_trading_day"] == 1]
        non_trading_days = df[df["is_trading_day"] == 0]
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"下载交易日历信息完成，共{len(df)}天，其中交易日{len(trading_days)}天，非交易日{len(non_trading_days)}天")
        logger.info(f"耗时{duration:.2f}秒")
        return True
    
    except Exception as e:
        logger.error(f"下载交易日历信息失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 