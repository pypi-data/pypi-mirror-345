#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全量计算股票交易状态面板数据

该脚本从头计算并创建所有历史交易状态面板数据，
按照证券类型和年月(security_type + year-month)结构字段进行存储
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所需模块
from datawhale.domain_pro.panel_trading_status import (
    create_trading_status_panel,
    TRADING_STATUS_PANEL_NAME,
    SECURITY_TYPE_STOCK,
    SECURITY_TYPE_INDEX,
    SECURITY_TYPE_CONVERTIBLE_BOND
)
from datawhale import dw_panel_exists, dw_panel_delete
from datawhale.logging import get_user_logger

# 获取日志记录器
logger = get_user_logger(__name__)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='创建股票交易状态面板数据')
    parser.add_argument('--start-date', type=str, help='开始日期，格式为YYYY-MM-DD')
    parser.add_argument('--end-date', type=str, help='结束日期，格式为YYYY-MM-DD')
    parser.add_argument('--force', action='store_true', help='强制重新创建，即使数据已存在')
    parser.add_argument('--clean', action='store_true', help='清空现有数据后重新创建')
    parser.add_argument('--structure', type=str, help='指定要处理的年月结构，格式为YYYY-MM，不指定则处理所有结构')
    parser.add_argument('--security-type', type=str, choices=[SECURITY_TYPE_STOCK, SECURITY_TYPE_INDEX, SECURITY_TYPE_CONVERTIBLE_BOND],
                        help='指定要处理的证券类型，不指定则处理所有类型')
    args = parser.parse_args()
    
    start_time = datetime.now()
    logger.info(f"开始创建股票交易状态面板数据: {start_time}")
    
    # 检查是否已存在面板数据
    panel_exists_flag = dw_panel_exists(TRADING_STATUS_PANEL_NAME)
    
    # 如果指定了--clean参数或者--force参数且面板已存在，则删除现有面板数据
    if panel_exists_flag and (args.clean or args.force):
        # 如果同时指定了特定的年月结构和证券类型
        if args.structure and args.security_type:
            logger.info(f"检测到交易状态面板数据 {TRADING_STATUS_PANEL_NAME} 已存在，将更新 {args.security_type} 类型的 {args.structure} 结构...")
            # 新版本中不需要删除结构，会自动覆盖或更新
        # 如果只指定了年月结构
        elif args.structure:
            logger.info(f"检测到交易状态面板数据 {TRADING_STATUS_PANEL_NAME} 已存在，将更新所有类型的 {args.structure} 结构...")
            # 新版本中不需要删除结构，会自动覆盖或更新
        # 如果只指定了证券类型
        elif args.security_type:
            logger.info(f"检测到交易状态面板数据 {TRADING_STATUS_PANEL_NAME} 已存在，将更新 {args.security_type} 类型的所有结构...")
            # 新版本中不需要删除结构，会自动覆盖或更新
        else:
            # 删除整个面板
            logger.info(f"检测到交易状态面板数据 {TRADING_STATUS_PANEL_NAME} 已存在，准备删除...")
            try:
                success = dw_panel_delete(panel_name=TRADING_STATUS_PANEL_NAME)
                if success:
                    logger.info(f"成功删除交易状态面板数据 {TRADING_STATUS_PANEL_NAME}")
                    panel_exists_flag = False  # 更新面板存在标志
                else:
                    logger.error(f"删除交易状态面板数据 {TRADING_STATUS_PANEL_NAME} 失败")
                    sys.exit(1)
            except Exception as e:
                logger.error(f"删除交易状态面板数据时发生错误: {str(e)}")
                sys.exit(1)
    elif panel_exists_flag and not args.force and not args.clean:
        # 如果指定了结构但没有force或clean标志，简单提示
        if args.structure or args.security_type:
            logger.warning(f"交易状态面板数据已存在。使用 --force 参数可在已有结构上更新数据。")
            return
        else:
            logger.warning(f"交易状态面板数据 {TRADING_STATUS_PANEL_NAME} 已存在。使用 --force 或 --clean 参数可重新创建。")
            return
    
    # 创建交易状态面板数据
    try:
        # 如果指定了特定结构，设置相应的日期范围
        if args.structure:
            logger.info(f"将创建年月结构为 {args.structure} 的交易状态面板数据")
            
            # 解析结构值为日期范围（假设格式为YYYY-MM）
            if args.start_date is None and args.end_date is None:
                year, month = args.structure.split('-')
                # 当月第一天
                month_start = f"{args.structure}-01"
                
                # 计算月末日期
                if month == '12':
                    next_year = int(year) + 1
                    next_month = '01'
                else:
                    next_year = int(year)
                    next_month = f"{int(month) + 1:02d}"
                
                # 下月第一天减一天得到本月最后一天
                next_month_first_day = datetime.strptime(f"{next_year}-{next_month}-01", "%Y-%m-%d")
                month_end = (next_month_first_day - timedelta(days=1)).strftime("%Y-%m-%d")
                
                # 更新日期范围参数
                args.start_date = month_start
                args.end_date = month_end
                
                logger.info(f"根据结构值 {args.structure} 设置日期范围: {args.start_date} 至 {args.end_date}")
        
        # 记录证券类型信息
        if args.security_type:
            logger.info(f"将只处理 {args.security_type} 类型的证券")
        else:
            logger.info("将处理所有类型的证券")
        
        # 创建交易状态面板数据
        success = create_trading_status_panel(args.start_date, args.end_date)
        
        if success:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"创建股票交易状态面板数据成功！耗时: {duration:.2f}秒")
        else:
            logger.error("创建股票交易状态面板数据失败！")
            sys.exit(1)
    except Exception as e:
        logger.error(f"创建股票交易状态面板数据时发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 