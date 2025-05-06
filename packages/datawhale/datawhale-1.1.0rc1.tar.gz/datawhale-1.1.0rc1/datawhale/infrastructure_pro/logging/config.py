#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import Dict, Any, Optional, Union
from ..config.config_manager import ConfigManager


class LoggingConfig:
    """日志配置管理类

    集中管理所有日志相关的配置项，包括日志级别、文件路径、滚动策略等。
    支持按架构层级（infrastructure、domain、application）组织日志文件。
    实现了基于领域驱动设计的日志配置管理。
    同时区分用户日志和系统日志：
    - 用户日志(user)：主要了解程序执行进展情况
    - 系统日志(system)：记录详细信息，按架构层级区分

    所有配置参数都从YAML配置文件(infrastructure.logging)中读取，不在代码中定义默认值。
    日志目录从storage配置中获取，使用runtime_dir和logs_dir组合确定日志存储位置。
    """

    # 配置键名常量，避免字符串硬编码
    KEY_LAYERS = "layers"
    KEY_LOG_TYPES = "log_types"
    KEY_COLOR_THEMES = "color_themes"
    KEY_LEVEL = "level"
    KEY_FORMAT = "format"
    KEY_COLOR_THEME = "color_theme"
    KEY_COLOR_THEME_DICT = "color_theme_dict"
    KEY_ENABLED = "enabled"  # 新增：日志启用状态配置键

    # 日志类型常量
    LOG_TYPE_USER = "user"
    LOG_TYPE_SYSTEM = "system"

    # 默认日志文件名
    DEFAULT_USER_LOG_FILE = "user.log"
    DEFAULT_SYSTEM_LOG_FILE = "system.log"

    # 配置路径
    CONFIG_PATH = "infrastructure.logging"
    STORAGE_CONFIG_PATH = "infrastructure.storage"

    def __init__(self):
        """初始化日志配置管理器

        从YAML配置文件中加载配置，如果配置文件不存在或配置不完整，可能会导致错误。
        请确保infrastructure.logging配置节和storage配置节存在且配置完整。
        """
        self.config_manager = ConfigManager()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """从YAML配置文件加载配置

        从infrastructure.logging配置节加载完整的日志配置。

        Returns:
            Dict[str, Any]: 配置字典
        """
        config = self.config_manager.get(self.CONFIG_PATH, {})
        if not config:
            # 如果配置为空，记录警告
            print(f"警告：无法从{self.CONFIG_PATH}加载日志配置，请检查配置文件")
        return config

    def get_layer_from_name(self, name: str) -> str:
        """从日志记录器名称中获取所属架构层级

        Args:
            name: 日志记录器名称

        Returns:
            str: 架构层级名称，如"infrastructure"、"domain"、"application"或"other"
        """
        if not name:
            return "other"

        # 根据模块名确定所属层级
        name_parts = name.split(".")
        layers = self.config.get(self.KEY_LAYERS, {}).keys()

        for layer in layers:
            if layer in name_parts:
                return layer

        return "other"

    def get_log_dir(self) -> str:
        """获取日志根目录路径

        从storage配置中获取runtime_dir和logs_dir，组合得到完整的日志存储路径。

        Returns:
            str: 日志目录的完整路径

        Raises:
            ValueError: 如果配置中缺少必要的存储路径配置项
        """
        # 获取存储配置
        storage_config = self.config_manager.get(self.STORAGE_CONFIG_PATH, {})

        # 获取运行时目录
        runtime_dir = storage_config.get("runtime_dir")
        if not runtime_dir:
            raise ValueError(
                f"配置文件中缺少runtime_dir配置项，请检查infrastructure.storage配置"
            )

        # 获取日志目录（相对于运行时目录）
        logs_dir = storage_config.get("logs_dir")
        if not logs_dir:
            raise ValueError(
                f"配置文件中缺少logs_dir配置项，请检查infrastructure.storage配置"
            )

        # 组合得到完整的日志目录路径
        log_dir = os.path.join(runtime_dir, logs_dir)

        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        return log_dir

    def is_log_type_enabled(self, name: str, log_type: str) -> bool:
        """检查指定的日志类型在给定模块/层级中是否启用

        首先检查模块/层级特定的启用配置，然后回退到全局类型配置，最后默认为True

        Args:
            name: 日志记录器名称，用于识别所属层级
            log_type: 日志类型，可选值为"user"或"system"

        Returns:
            bool: 日志类型是否启用
        """
        # 确定日志所属层级
        layer = self.get_layer_from_name(name)

        # 检查层级特定的日志类型启用配置
        layers_config = self.config.get(self.KEY_LAYERS, {})
        if layer in layers_config:
            # 如果层级配置中有日志类型配置
            layer_config = layers_config[layer]
            log_types_in_layer = layer_config.get(self.KEY_LOG_TYPES, {})
            if log_type in log_types_in_layer:
                # 检查层级特定的日志类型启用配置
                enabled = log_types_in_layer[log_type].get(self.KEY_ENABLED)
                if enabled is not None:
                    return enabled

        # 检查全局日志类型配置中的启用状态
        log_types_config = self.config.get(self.KEY_LOG_TYPES, {})
        if log_type in log_types_config:
            enabled = log_types_config[log_type].get(self.KEY_ENABLED)
            if enabled is not None:
                return enabled

        # 默认情况下启用日志
        return True

    def get_config(self, name: str = None, log_type: str = None) -> Dict[str, Any]:
        """获取完整的日志配置

        Args:
            name: 日志记录器名称，用于获取特定层级的配置
            log_type: 日志类型，可选值为"user"或"system"

        Returns:
            Dict[str, Any]: 日志配置字典
        """
        # 获取全局配置的副本（排除层级、日志类型和颜色主题配置）
        result_config = {
            k: v
            for k, v in self.config.items()
            if k not in [self.KEY_LAYERS, self.KEY_LOG_TYPES, self.KEY_COLOR_THEMES]
        }

        # 确保配置中有默认的日志级别（即使全局配置中没有）
        if self.KEY_LEVEL not in result_config:
            result_config[self.KEY_LEVEL] = "INFO"  # 默认使用INFO级别

        # 默认情况下启用日志
        result_config[self.KEY_ENABLED] = True

        # 确定日志所属层级并获取层级配置
        layer = self.get_layer_from_name(name)
        layers_config = self.config.get(self.KEY_LAYERS, {})

        if layer in layers_config:
            # 更新配置，层级配置覆盖全局配置
            layer_config = layers_config[layer]
            result_config.update(layer_config)

        # 应用日志类型特定配置
        log_types_config = self.config.get(self.KEY_LOG_TYPES, {})
        if log_type and log_type in log_types_config:
            # 更新配置，日志类型配置覆盖层级配置和全局配置
            log_type_config = log_types_config[log_type]
            result_config.update(log_type_config)

        # 获取颜色主题
        theme_name = result_config.get(self.KEY_COLOR_THEME)
        if theme_name:
            color_themes = self.config.get(self.KEY_COLOR_THEMES, {})
            if theme_name in color_themes:
                result_config[self.KEY_COLOR_THEME_DICT] = color_themes[theme_name]

        return result_config
