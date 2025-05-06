#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TuShare配置模块

提供TuShare的token配置和初始化功能
"""

import os
import json
import tushare as ts
from datawhale.infrastructure_pro.logging import get_user_logger

# 获取用户日志记录器
logger = get_user_logger(__name__)

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "tushare_config.json")


def get_tushare_token():
    """
    从配置文件中获取TuShare的token

    Returns:
        str: TuShare的token
    """
    try:
        # 检查配置文件是否存在
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"TuShare配置文件不存在: {CONFIG_FILE}")
            return None

        # 读取配置文件
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 获取token
        token = config.get("token")
        if not token:
            logger.error("TuShare配置文件中未找到token")
            return None

        return token
    except Exception as e:
        logger.error(f"读取TuShare token失败: {str(e)}")
        return None


def set_tushare_token(token: str) -> bool:
    """
    设置并保存TuShare的token到配置文件

    Args:
        token: 新的TuShare token

    Returns:
        bool: 设置是否成功
    """
    if not token or not isinstance(token, str):
        logger.error("无效的token值")
        return False

    try:
        # 准备配置数据
        config = {"token": token}

        # 确保目录存在
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

        # 保存到配置文件
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        logger.info("TuShare token已保存到配置文件")

        # 重新初始化token
        return init_tushare_token()
    except Exception as e:
        logger.error(f"保存TuShare token失败: {str(e)}")
        return False


def init_tushare_token():
    """
    初始化TuShare的token

    Returns:
        bool: 初始化是否成功
    """
    try:
        # 获取token
        token = get_tushare_token()
        if not token:
            return False

        # 设置TuShare的token
        ts.set_token(token)
        logger.info("TuShare token初始化成功")
        return True
    except Exception as e:
        logger.error(f"TuShare token初始化失败: {str(e)}")
        return False


def get_pro_api():
    """
    获取TuShare的pro API接口

    Returns:
        pro_api: TuShare的pro API接口对象
    """
    try:
        # 确保token已初始化
        if not init_tushare_token():
            return None

        # 获取pro API接口
        pro = ts.pro_api()
        return pro
    except Exception as e:
        logger.error(f"获取TuShare pro API失败: {str(e)}")
        return None
