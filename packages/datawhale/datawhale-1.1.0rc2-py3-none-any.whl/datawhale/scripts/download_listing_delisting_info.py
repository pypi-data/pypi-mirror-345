#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载上市退市信息脚本

此脚本用于下载股票市场的上市和退市信息，并保存到指定的数据存储中。
可以作为定时任务运行，以定期更新上市退市信息。
"""

import os
import sys
import argparse
from datetime import datetime
import pandas as pd

# 导入上市退市信息模块
from datawhale.domain_pro.info_listing_and_delisting import (
    fetch_all_listing_delisting_info,
    save_listing_delisting_info,
    LISTING_DELISTING_DATASET
)

# 导入日志模块
from datawhale.logging import get_user_logger

# 导入存储接口
from datawhale import dw_exists, dw_delete

# 获取日志记录器
logger = get_user_logger("download_listing_delisting_info")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="下载股票上市退市信息")
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="可选的输出CSV文件路径，如果不指定则只保存到默认数据存储"
    )
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    logger.info("开始下载股票上市退市信息")
    start_time = datetime.now()
    
    try:
        # 检查数据集是否存在，如果存在则删除
        if dw_exists(LISTING_DELISTING_DATASET):
            logger.info(f"检测到数据集 {LISTING_DELISTING_DATASET} 已存在，正在删除...")
            if dw_delete(LISTING_DELISTING_DATASET):
                logger.info(f"成功删除数据集 {LISTING_DELISTING_DATASET}")
            else:
                logger.error(f"删除数据集 {LISTING_DELISTING_DATASET} 失败")
                return False
        
        # 获取全市场上市退市信息
        df = fetch_all_listing_delisting_info()
        
        if df.empty:
            logger.warning("未获取到有效的上市退市信息")
            return False
        
        # 保存到数据存储 - 确保使用listing_delisting_info.py中的save_listing_delisting_info函数
        success = save_listing_delisting_info(df)
        if not success:
            logger.error("保存上市退市信息到数据存储失败")
            return False
        
        # 如果指定了输出文件，则同时保存到CSV
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            df.to_csv(args.output, index=False, encoding="utf-8")
            logger.info(f"上市退市信息已保存到: {args.output}")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"下载上市退市信息完成，共{len(df)}条记录，耗时{duration:.2f}秒")
        return True
    
    except Exception as e:
        logger.error(f"下载上市退市信息失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 