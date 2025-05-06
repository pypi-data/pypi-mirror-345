#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成次新股面板数据脚本

用于生成指定时间范围内的次新股面板数据

注意：
1. 本面板记录了每个交易日哪些股票属于次新股状态
2. 次新股判断是基于上市日期和截止日期(new_stock_cutoff_date)进行的
3. 如果股票在当前日期处于次新股状态，标记为1，否则不在面板中显示或标记为0
"""

import argparse
from datetime import datetime, timedelta
import sys
import os
import shutil

# 添加项目根目录到Python路径
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_dir)

from datawhale.domain_pro.panel_new_stock import create_new_stock_panel, NEW_STOCK_PANEL_NAME
from datawhale import dw_panel_exists, dw_panel_delete
from datawhale.logging import get_user_logger

# 获取用户日志记录器
logger = get_user_logger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="生成次新股面板数据")
    
    # 添加起始日期参数，默认为1990-01-01
    default_start_date = "1990-01-01"
    parser.add_argument("--start_date", type=str, default=default_start_date,
                        help=f"起始日期，格式：YYYY-MM-DD，默认为{default_start_date}")
    
    # 添加结束日期参数，默认为当前日期
    default_end_date = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument("--end_date", type=str, default=default_end_date,
                        help=f"结束日期，格式：YYYY-MM-DD，默认为{default_end_date}")
    
    # 添加是否强制重新生成的参数
    parser.add_argument("--force", action="store_true",
                        help="强制重新生成，将删除现有面板数据")
    
    return parser.parse_args()

def cleanup_existing_data():
    """清理现有面板数据"""
    try:
        # 检查面板数据是否存在
        if dw_panel_exists(NEW_STOCK_PANEL_NAME):
            logger.info(f"删除现有面板数据: {NEW_STOCK_PANEL_NAME}")
            dw_panel_delete(NEW_STOCK_PANEL_NAME)
            
        logger.info("成功清理现有次新股面板数据")
        return True
    except Exception as e:
        logger.error(f"清理现有面板数据时发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    start_date = args.start_date
    end_date = args.end_date
    force = args.force
    
    logger.info(f"开始生成次新股面板数据: 时间范围从{start_date}到{end_date}")
    
    try:
        # 如果指定了强制重新生成，先清理现有数据
        if force:
            logger.info("强制重新生成，清理现有面板数据")
            cleanup_result = cleanup_existing_data()
            if not cleanup_result:
                logger.error("清理现有面板数据失败，生成操作中止")
                print("清理现有面板数据失败，生成操作中止")
                return 1
        
        # 生成次新股面板数据
        success = create_new_stock_panel(start_date=start_date, end_date=end_date)
        
        if success:
            logger.info("生成次新股面板数据成功")
            print(f"生成次新股面板数据成功: 时间范围从{start_date}到{end_date}")
            return 0
        else:
            logger.error("生成次新股面板数据失败")
            print(f"生成次新股面板数据失败: 时间范围从{start_date}到{end_date}")
            return 1
    except Exception as e:
        logger.error(f"生成次新股面板数据时发生异常: {str(e)}")
        print(f"生成次新股面板数据时发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 