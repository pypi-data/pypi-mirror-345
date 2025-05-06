#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Optional, Union, List, Any
import os
import pandas as pd
from datetime import datetime
import traceback
import yaml

# 从顶层模块导入
from datawhale.logging import get_system_logger, get_user_logger
from datawhale.exceptions import StorageError
from datawhale.config import config, get_config

# 模块内的导入使用相对导入
from .panel import Panel
from .metainfo.panel_metainfo import PanelMetaInfo
from .layers.layers import Layers

# 系统日志记录器，用于详细技术日志
logger = get_system_logger(__name__)
# 用户日志记录器，用于记录主要操作和状态变化
user_logger = get_user_logger(__name__)


class PanelStorageService:
    """面板数据存储服务实现

    提供基于元数据配置的面板数据存储服务，支持灵活的文件结构和数据管理。

    主要功能：
    1. 基于元数据配置的存储结构管理
    2. 多层文件结构支持
    3. 可扩展的更新策略
    4. 集成的元数据管理
    5. 基础的数据操作（保存、加载、删除）

    属性：
        panel_dir (str): 面板存储服务的基础目录路径
        metainfo_dir (str): 元数据目录路径
        encoding (str): 文件编码方式
        default_format (str): 默认文件格式
    """

    def __init__(self, storage_config=None):
        """初始化面板存储服务

        使用storage.yaml配置文件中的配置初始化面板存储服务。

        Args:
            storage_config: 存储配置，如果为None则从配置系统获取
        """
        # 如果没有提供配置，则从config装饰器获取
        if storage_config is None:
            config_manager = get_config()
            storage_config = config_manager.get("storage", {})

        # 规范化路径分隔符，确保跨平台兼容性
        self.panel_dir = os.path.normpath(
            os.path.abspath(storage_config.get("panel_dir"))
        )

        # 规范化路径分隔符，确保跨平台兼容性
        runtime_dir = os.path.normpath(
            os.path.abspath(storage_config.get("runtime_dir"))
        )
        self.metainfo_dir = os.path.normpath(
            os.path.join(runtime_dir, storage_config.get("metainfo_dir"))
        )

        # 设置编码和默认格式
        self.encoding = storage_config.get("encoding", "utf-8")
        self.default_format = storage_config.get("format", "csv")

        # 确保必要目录存在
        self._init_storage()

        logger.info(
            f"面板存储服务初始化完成：panel_dir={self.panel_dir}, "
            f"metainfo_dir={self.metainfo_dir}, encoding={self.encoding}, "
            f"default_format={self.default_format}"
        )
        user_logger.info("面板存储服务初始化完成")

    def _init_storage(self) -> None:
        """初始化存储环境

        创建基础存储目录和元数据目录。

        Raises:
            StorageError: 初始化失败时抛出
        """
        try:
            os.makedirs(self.panel_dir, exist_ok=True)
            os.makedirs(self.metainfo_dir, exist_ok=True)
            logger.info("面板存储环境初始化成功")
        except Exception as e:
            error_msg = f"初始化面板存储环境失败：{str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise StorageError(error_msg)

    def _log_operation_context(
        self, operation: str, data_name: str, error: Exception = None
    ) -> Dict:
        """记录操作上下文信息

        生成详细的操作上下文信息，用于日志记录和错误追踪。

        Args:
            operation: 操作类型
            data_name: 数据名称
            error: 异常信息对象（如果有）

        Returns:
            Dict: 操作上下文信息
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data_name": data_name,
            "panel_dir": self.panel_dir,
            "metainfo_dir": self.metainfo_dir,
            "layer": "infrastructure_pro",
            "service": self.__class__.__name__,
            "operation_id": f"{operation}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "module": "storage",
            "component": "panel_storage_service",
            "process_id": os.getpid(),
            "thread_id": hash(datetime.now()),
        }

        if error:
            context["error"] = str(error)
            context["error_type"] = error.__class__.__name__
            context["traceback"] = traceback.format_exc()
            context["error_details"] = {
                "args": getattr(error, "args", None),
                "cause": str(getattr(error, "__cause__", None)),
                "code": getattr(error, "code", None),
                "strerror": getattr(error, "strerror", None),
            }

        return context

    def _get_panel(self, panel_name: str) -> Panel:
        """获取面板数据对象

        Args:
            panel_name: 面板数据名称

        Returns:
            Panel: 面板数据对象

        Raises:
            FileNotFoundError: 面板数据不存在时抛出
        """
        logger.debug(f"获取面板数据对象: {panel_name}")
        return Panel.load_panel(panel_name, self.panel_dir, self.metainfo_dir)

    def save(
        self,
        data: pd.DataFrame,
        panel_name: str,
        field_values: Dict[str, str] = None,
        mode: str = None,
        update_key: str = None,
        **kwargs,
    ) -> bool:
        """保存面板数据

        根据元数据配置保存数据到对应的文件结构中。

        Args:
            data: 要保存的数据
            panel_name: 面板数据名称
            field_values: 字段值映射，用于直接指定动态层的值
            mode: 更新模式，如果为None则使用元数据中的默认值
                可选值："overwrite"（覆盖）、"append"（追加）或"update"（智能更新）
            update_key: 当mode为'update'时，用于比较的列名，只有该列值大于文件最后一行对应值的数据才会被追加
            **kwargs: 额外参数，传递给底层保存函数

        Returns:
            bool: 保存是否成功

        Raises:
            StorageError: 保存失败时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始保存面板数据: {panel_name}")
            logger.info(
                f"PanelStorageService开始保存数据: {panel_name}, rows={len(data)}, field_values={field_values}, mode={mode}, update_key={update_key}"
            )

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"保存面板数据失败: {error_msg}")
                raise StorageError(error_msg)

            # 执行保存操作
            try:
                batch_size = kwargs.pop("batch_size", None)
                panel.save(data, field_values, mode, update_key, batch_size)

                # 记录成功日志
                user_logger.info(f"成功保存面板数据: {panel_name}, 共{len(data)}行")
                return True
            except Exception as e:
                error_msg = f"保存面板数据失败: {str(e)}"
                user_logger.error(f"保存面板数据失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("save", panel_name, e)
            error_msg = f"保存面板数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"保存面板数据时发生错误: {panel_name} - {str(e)}")
            raise StorageError(error_msg)

    def query(
        self, panel_name: str, field_values: Dict[str, str] = None, **kwargs
    ) -> Optional[pd.DataFrame]:
        """查询面板数据

        根据元数据配置和字段值查询面板数据，返回宽格式（面板格式）的结果。

        Args:
            panel_name: 面板数据名称
            field_values: 字段值映射，用于定位具体文件
            **kwargs: 额外参数，会直接传递给Panel.query方法
                sort_by: 排序字段
                parallel: 是否使用并行处理，默认为True
                columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            pd.DataFrame: 查询结果，宽格式的面板数据
            如果没有匹配数据或数据为空，返回None

        Raises:
            StorageError: 查询失败时抛出
        """
        try:
            logger.info(
                f"PanelStorageService开始查询面板数据: panel={panel_name}, field_values={field_values}, kwargs={kwargs}"
            )

            # 加载面板数据
            panel = self._get_panel(panel_name)

            # 执行查询
            try:
                result = panel.query(field_values=field_values, **kwargs)

                # 返回结果，如果结果为空，统一返回None
                if result is not None and result.empty:
                    return None

                return result
            except Exception as e:
                error_msg = f"查询面板数据失败: {str(e)}"
                logger.error(error_msg)
                raise StorageError(error_msg)

        except Exception as e:
            if isinstance(e, StorageError):
                raise

            context = self._log_operation_context("query", panel_name, e)
            error_msg = f"查询面板数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            raise StorageError(error_msg)

    def delete(self, panel_name: str, field_values: Dict[str, str] = None) -> bool:
        """删除面板数据

        根据元数据配置和字段值删除面板数据文件。

        Args:
            panel_name: 面板数据名称
            field_values: 字段值映射，用于定位具体文件。如果为None则删除整个面板数据。

        Returns:
            bool: 删除是否成功

        Raises:
            StorageError: 删除失败时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始删除面板数据: {panel_name}")
            logger.info(
                f"PanelStorageService开始删除数据: {panel_name}, field_values={field_values}"
            )

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                # 面板数据不存在，抛出StorageError异常
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 执行删除操作
            try:
                result = panel.delete(field_values)

                # 记录成功日志
                if field_values is None:
                    user_logger.info(f"成功删除面板数据集: {panel_name}")
                else:
                    user_logger.info(f"成功删除面板数据: {panel_name}")

                return result
            except Exception as e:
                error_msg = f"删除面板数据失败: {str(e)}"
                user_logger.error(f"删除面板数据失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("delete", panel_name, e)
            error_msg = f"删除面板数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"删除面板数据时发生错误: {panel_name} - {str(e)}")
            raise StorageError(error_msg)

    def exists(self, panel_name: str, field_values: Dict[str, str] = None) -> bool:
        """检查面板数据是否存在

        根据元数据配置和字段值检查面板数据文件是否存在。

        Args:
            panel_name: 面板数据名称
            field_values: 字段值映射，用于定位具体文件

        Returns:
            bool: 面板数据是否存在

        Raises:
            StorageError: 检查失败时抛出
        """
        try:
            logger.info(
                f"检查面板数据是否存在: {panel_name}, field_values={field_values}"
            )

            # 检查面板数据集是否存在
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                logger.debug(f"面板数据不存在: {panel_name}")
                return False

            # 使用Panel类的exists方法检查数据是否存在
            return panel.exists(field_values)

        except Exception as e:
            context = self._log_operation_context("exists", panel_name, e)
            error_msg = f"检查面板数据存在性失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            raise StorageError(error_msg)

    def create_panel(
        self,
        name: str,
        index_col: str,
        value_dtype: str,
        entity_col_name: str = "entity_id",
        format: str = None,
        structure_fields: List[str] = None,
        update_mode: str = None,
    ) -> Panel:
        """创建新的面板数据

        创建面板数据前会检查参数有效性，并验证面板数据文件夹和元数据文件是否已存在。
        如果已存在则会抛出错误，避免意外覆盖现有数据。

        Args:
            name: 面板数据名称
            index_col: 索引列名称（日期列）
            value_dtype: 值数据类型（如"float64"）
            entity_col_name: 实体列名称，默认为'entity_id'
            format: 文件格式，默认使用配置中的default_format
            structure_fields: 文件结构字段列表，用于确定文件层级结构
            update_mode: 更新模式，可选值："append"（追加）、"overwrite"（覆盖）或"update"（智能更新），默认为"append"

        Returns:
            Panel: 创建的面板数据对象

        Raises:
            StorageError: 参数无效或文件/文件夹已存在时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始创建面板数据: {name}")
            # 计算层级数 (层级数=结构字段数+1)
            panel_level = len(structure_fields) + 1 if structure_fields else 1
            logger.info(
                f"PanelStorageService开始创建面板数据: name={name}, level={panel_level}, format={format}, update_mode={update_mode}"
            )

            # 使用默认值
            if format is None:
                format = self.default_format
            if update_mode is None:
                update_mode = "append"

            # 验证update_mode参数
            if update_mode not in ["append", "overwrite", "update"]:
                error_msg = f"无效的更新模式：{update_mode}，必须是'append'、'overwrite'或'update'"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 检查面板数据文件夹是否已存在
            panel_folder = os.path.join(self.panel_dir, name)
            if os.path.exists(panel_folder):
                error_msg = f"面板数据文件夹已存在: {name}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 检查元数据文件是否已存在
            meta_file = os.path.join(self.metainfo_dir, f"{name}.yaml")
            if os.path.exists(meta_file):
                error_msg = f"面板数据元数据文件已存在: {name}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 创建面板数据
            try:
                panel = Panel.create_panel(
                    name=name,
                    folder=self.panel_dir,
                    meta_folder=self.metainfo_dir,
                    index_col=index_col,
                    value_dtype=value_dtype,
                    entity_col_name=entity_col_name,
                    format=format,
                    structure_fields=structure_fields,
                    update_mode=update_mode,
                )

                # 创建带有结构字段的目录结构（如果有结构字段）
                if structure_fields and len(structure_fields) > 0:
                    # 创建主目录
                    os.makedirs(panel_folder, exist_ok=True)
                    # 结构字段目录会在保存数据时通过field_values动态创建

                # 记录成功日志
                user_logger.info(f"成功创建面板数据: {name}, 层级结构: {panel_level}")

                return panel
            except Exception as e:
                error_msg = f"创建面板数据失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"创建面板数据失败: {name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            # 如果是已知的StorageError，直接抛出
            if isinstance(e, StorageError):
                raise

            # 其他异常，记录详细信息并包装为StorageError
            context = self._log_operation_context("create_panel", name, e)
            error_msg = f"创建面板数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"创建面板数据时发生错误: {name} - {str(e)}")
            raise StorageError(error_msg)

    def get_all_entities(
        self, panel_name: str, field_values: Dict[str, str] = None
    ) -> List[str]:
        """获取所有实体代码

        Args:
            panel_name: 面板数据名称
            field_values: 查询条件字段值映射

        Returns:
            List[str]: 所有实体代码列表

        Raises:
            StorageError: 获取失败时抛出

        Note:
            此方法使用Panel.query方法获取数据，因此也支持query方法的所有参数，
            包括columns参数，但columns不会影响返回的实体列表。
        """
        try:
            logger.info(
                f"开始获取面板数据所有实体: {panel_name}, field_values={field_values}"
            )

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"获取所有实体失败: {error_msg}")
                raise StorageError(error_msg)

            # 获取所有实体
            try:
                entities = panel.get_all_entities(field_values)

                logger.info(
                    f"成功获取面板数据所有实体: {panel_name}, 实体数量: {len(entities)}"
                )
                return entities
            except Exception as e:
                error_msg = f"获取所有实体失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"获取所有实体失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("get_all_entities", panel_name, e)
            error_msg = f"获取所有实体失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"获取所有实体时发生错误: {panel_name} - {str(e)}")
            raise StorageError(error_msg)

    def get_entity_data(
        self, panel_name: str, entity_id: str, field_values: Dict[str, str] = None
    ) -> pd.Series:
        """获取特定实体的数据

        Args:
            panel_name: 面板数据名称
            entity_id: 实体标识符
            field_values: 查询条件字段值映射

        Returns:
            pd.Series: 特定实体的数据序列，索引为日期

        Raises:
            StorageError: 获取失败时抛出

        Note:
            此方法使用Panel.query方法获取数据，因此也支持query方法的所有参数，
            但不会直接传递columns参数，因为只需要返回单个实体的数据。
        """
        try:
            logger.info(
                f"开始获取面板数据实体数据: {panel_name}, entity_id={entity_id}, field_values={field_values}"
            )

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"获取实体数据失败: {error_msg}")
                raise StorageError(error_msg)

            # 获取实体数据
            try:
                entity_data = panel.get_entity_data(entity_id, field_values)

                logger.info(
                    f"成功获取面板数据实体数据: {panel_name}, entity_id={entity_id}, 数据点数量: {len(entity_data)}"
                )
                return entity_data
            except Exception as e:
                error_msg = f"获取实体数据失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(
                    f"获取实体数据失败: {panel_name}, entity_id={entity_id} - {str(e)}"
                )
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context(
                "get_entity_data", f"{panel_name}_{entity_id}", e
            )
            error_msg = f"获取实体数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(
                f"获取实体数据时发生错误: {panel_name}, entity_id={entity_id} - {str(e)}"
            )
            raise StorageError(error_msg)

    def get_date_data(
        self, panel_name: str, date: str, field_values: Dict[str, str] = None
    ) -> pd.Series:
        """获取特定日期的数据

        Args:
            panel_name: 面板数据名称
            date: 日期字符串
            field_values: 查询条件字段值映射

        Returns:
            pd.Series: 特定日期的数据序列，索引为实体名称

        Raises:
            StorageError: 获取失败时抛出

        Note:
            此方法使用Panel.query方法获取数据，因此也支持query方法的所有参数，
            但不会直接传递columns参数，因为需要返回特定日期的所有实体数据。
        """
        try:
            logger.info(
                f"开始获取面板数据日期数据: {panel_name}, date={date}, field_values={field_values}"
            )

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"获取日期数据失败: {error_msg}")
                raise StorageError(error_msg)

            # 获取日期数据
            try:
                date_data = panel.get_date_data(date, field_values)

                logger.info(
                    f"成功获取面板数据日期数据: {panel_name}, date={date}, 数据点数量: {len(date_data)}"
                )
                return date_data
            except Exception as e:
                error_msg = f"获取日期数据失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(
                    f"获取日期数据失败: {panel_name}, date={date} - {str(e)}"
                )
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context(
                "get_date_data", f"{panel_name}_{date}", e
            )
            error_msg = f"获取日期数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(
                f"获取日期数据时发生错误: {panel_name}, date={date} - {str(e)}"
            )
            raise StorageError(error_msg)

    def get_panel_stats(
        self, panel_name: str, field_values: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """获取面板数据统计信息

        Args:
            panel_name: 面板数据名称
            field_values: 查询条件字段值映射

        Returns:
            Dict[str, Any]: 统计信息字典

        Raises:
            StorageError: 获取失败时抛出

        Note:
            此方法使用Panel.query方法获取数据，因此也支持query方法的所有参数，
            包括columns参数，但通常不需要传递columns参数，因为需要所有列来计算统计信息。
        """
        try:
            logger.info(
                f"开始获取面板数据统计信息: {panel_name}, field_values={field_values}"
            )

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"获取面板数据统计信息失败: {error_msg}")
                raise StorageError(error_msg)

            # 获取统计信息
            try:
                stats = panel.get_panel_stats(field_values)

                logger.info(f"成功获取面板数据统计信息: {panel_name}")
                return stats
            except Exception as e:
                error_msg = f"获取面板数据统计信息失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"获取面板数据统计信息失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("get_panel_stats", panel_name, e)
            error_msg = f"获取面板数据统计信息失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(
                f"获取面板数据统计信息时发生错误: {panel_name} - {str(e)}"
            )
            raise StorageError(error_msg)

    def get_panel(self, panel_name: str) -> Panel:
        """获取面板数据对象（公开接口）

        Args:
            panel_name: 面板数据名称

        Returns:
            Panel: 面板数据对象

        Raises:
            StorageError: 面板数据不存在时抛出
        """
        try:
            return self._get_panel(panel_name)
        except FileNotFoundError as e:
            error_msg = f"面板数据不存在: {panel_name}"
            logger.error(error_msg)
            raise StorageError(error_msg)

    def read_last_line(
        self,
        panel_name: str,
        field_values: Dict[str, str] = None,
        dtypes: Dict[str, str] = None,
        columns: List[str] = None,
    ) -> Optional[pd.DataFrame]:
        """读取面板数据文件的最后一行

        根据字段值确定面板数据文件，并读取该文件的最后一行。这对于智能更新模式下检查最新记录特别有用。

        Args:
            panel_name: 面板数据名称
            field_values: 字段值映射，用于定位具体文件。如果是单层结构面板，可以为None
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用元数据中的dtypes
            columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            Optional[pd.DataFrame]: 包含最后一行数据的DataFrame，如果文件不存在或为空则返回None
            返回的是宽格式数据，其中一行包含了某个日期下所有实体的数据

        Raises:
            StorageError: 读取失败时抛出
        """
        try:
            # 记录日志
            logger.info(
                f"开始读取面板数据文件最后一行: {panel_name}, field_values={field_values}, columns={columns}"
            )
            user_logger.info(f"开始读取面板数据文件最后一行: {panel_name}")

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"读取面板数据最后一行失败: {error_msg}")
                raise StorageError(error_msg)

            # 读取最后一行
            try:
                # 将columns参数传递给Panel.read_last_line方法，以支持列选择功能
                last_line = panel.read_last_line(field_values, dtypes)

                # 如果提供了columns参数并且结果不为空，则过滤列
                if (
                    columns is not None
                    and last_line is not None
                    and not last_line.empty
                ):
                    # 确保索引列始终包含在内
                    if (
                        panel.index_col not in columns
                        and panel.index_col in last_line.columns
                    ):
                        columns = columns + [panel.index_col]

                    # 过滤列
                    columns_to_keep = [
                        col for col in columns if col in last_line.columns
                    ]
                    last_line = last_line[columns_to_keep]

                # 记录成功日志
                if last_line is None or last_line.empty:
                    user_logger.warning(f"面板数据文件为空或只有表头: {panel_name}")
                else:
                    user_logger.info(f"成功读取面板数据最后一行: {panel_name}")

                return last_line
            except FileNotFoundError as e:
                error_msg = f"面板数据文件不存在: {str(e)}"
                logger.error(error_msg)
                user_logger.error(
                    f"读取面板数据最后一行失败: {panel_name} - {error_msg}"
                )
                raise StorageError(error_msg)
            except Exception as e:
                error_msg = f"读取面板数据最后一行失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"读取面板数据最后一行失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("read_last_line", panel_name, e)
            error_msg = f"读取面板数据最后一行失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(
                f"读取面板数据最后一行时发生错误: {panel_name} - {str(e)}"
            )
            raise StorageError(error_msg)

    def read_last_n_lines(
        self,
        panel_name: str,
        n: int,
        field_values: Dict[str, str] = None,
        dtypes: Dict[str, str] = None,
        columns: List[str] = None,
    ) -> Optional[pd.DataFrame]:
        """读取面板数据文件的最后n行

        根据字段值确定面板数据文件，并读取该文件的最后n行。这对于数据分析和智能更新模式特别有用。

        Args:
            panel_name: 面板数据名称
            n: 需要读取的行数，必须是正整数
            field_values: 字段值映射，用于定位具体文件。如果是单层结构面板，可以为None
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用元数据中的dtypes
            columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            Optional[pd.DataFrame]: 包含最后n行数据的DataFrame
            如果文件为空返回None，如果文件只有表头则返回一个只有表头的空DataFrame
            返回的是宽格式数据，其中每行代表一个日期下所有实体的数据

        Raises:
            StorageError: 读取失败时抛出
        """
        try:
            # 验证n是否为正整数
            if not isinstance(n, int) or n <= 0:
                error_msg = f"n必须是正整数，当前值为: {n}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 记录日志
            logger.info(
                f"开始读取面板数据文件最后{n}行: {panel_name}, field_values={field_values}, columns={columns}"
            )
            user_logger.info(f"开始读取面板数据文件最后{n}行: {panel_name}")

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"读取面板数据最后{n}行失败: {error_msg}")
                raise StorageError(error_msg)

            # 读取最后n行
            try:
                last_n_lines = panel.read_last_n_lines(n, field_values, dtypes)

                # 如果提供了columns参数并且结果不为空，则过滤列
                if (
                    columns is not None
                    and last_n_lines is not None
                    and not last_n_lines.empty
                ):
                    # 确保索引列始终包含在内
                    if (
                        panel.index_col not in columns
                        and panel.index_col in last_n_lines.columns
                    ):
                        columns = columns + [panel.index_col]

                    # 过滤列
                    columns_to_keep = [
                        col for col in columns if col in last_n_lines.columns
                    ]
                    last_n_lines = last_n_lines[columns_to_keep]

                # 记录成功日志
                if last_n_lines is None or last_n_lines.empty:
                    user_logger.warning(f"面板数据文件为空或只有表头: {panel_name}")
                else:
                    user_logger.info(
                        f"成功读取面板数据最后{n}行: {panel_name}, 共{len(last_n_lines)}行"
                    )

                return last_n_lines
            except FileNotFoundError as e:
                error_msg = f"面板数据文件不存在: {str(e)}"
                logger.error(error_msg)
                user_logger.error(
                    f"读取面板数据最后{n}行失败: {panel_name} - {error_msg}"
                )
                raise StorageError(error_msg)
            except ValueError as e:
                error_msg = f"读取面板数据最后{n}行参数错误: {str(e)}"
                logger.error(error_msg)
                user_logger.error(
                    f"读取面板数据最后{n}行失败: {panel_name} - {error_msg}"
                )
                raise StorageError(error_msg)
            except Exception as e:
                error_msg = f"读取面板数据最后{n}行失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"读取面板数据最后{n}行失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("read_last_n_lines", panel_name, e)
            error_msg = f"读取面板数据最后{n}行失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(
                f"读取面板数据最后{n}行时发生错误: {panel_name} - {str(e)}"
            )
            raise StorageError(error_msg)

    def get_header(
        self, panel_name: str, field_values: Dict[str, str] = None
    ) -> Optional[List[str]]:
        """获取面板数据文件的表头（列名）

        根据字段值确定面板数据文件，并读取该文件的表头。

        Args:
            panel_name: 面板数据名称
            field_values: 字段值映射，用于定位具体文件。如果是单层结构面板，可以为None

        Returns:
            Optional[List[str]]: 文件表头列名列表，如果文件不存在或为空则返回None

        Raises:
            StorageError: 获取失败时抛出
        """
        try:
            # 记录日志
            logger.info(
                f"开始获取面板数据文件表头: {panel_name}, field_values={field_values}"
            )
            user_logger.debug(f"开始获取面板数据文件表头: {panel_name}")

            # 加载面板数据
            try:
                panel = self._get_panel(panel_name)
            except FileNotFoundError:
                error_msg = f"面板数据不存在: {panel_name}"
                logger.error(error_msg)
                user_logger.error(f"获取面板数据表头失败: {error_msg}")
                raise StorageError(error_msg)

            # 获取表头
            try:
                header = panel.get_header(field_values)

                # 记录成功日志
                if header is None:
                    user_logger.warning(f"面板数据文件为空或无表头: {panel_name}")
                else:
                    user_logger.debug(
                        f"成功获取面板数据表头: {panel_name}, 列数: {len(header)}"
                    )

                return header

            except FileNotFoundError as e:
                error_msg = f"面板数据文件不存在: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"获取面板数据表头失败: {panel_name} - {error_msg}")
                raise StorageError(error_msg)
            except Exception as e:
                error_msg = f"获取面板数据表头失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"获取面板数据表头失败: {panel_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("get_header", panel_name, e)
            error_msg = f"获取面板数据表头失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"获取面板数据表头时发生错误: {panel_name} - {str(e)}")
            raise StorageError(error_msg)


# 全局变量，但不立即初始化
_panel_storage_service_instance = None


def _get_panel_storage_service() -> PanelStorageService:
    """获取PanelStorageService单例实例

    使用懒加载方式，只有在首次调用时才会创建实例

    Returns:
        PanelStorageService: 面板存储服务实例
    """
    global _panel_storage_service_instance
    if _panel_storage_service_instance is None:
        # 首次调用时初始化
        _panel_storage_service_instance = PanelStorageService()
        logger.debug("PanelStorageService实例已按需初始化")
    return _panel_storage_service_instance
