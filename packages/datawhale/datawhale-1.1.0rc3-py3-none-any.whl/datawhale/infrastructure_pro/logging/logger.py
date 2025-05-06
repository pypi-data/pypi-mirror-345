#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
from typing import Optional, Dict, Any
from .config import LoggingConfig


# 定义彩色日志格式
class ColoredFormatter(logging.Formatter):
    """自定义彩色日志格式化器

    根据日志级别设置不同的颜色：
    - DEBUG: 蓝色
    - INFO: 绿色
    - WARNING: 黄色
    - ERROR: 红色
    - CRITICAL: 紫红色

    颜色主题可以通过配置文件自定义，默认使用内置的默认颜色主题。
    """

    # 默认ANSI颜色代码
    DEFAULT_COLORS = {
        "DEBUG": "\033[94m",  # 蓝色
        "INFO": "\033[92m",  # 绿色
        "WARNING": "\033[93m",  # 黄色
        "ERROR": "\033[91m",  # 红色
        "CRITICAL": "\033[95m",  # 紫红色
        "RESET": "\033[0m",  # 重置颜色
    }

    def __init__(
        self, fmt=None, datefmt=None, style="%", validate=True, *, color_theme=None
    ):
        """初始化彩色日志格式化器

        Args:
            fmt: 日志格式字符串
            datefmt: 日期格式字符串
            style: 格式化风格
            validate: 是否验证格式字符串
            color_theme: 颜色主题字典，覆盖默认颜色
        """
        super().__init__(fmt, datefmt, style, validate)
        self.colors = self.DEFAULT_COLORS.copy()
        # 更新颜色主题
        if color_theme and isinstance(color_theme, dict):
            for level, color in color_theme.items():
                self.colors[level] = color

    def format(self, record):
        """格式化日志记录，添加颜色代码"""
        levelname = record.levelname
        # 如果日志级别在预设颜色中，添加对应颜色
        if levelname in self.colors:
            record.levelname = (
                f"{self.colors[levelname]}{levelname}{self.colors['RESET']}"
            )
            if hasattr(record, "msg") and record.msg:
                # 仅对文本消息添加颜色，避免对结构化数据添加颜色
                if isinstance(record.msg, str):
                    record.msg = (
                        f"{self.colors[levelname]}{record.msg}{self.colors['RESET']}"
                    )
        return super().format(record)


# 定义一个日志级别设置为CRITICAL+1的特殊处理器
# 这样可以使这个处理器不处理任何日志消息
class DisabledHandler(logging.Handler):
    """禁用的日志处理器，级别设置为CRITICAL+1，不处理任何日志消息"""

    def __init__(self):
        super().__init__(logging.CRITICAL + 1)

    def emit(self, record):
        """不执行任何操作，丢弃所有日志消息"""
        pass


class NullLogger(logging.Logger):
    """空日志记录器，不记录任何日志消息

    当日志类型在某个层级被禁用时使用此日志记录器。
    该记录器会丢弃所有日志消息，但仍然提供与标准Logger相同的接口。
    """

    def __init__(self, name):
        """初始化空日志记录器

        Args:
            name: 日志记录器的名称
        """
        super().__init__(name, logging.CRITICAL + 1)
        # 添加一个禁用的处理器，确保不处理任何日志消息
        self.addHandler(DisabledHandler())
        # 确保不传播到父记录器
        self.propagate = False


def setup_logger(name, log_file, config=None):
    """设置并返回一个命名的日志记录器

    Args:
        name (str): 日志记录器的名称
        log_file (str): 日志文件的路径
        config (Dict[str, Any]): 日志配置字典，包含level、max_bytes、backup_count等配置项

    Returns:
        logging.Logger: 配置好的日志记录器

    Raises:
        OSError: 当无法创建日志目录或文件时抛出
    """
    # 获取已存在的日志记录器
    existing_logger = logging.getLogger(name)
    if existing_logger.handlers:
        # 清理现有的处理器
        for handler in existing_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()  # 确保文件句柄被正确关闭
            existing_logger.removeHandler(handler)

    try:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
                print(f"已创建日志目录: {log_dir}")
            except OSError as e:
                # 如果创建目录失败，使用默认目录
                # 使用LoggingConfig获取默认日志目录
                logging_config = LoggingConfig()
                default_log_dir = logging_config.get_log_dir()
                default_dir = os.path.join(default_log_dir, "other")
                if not os.path.exists(default_dir):
                    os.makedirs(default_dir, exist_ok=True)
                log_file = os.path.join(default_dir, os.path.basename(log_file))
                print(f"创建日志目录失败: {str(e)}，将使用默认目录: {default_dir}")
    except Exception as e:
        raise OSError(f"无法创建日志目录: {str(e)}")

    # 使用配置或默认值
    if config is None:
        config = {}

    # 确保有一个默认的INFO级别，即使移除了全局级别设置
    level = getattr(logging, config.get("level", "INFO"))
    max_bytes = config.get("max_bytes", 10 * 1024 * 1024)
    backup_count = config.get("backup_count", 5)
    log_format = config.get(
        "format",
        "%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(thread)d - %(message)s",
    )
    date_format = config.get("date_format", "%Y-%m-%d %H:%M:%S")
    use_color = config.get("use_color", True)  # 默认启用彩色日志
    color_theme = config.get("color_theme_dict", None)  # 获取颜色主题

    # 创建一个命名的日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # 确保日志不会传播到根记录器
    logger.propagate = False

    # 创建按大小滚动的文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 创建格式化器
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)

    # 为控制台输出设置彩色格式化器（如果启用）
    if use_color:
        console_formatter = ColoredFormatter(
            log_format, datefmt=date_format, color_theme=color_theme
        )
    else:
        console_formatter = file_formatter
    console_handler.setFormatter(console_formatter)

    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_user_logger(name, propagate=False, enabled=None):
    """获取用户日志记录器，用于记录程序执行进展情况

    用户日志记录器使用简洁的日志格式，主要用于展示程序执行的关键步骤和进展。
    所有用户日志将记录到同一个文件中。

    Args:
        name (str): 日志记录器的名称
        propagate (bool): 是否将日志传播到父记录器，默认为False
        enabled (bool, optional): 是否启用日志记录，默认为None（根据配置决定）

    Returns:
        logging.Logger: 配置好的用户日志记录器或禁用的日志记录器
    """
    # 获取日志配置
    config = LoggingConfig()

    # 检查日志是否启用，优先使用参数传入的值，然后检查配置
    if enabled is None:
        enabled = config.is_log_type_enabled(name, config.LOG_TYPE_USER)

    # 如果日志被禁用，返回一个空日志记录器
    if not enabled:
        return NullLogger("user_logger_disabled")

    # 使用固定名称，确保所有用户日志记录到同一个文件
    logger_name = "user_logger"
    logger = logging.getLogger(logger_name)
    # 设置传播属性
    logger.propagate = propagate

    if logger.handlers:
        return logger

    # 使用固定的文件名，确保所有用户日志记录到同一个文件
    log_file = os.path.join(config.get_log_dir(), config.DEFAULT_USER_LOG_FILE)
    log_config = config.get_config(name, "user")

    # 创建新的日志记录器
    return setup_logger(logger_name, log_file, log_config)


def get_system_logger(name, propagate=False, enabled=None):
    """获取系统日志记录器，用于记录详细的系统信息

    系统日志记录器使用详细的日志格式，记录系统运行的详细信息，包括进程ID、线程ID等。
    所有系统日志将记录到同一个文件中，但会根据架构层级（infrastructure、domain、application等）进行区分。

    Args:
        name (str): 日志记录器的名称，会用于确定所属架构层级
        propagate (bool): 是否将日志传播到父记录器，默认为False
        enabled (bool, optional): 是否启用日志记录，默认为None（根据配置决定）

    Returns:
        logging.Logger: 配置好的系统日志记录器或禁用的日志记录器
    """
    # 获取日志配置
    config = LoggingConfig()

    # 检查日志是否启用，优先使用参数传入的值，然后检查配置
    if enabled is None:
        enabled = config.is_log_type_enabled(name, config.LOG_TYPE_SYSTEM)

    # 如果日志被禁用，返回一个空日志记录器
    if not enabled:
        return NullLogger("system_logger_disabled")

    # 确定模块所属的架构层级
    layer = config.get_layer_from_name(name)

    # 使用固定名称和层级前缀，确保所有系统日志记录到同一个文件，同时保留层级信息
    logger_name = f"system_logger.{layer}"
    logger = logging.getLogger(logger_name)
    # 设置传播属性
    logger.propagate = propagate

    if logger.handlers:
        return logger

    # 使用固定的文件名，确保所有系统日志记录到同一个文件
    log_file = os.path.join(config.get_log_dir(), config.DEFAULT_SYSTEM_LOG_FILE)

    # 获取系统日志配置，但保留层级特定的格式
    log_config = config.get_config(name, "system")

    # 修改日志格式，添加层级标识
    if "format" in log_config:
        # 在格式字符串中添加层级信息，便于在system.log中区分不同层的日志
        original_format = log_config["format"]
        if "[%(name)s]" in original_format:
            # 如果格式中已经有name，替换为带层级信息的格式
            log_config["format"] = original_format.replace(
                "[%(name)s]", f"[{layer}][%(name)s]"
            )
        else:
            # 如果格式中没有name，添加层级信息
            parts = original_format.split(" - ", 1)
            if len(parts) > 1:
                log_config["format"] = f"{parts[0]} - [{layer}] - {parts[1]}"
            else:
                # 兜底处理
                log_config["format"] = f"%(asctime)s - [{layer}] - {original_format}"

    # 创建新的日志记录器
    return setup_logger(logger_name, log_file, log_config)
