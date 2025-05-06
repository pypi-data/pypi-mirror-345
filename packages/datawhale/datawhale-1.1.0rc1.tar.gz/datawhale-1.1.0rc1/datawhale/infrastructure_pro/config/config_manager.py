#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import json
from typing import Dict, Any, Optional, List, Union


class IncludeLoader(yaml.SafeLoader):
    """支持!include标签的YAML加载器

    允许在YAML文件中使用!include标签来包含其他YAML文件的内容。
    包含的文件路径应相对于当前文件目录。

    示例:
        infrastructure:
          logging: !include infrastructure/logging.yaml
    """

    # 使用类变量跟踪包含文件的堆栈，所有实例共享
    _included_files_stack = set()

    # 设置最大递归深度，非常保守
    _max_include_depth = 3

    # 跟踪当前递归深度
    _current_depth = 0

    def __init__(self, stream):
        # 确定根目录
        self._root = (
            os.path.dirname(stream.name) if hasattr(stream, "name") else os.getcwd()
        )
        super(IncludeLoader, self).__init__(stream)

    @classmethod
    def include(cls, loader, node):
        """处理!include标签，限制递归深度并防止循环引用

        Args:
            loader: YAML加载器实例
            node: 当前处理的节点

        Returns:
            包含的YAML文件内容，或在循环引用或错误时返回空字典
        """
        # 增加递归深度计数
        cls._current_depth += 1

        try:
            # 严格检查递归深度
            if cls._current_depth > cls._max_include_depth:
                print(f"警告: include深度超过限制({cls._max_include_depth})，终止递归")
                return {}

            # 解析文件名
            filename = os.path.join(loader._root, loader.construct_scalar(node))
            abs_filename = os.path.abspath(filename)

            # 循环引用检测
            if abs_filename in cls._included_files_stack:
                print(f"警告: 检测到循环引用 {abs_filename}，跳过加载")
                return {}

            # 将文件添加到已加载集合
            cls._included_files_stack.add(abs_filename)

            # 尝试加载文件
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    # 使用SafeLoader而不是IncludeLoader作为备选方案，防止深度嵌套
                    # 当深度接近限制时，禁止进一步include
                    if cls._current_depth >= cls._max_include_depth - 1:
                        # 最后一层使用SafeLoader避免任何潜在的递归
                        result = yaml.load(f, yaml.SafeLoader)
                    else:
                        # 正常情况下使用IncludeLoader
                        result = yaml.load(f, IncludeLoader)

                    # 确保返回字典
                    return result if isinstance(result, dict) else {}
            except Exception as e:
                print(f"加载包含文件 {filename} 时出错: {str(e)}")
                return {}
        except Exception as e:
            # 捕获所有异常，确保不会因为任何原因卡死
            print(f"include操作出现未预期错误: {str(e)}")
            return {}
        finally:
            # 清理工作：移除文件并减少深度计数
            if "abs_filename" in locals() and abs_filename in cls._included_files_stack:
                cls._included_files_stack.remove(abs_filename)
            cls._current_depth -= 1


# 添加自定义标签处理器
IncludeLoader.add_constructor("!include", IncludeLoader.include)


class ConfigManager:
    """配置管理器

    作为基础设施层的组件，负责管理和提供系统配置信息。
    使用单例模式确保全局配置的一致性。
    支持多配置文件加载和灵活的配置访问。
    支持使用!include指令导入嵌套配置文件。
    """

    # 单例模式相关属性
    _instance = None
    _config = None

    # 配置文件信息
    _config_files = {
        "infrastructure": "infrastructure_config.yaml",
        "domain": "domain_config.yaml",
        "application": "application_config.yaml",
    }

    # 测试模式配置
    _test_mode = False
    _test_config_dir = None

    # 各层级中需要提升到根级别的键
    _root_level_keys = {
        "infrastructure": ["storage", "datasource", "process", "retry", "logging"],
        "domain": [],
        "application": [],
    }

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化配置管理器"""
        if self._config is None:
            self._load_config()

    @classmethod
    def enable_test_mode(cls, test_config_dir):
        """启用测试模式，使用测试配置目录

        调用时机：
        - 必须在ConfigManager实例化之前调用此方法
        - 通常在测试用例的setup阶段调用，用于设置测试环境
        - 调用后创建的ConfigManager实例将使用测试配置目录

        Args:
            test_config_dir: 测试配置文件目录的路径
        """
        cls._test_mode = True
        cls._test_config_dir = test_config_dir
        cls._config = None  # 重置配置以强制重新加载
        cls._instance = None

    @classmethod
    def disable_test_mode(cls):
        """禁用测试模式，恢复使用正常配置目录"""
        cls._test_mode = False
        cls._test_config_dir = None
        cls._config = None  # 重置配置以强制重新加载

    def _get_config_dir(self) -> str:
        """获取配置目录路径

        根据是否处于测试模式返回不同的配置目录

        Returns:
            str: 配置目录路径
        """
        if self._test_mode and self._test_config_dir:
            config_dir = self._test_config_dir
            # 设置测试根目录变量，用于替换配置中的${TEST_ROOT}
            self._test_root = os.path.dirname(os.path.dirname(self._test_config_dir))
        else:
            config_dir = os.path.dirname(__file__)
        return config_dir

    def _load_yaml_file(self, file_path: str) -> Dict:
        """加载YAML文件

        Args:
            file_path: YAML文件路径

        Returns:
            Dict: 加载的配置数据
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = yaml.load(f, IncludeLoader)

                # 处理配置中的环境变量替换
                if config_data and self._test_mode and hasattr(self, "_test_root"):
                    config_data = self._process_env_variables(config_data)

                return config_data or {}
        except Exception as e:
            print(f"加载配置文件 {file_path} 出错: {str(e)}")
            return {}

    def _process_config_data(self, config_type: str, config_data: Dict) -> None:
        """处理特定类型的配置数据

        根据配置类型进行不同的处理，并添加到配置字典中

        Args:
            config_type: 配置类型
            config_data: 配置数据
        """
        # 确保配置类型的字典存在
        if config_type not in self._config:
            self._config[config_type] = {}

        # 获取该类型的配置节点
        config_section = config_data.get(config_type, {})

        # 更新配置类型对应的配置
        self._config[config_type].update(config_section)

        # 处理特殊配置类型
        if config_type == "infrastructure":
            # 将关键配置添加到根级别，便于直接访问
            for key in self._root_level_keys.get(config_type, []):
                if key in config_section:
                    self._config[key] = config_section[key]

        elif config_type == "domain":
            # 将domain配置添加到根级别
            if "domain" not in self._config:
                self._config["domain"] = {}
            self._config["domain"].update(config_section)

        elif config_type == "application":
            # 将application配置添加到根级别
            self._config["application"] = config_section

            # 处理storage结构配置
            if "storage" in config_section and "structure" in config_section["storage"]:
                if "storage" not in self._config:
                    self._config["storage"] = {}
                self._config["storage"]["structure"] = config_section["storage"][
                    "structure"
                ]
        else:
            # 其他配置类型直接添加
            self._config[config_type] = config_section

    def _load_config(self):
        """加载所有配置文件并合并配置"""
        self._config = {}
        config_dir = self._get_config_dir()

        # 检查是否为测试模式下的空配置目录
        if self._test_mode and (
            not os.path.exists(config_dir) or not os.listdir(config_dir)
        ):
            # 在测试模式下不设置默认值，保持空配置
            return

        # 非测试模式或非空测试目录时，设置默认编码为UTF-8
        self._config["infrastructure"] = {"storage": {"encoding": "utf-8"}}

        # 按顺序加载配置文件，确保正确的配置覆盖顺序
        for config_type, config_file in self._config_files.items():
            config_path = os.path.join(config_dir, config_file)
            if os.path.exists(config_path):
                config_data = self._load_yaml_file(config_path)
                if config_data:
                    self._process_config_data(config_type, config_data)

    def _process_env_variables(self, config_data: Dict) -> Dict:
        """处理配置中的环境变量

        替换配置中的环境变量占位符，如${TEST_ROOT}

        Args:
            config_data: 原始配置数据

        Returns:
            Dict: 处理后的配置数据
        """
        # 将配置转换为字符串以便进行全局替换
        config_str = json.dumps(config_data)

        # 替换${TEST_ROOT}变量
        if hasattr(self, "_test_root"):
            config_str = config_str.replace(
                "${TEST_ROOT}", self._test_root.replace("\\", "\\\\")
            )

        # 转换回字典
        return json.loads(config_str)

    def get(self, key_path: str, default=None) -> Any:
        """获取配置值

        Args:
            key_path: 配置键路径，使用点号分隔，如'infrastructure.logging.level'
            default: 默认值

        Returns:
            配置值
        """
        if not key_path:
            return default

        keys = key_path.split(".")
        value = self._config

        # 遍历嵌套键
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default

        return value

    def get_config_by_type(
        self,
        type_path: str,
        component: str = None,
        config_key: str = None,
        default: Any = None,
    ) -> Any:
        """通用配置获取方法

        Args:
            type_path: 配置类型路径，如'infrastructure'
            component: 组件名称，如'logging'
            config_key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        # 构建完整的配置路径
        if component:
            base_path = f"{type_path}.{component}"
        else:
            base_path = type_path

        # 获取配置
        config = self.get(base_path, default if config_key is None else {})

        # 如果指定了配置键且配置不为空，则获取对应键的值
        if config_key and isinstance(config, dict):
            return config.get(config_key, default)

        return config

    def get_infrastructure_config(self, component: str, config_key: str = None) -> Any:
        """获取基础设施组件配置

        Args:
            component: 组件名称，如'logging', 'storage', 'process'等
            config_key: 可选的配置键

        Returns:
            配置值
        """
        return self.get_config_by_type("infrastructure", component, config_key, {})

    def get_domain_config(self, component: str, config_key: str = None) -> Any:
        """获取领域层配置

        Args:
            component: 领域组件名称，如'daily_kline', 'validation'等
            config_key: 可选的配置键，用于获取特定配置项

        Returns:
            配置值
        """
        return self.get_config_by_type("domain", component, config_key)

    def get_datasource_config(self, source_type: str, config_key: str = None) -> Any:
        """获取指定数据源的配置

        Args:
            source_type: 数据源类型，如'daily_kline', 'stock_list'等
            config_key: 可选的配置键，用于获取特定配置项

        Returns:
            配置值
        """
        # 首先尝试从infrastructure.datasource获取配置
        config = self.get_infrastructure_config(f"datasource.{source_type}")

        # 如果在infrastructure中没有找到，尝试从application中获取
        if not config:
            config = self.get_config_by_type("application", source_type)

        # 如果指定了配置键且配置不为空，则获取对应键的值
        if config_key and config:
            return config.get(config_key)

        return config

    def get_datasource_meta(self, source_type: str) -> Optional[Dict]:
        """获取数据源的元数据配置

        Args:
            source_type: 数据源类型，如'tushare', 'baostock'等

        Returns:
            Optional[Dict]: 数据源元数据配置
        """
        return self.get(f"infrastructure.datasource.meta.{source_type}")

    def get_download_config(self, component: str = None) -> Dict:
        """获取下载配置

        Args:
            component: 可选的组件名称，用于获取特定组件的下载配置

        Returns:
            Dict: 下载配置
        """
        if component:
            return self.get(f"application.{component}.download", {})
        return self.get("application.download", {})

    # 使用属性装饰器简化常用配置的访问
    @property
    def datasource_meta_config(self) -> Dict:
        """获取所有数据源的元数据配置"""
        return self.get("infrastructure.datasource_meta", {})

    @property
    def logging_config(self) -> Dict:
        """获取日志配置"""
        return self.get_infrastructure_config("logging")

    @property
    def storage_config(self) -> Dict:
        """获取存储配置"""
        return self.get_infrastructure_config("storage")

    @property
    def process_config(self) -> Dict:
        """获取进程管理配置"""
        return self.get_infrastructure_config("process")

    @property
    def retry_config(self) -> Dict:
        """获取重试配置"""
        return self.get_infrastructure_config("retry")

    def set(self, key_path: str, value: Any) -> None:
        """设置配置值

        Args:
            key_path: 配置键路径，使用点号分隔，如'infrastructure.logging.level'
            value: 要设置的值
        """
        if not key_path:
            return

        keys = key_path.split(".")
        current = self._config

        # 遍历到倒数第二个键，创建必要的嵌套字典
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # 设置最后一个键的值
        current[keys[-1]] = value

    def reload(self):
        """重新加载配置信息

        用于在运行时重新加载配置文件，或者应用环境变量更改
        """
        self._load_config()

    def update(self, config_data: Dict) -> None:
        """更新配置

        Args:
            config_data: 新的配置数据
        """
        # 检查参数类型并处理空值
        if not config_data:
            return

        # 确保 config_data 是字典
        if not isinstance(config_data, dict):
            return

        # 处理各类型的配置数据
        for config_type, config_section in config_data.items():
            if config_type in self._config_files:
                self._process_config_data(config_type, {config_type: config_section})
            else:
                # 对于未知类型，直接添加
                self._config[config_type] = config_section


# 实例化配置管理器
# 确保在其他模块中使用ConfigManager时，已经加载了配置
config = ConfigManager()
