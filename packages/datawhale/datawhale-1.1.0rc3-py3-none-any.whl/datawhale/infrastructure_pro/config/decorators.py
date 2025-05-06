#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置装饰器模块
直接定义config函数，避免循环引用问题
"""

import functools
import inspect
from typing import Any, Callable, Optional, Union, TypeVar, cast
from datawhale.infrastructure_pro.config.config_manager import ConfigManager


def get_config():
    """获取配置管理器实例

    Returns:
        ConfigManager: 配置管理器实例
    """
    return ConfigManager()


F = TypeVar("F", bound=Callable[..., Any])


def config(
    key_path: Optional[str] = None, default: Any = None, arg_name: Optional[str] = None
) -> Union[Callable[[F], F], Any]:
    """配置装饰器，实现多种配置值获取和注入方式

    用法示例:

    1. 作为装饰器，将配置值作为第一个参数传入:
    @config("infrastructure.datasource.daily_kline")
    def process_data(config_value, other_args):
        # 使用 config_value 进行处理
        pass

    2. 作为装饰器，将配置值注入到指定参数:
    @config("infrastructure.process.max_workers", arg_name="workers")
    def run_tasks(tasks, workers=3):
        # 函数调用时 workers 参数会被配置值覆盖
        pass

    3. 直接调用获取配置值:
    max_workers = config("infrastructure.process.max_workers", default=5)

    Args:
        key_path: 配置路径，使用点号分隔，如 "infrastructure.logging.level"
        default: 默认值，当配置不存在时使用
        arg_name: 指定要替换的参数名称，如果为None则作为第一个参数传入

    Returns:
        Union[Callable, Any]: 装饰器函数或配置值
    """
    # 获取配置管理器实例 (单例)
    cfg = get_config()

    # 场景1: 无参数装饰器模式 @config
    if callable(key_path):
        func = key_path

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 将整个配置管理器作为第一个参数传入
            return func(cfg, *args, **kwargs)

        return cast(F, wrapper)

    # 场景2: 直接调用获取配置值 config('path')
    try:
        # 尝试获取调用者信息
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_info = inspect.getframeinfo(frame.f_back)
            # 判断是否为直接调用:
            # - 如果调用发生在函数内部(非模块级别)
            # - 不是在类定义中
            # - 不是在lambda中
            if caller_info.function not in ("<module>", "<lambda>") and (
                not caller_info.code_context
                or "class " not in caller_info.code_context[0]
            ):
                if key_path is not None:
                    return cfg.get(key_path, default)
    except Exception:
        # 如果获取调用栈信息失败，回退到装饰器模式
        pass
    finally:
        # 清理引用，避免潜在的循环引用
        if frame:
            del frame

    # 场景3: 装饰器模式 @config('path') 或 @config('path', arg_name='param')
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取配置值或整个配置对象
            config_value = cfg.get(key_path, default) if key_path else cfg

            # 根据参数注入方式决定如何传递配置值
            if arg_name:
                # 注入到指定名称的参数
                kwargs[arg_name] = config_value
                return func(*args, **kwargs)
            else:
                # 作为第一个参数注入
                return func(config_value, *args, **kwargs)

        return cast(F, wrapper)

    return decorator
