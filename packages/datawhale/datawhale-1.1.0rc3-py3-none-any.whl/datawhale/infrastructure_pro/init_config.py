#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化配置模块

提供数据目录和运行时目录的配置功能
"""

import os
import yaml
import pathlib
import re
from datawhale.infrastructure_pro.config.config_manager import IncludeLoader


def _update_yaml_value(file_path, key, value):
    """
    通过文本替换方式更新YAML文件中的值，保持原有内容顺序
    
    Args:
        file_path: YAML文件路径
        key: 要更新的键名
        value: 新的值
        
    Returns:
        bool: 更新是否成功
    """
    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 使用正则表达式查找并替换键值对
    pattern = fr"^({key}\s*:).*$"
    replacement = fr"\1 {value}"
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 如果内容未变，说明未找到键
    if new_content == content:
        return False
    
    # 写入更新后的内容
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    return True


def set_data_dir(absolute_path):
    """
    设置数据存储路径

    在指定的绝对路径下创建dataset和panel两个子目录，并更新配置

    Args:
        absolute_path: 数据存储的绝对路径

    Returns:
        str: 设置的数据存储绝对路径
    """
    # 创建数据根目录
    pathlib.Path(absolute_path).mkdir(parents=True, exist_ok=True)

    # 创建dataset和panel子目录
    dataset_dir = os.path.join(absolute_path, "dataset")
    panel_dir = os.path.join(absolute_path, "panel")
    pathlib.Path(dataset_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(panel_dir).mkdir(parents=True, exist_ok=True)

    # 获取storage.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    storage_config_file = os.path.join(config_dir, "infrastructure", "storage.yaml")

    # 更新dataset_dir和panel_dir值
    _update_yaml_value(storage_config_file, "dataset_dir", dataset_dir)
    _update_yaml_value(storage_config_file, "panel_dir", panel_dir)

    return absolute_path


def set_runtime_dir(absolute_path):
    """
    设置运行信息存储路径

    Args:
        absolute_path: 运行信息存储的绝对路径
    """
    # 创建目录
    pathlib.Path(absolute_path).mkdir(parents=True, exist_ok=True)

    # 获取storage.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    storage_config_file = os.path.join(config_dir, "infrastructure", "storage.yaml")

    # 更新runtime_dir值
    _update_yaml_value(storage_config_file, "runtime_dir", absolute_path)

    return absolute_path


def get_data_dir():
    """
    获取当前配置的数据存储路径

    Returns:
        str: 数据存储的绝对路径
    """
    # 获取storage.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    storage_config_file = os.path.join(config_dir, "infrastructure", "storage.yaml")

    # 读取配置
    with open(storage_config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, yaml.SafeLoader)

    return config["dataset_dir"]


def get_runtime_dir():
    """
    获取当前配置的运行信息存储路径

    Returns:
        str: 运行信息存储的绝对路径
    """
    # 获取storage.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    storage_config_file = os.path.join(config_dir, "infrastructure", "storage.yaml")

    # 读取配置
    with open(storage_config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, yaml.SafeLoader)

    return config["runtime_dir"]


def set_user_log_level(level):
    """
    设置用户日志级别

    Args:
        level: 日志级别，可选值为 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'，不区分大小写

    Returns:
        str: 设置后的日志级别

    Raises:
        ValueError: 当日志级别无效时抛出
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # 转换为大写并验证日志级别
    level_upper = level.upper() if isinstance(level, str) else level

    if level_upper not in valid_levels:
        raise ValueError(
            f"无效的日志级别: {level}，有效值为: {', '.join(valid_levels)}"
        )

    # 获取logging.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    logging_config_file = os.path.join(config_dir, "infrastructure", "logging.yaml")

    # 更新用户日志级别
    # 在log_types.user部分找到level并更新
    with open(logging_config_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 使用正则表达式查找并替换用户日志级别
    pattern = r"(log_types:\n(?:.*\n)*?  user:\n(?:.*\n)*?    level:) .*"
    replacement = r"\1 " + level_upper
    new_content = re.sub(pattern, replacement, content)
    
    with open(logging_config_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    return level_upper


def set_system_log_level(level):
    """
    设置系统日志级别

    Args:
        level: 日志级别，可选值为 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'，不区分大小写

    Returns:
        str: 设置后的日志级别

    Raises:
        ValueError: 当日志级别无效时抛出
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # 转换为大写并验证日志级别
    level_upper = level.upper() if isinstance(level, str) else level

    if level_upper not in valid_levels:
        raise ValueError(
            f"无效的日志级别: {level}，有效值为: {', '.join(valid_levels)}"
        )

    # 获取logging.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    logging_config_file = os.path.join(config_dir, "infrastructure", "logging.yaml")

    # 更新系统日志级别
    # 在log_types.system部分找到level并更新
    with open(logging_config_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 使用正则表达式查找并替换系统日志级别
    pattern = r"(log_types:\n(?:.*\n)*?  system:\n(?:.*\n)*?    level:) .*"
    replacement = r"\1 " + level_upper
    new_content = re.sub(pattern, replacement, content)
    
    with open(logging_config_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    return level_upper


def get_user_log_level():
    """
    获取当前用户日志级别

    Returns:
        str: 当前用户日志级别
    """
    # 获取logging.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    logging_config_file = os.path.join(config_dir, "infrastructure", "logging.yaml")

    # 读取配置
    with open(logging_config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, yaml.SafeLoader)

    return config["log_types"]["user"]["level"]


def get_system_log_level():
    """
    获取当前系统日志级别

    Returns:
        str: 当前系统日志级别
    """
    # 获取logging.yaml文件路径
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    logging_config_file = os.path.join(config_dir, "infrastructure", "logging.yaml")

    # 读取配置
    with open(logging_config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, yaml.SafeLoader)

    return config["log_types"]["system"]["level"]


def set_tushare_token(token):
    """
    设置TuShare的token

    Args:
        token: TuShare的API token

    Returns:
        str: 设置成功返回token，失败返回None
    """
    if not token or not isinstance(token, str):
        raise ValueError("TuShare token不能为空且必须为字符串")

    # TuShare token仍然保存在主配置文件中
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取原始配置（使用IncludeLoader来支持!include标签）
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, IncludeLoader)

    # 更新TuShare token
    config["infrastructure"]["datasource"]["meta"]["tushare"]["token"] = token

    # 保存配置
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    return token


def get_tushare_token():
    """
    获取TuShare的token

    Returns:
        str: TuShare的API token
    """
    # TuShare token保存在主配置文件中
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取配置（使用IncludeLoader来支持!include标签）
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, IncludeLoader)

    return config["infrastructure"]["datasource"]["meta"]["tushare"]["token"]
