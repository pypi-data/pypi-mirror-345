#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载全量ST股票信息脚本

用于下载指定时间范围内的全部ST股票信息
"""

import argparse
from datetime import datetime, timedelta
import sys
import os
import shutil

# 添加项目根目录到Python路径
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_dir)

from datawhale.domain_pro.info_st.st_info import download_st_info_by_period, ST_INFO_DATASET
from datawhale.logging import get_user_logger

# 获取用户日志记录器
logger = get_user_logger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="下载ST股票信息")
    
    # 修改起始日期参数，默认为1990-01-01
    default_start_date = "19900101"
    parser.add_argument("--start_date", type=str, default=default_start_date,
                        help=f"起始日期，格式：YYYYMMDD，默认为{default_start_date}")
    
    # 添加结束日期参数，默认为当前日期
    default_end_date = datetime.now().strftime("%Y%m%d")
    parser.add_argument("--end_date", type=str, default=default_end_date,
                        help=f"结束日期，格式：YYYYMMDD，默认为{default_end_date}")
    
    # 添加是否强制重新下载的参数
    parser.add_argument("--force", action="store_true",
                        help="强制重新下载，将删除现有数据")
    
    return parser.parse_args()

def cleanup_existing_data():
    """清理现有数据文件和元数据"""
    try:
        # 数据文件路径
        data_dir = os.path.join(project_dir, "cache", "dataset", ST_INFO_DATASET)
        # 元数据文件路径
        meta_file = os.path.join(project_dir, "cache", "runtime", "metainfo", f"{ST_INFO_DATASET}.yaml")
        
        # 删除数据目录
        if os.path.exists(data_dir):
            logger.info(f"删除现有数据目录: {data_dir}")
            shutil.rmtree(data_dir)
            
        # 删除元数据文件
        if os.path.exists(meta_file):
            logger.info(f"删除现有元数据文件: {meta_file}")
            os.remove(meta_file)
            
        logger.info("成功清理现有ST股票信息数据")
        return True
    except Exception as e:
        logger.error(f"清理现有数据时发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    start_date = args.start_date
    end_date = args.end_date
    force = args.force
    
    logger.info(f"开始下载ST股票信息: 时间范围从{start_date}到{end_date}")
    
    try:
        # 如果指定了强制重新下载，先清理现有数据
        if force:
            logger.info("强制重新下载，清理现有数据")
            cleanup_result = cleanup_existing_data()
            if not cleanup_result:
                logger.error("清理现有数据失败，下载操作中止")
                print("清理现有数据失败，下载操作中止")
                return 1
        
        # 下载ST股票信息
        success = download_st_info_by_period(start_date=start_date, end_date=end_date)
        
        if success:
            logger.info("下载ST股票信息成功")
            print(f"下载ST股票信息成功: 时间范围从{start_date}到{end_date}")
            return 0
        else:
            logger.error("下载ST股票信息失败")
            print(f"下载ST股票信息失败: 时间范围从{start_date}到{end_date}")
            return 1
    except Exception as e:
        logger.error(f"下载ST股票信息时发生异常: {str(e)}")
        print(f"下载ST股票信息时发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 