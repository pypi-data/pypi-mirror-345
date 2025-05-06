#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化配置模块

提供数据目录和运行时目录的配置功能
"""

import os
import yaml
import pathlib


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

    # 修改storage.yaml文件中的配置
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取原始配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 更新数据路径
    config["infrastructure"]["storage"]["dataset_dir"] = dataset_dir
    config["infrastructure"]["storage"]["panel_dir"] = panel_dir

    # 保存配置
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    return absolute_path


def set_runtime_dir(absolute_path):
    """
    设置运行信息存储路径

    Args:
        absolute_path: 运行信息存储的绝对路径
    """
    # 创建目录
    pathlib.Path(absolute_path).mkdir(parents=True, exist_ok=True)

    # 修改配置文件
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取原始配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 更新运行信息路径
    config["infrastructure"]["storage"]["runtime_dir"] = absolute_path

    # 保存配置
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    return absolute_path


def get_data_dir():
    """
    获取当前配置的数据存储路径

    Returns:
        str: 数据存储的绝对路径
    """
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config["infrastructure"]["storage"]["dataset_dir"]


def get_runtime_dir():
    """
    获取当前配置的运行信息存储路径

    Returns:
        str: 运行信息存储的绝对路径
    """
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config["infrastructure"]["storage"]["runtime_dir"]


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

    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取原始配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 更新用户日志级别（保存标准格式）
    config["infrastructure"]["logging"]["log_types"]["user"]["level"] = level_upper

    # 保存配置
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

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

    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取原始配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 更新系统日志级别（保存标准格式）
    config["infrastructure"]["logging"]["log_types"]["system"]["level"] = level_upper

    # 保存配置
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    return level_upper


def get_user_log_level():
    """
    获取当前用户日志级别

    Returns:
        str: 当前用户日志级别
    """
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config["infrastructure"]["logging"]["log_types"]["user"]["level"]


def get_system_log_level():
    """
    获取当前系统日志级别

    Returns:
        str: 当前系统日志级别
    """
    config_file = os.path.join(
        os.path.dirname(__file__), "config", "infrastructure_config.yaml"
    )

    # 读取配置
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config["infrastructure"]["logging"]["log_types"]["system"]["level"]
