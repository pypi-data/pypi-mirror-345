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
from .dataset import Dataset
from .metainfo.metainfo import MetaInfo

# 系统日志记录器，用于详细技术日志
logger = get_system_logger(__name__)
# 用户日志记录器，用于记录主要操作和状态变化
user_logger = get_user_logger(__name__)


class StorageService:
    """新版文件存储服务实现

    提供基于元数据配置的文件存储服务，支持灵活的文件结构和数据管理。

    主要功能：
    1. 基于元数据配置的存储结构管理
    2. 多层文件结构支持
    3. 可扩展的更新策略
    4. 集成的元数据管理
    5. 基础的数据操作（保存、加载、删除）

    属性：
        data_dir (str): 存储服务的基础目录路径
        metainfo_dir (str): 元数据目录路径
        encoding (str): 文件编码方式
        default_format (str): 默认文件格式
    """

    def __init__(self, storage_config=None):
        """初始化存储服务

        使用storage.yaml配置文件中的配置初始化存储服务。

        Args:
            storage_config: 存储配置，如果为None则从配置系统获取
        """
        # 如果没有提供配置，则从config装饰器获取
        if storage_config is None:
            config_manager = get_config()
            storage_config = config_manager.get("storage", {})

        # 检查dataset_dir是否为None，如果是，则使用提供的data_dir
        dataset_dir = storage_config.get("dataset_dir")
        if dataset_dir is None:
            dataset_dir = storage_config.get("data_dir")
            if dataset_dir is None:
                raise ValueError("必须提供dataset_dir或data_dir配置项")

        # 规范化路径分隔符，确保跨平台兼容性
        self.data_dir = os.path.normpath(os.path.abspath(dataset_dir))

        # 检查runtime_dir是否为None
        runtime_dir = storage_config.get("runtime_dir")
        if runtime_dir is None:
            raise ValueError("必须提供runtime_dir配置项")

        # 规范化路径分隔符，确保跨平台兼容性
        runtime_dir = os.path.normpath(os.path.abspath(runtime_dir))
        metainfo_dir_name = storage_config.get("metainfo_dir", "metainfo")
        self.metainfo_dir = os.path.normpath(
            os.path.join(runtime_dir, metainfo_dir_name)
        )

        # 设置编码和默认格式
        self.encoding = storage_config.get("encoding", "utf-8")
        self.default_format = storage_config.get("format", "csv")

        # 确保必要目录存在
        self._init_storage()

        logger.info(
            f"存储服务初始化完成：data_dir={self.data_dir}, metainfo_dir={self.metainfo_dir}, "
            f"encoding={self.encoding}, default_format={self.default_format}"
        )
        user_logger.info("存储服务初始化完成")

    def _init_storage(self) -> None:
        """初始化存储环境

        创建基础存储目录和元数据目录。

        Raises:
            StorageError: 初始化失败时抛出
        """
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.metainfo_dir, exist_ok=True)
            logger.info("存储环境初始化成功")
        except Exception as e:
            error_msg = f"初始化存储环境失败：{str(e)}\n{traceback.format_exc()}"
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
            "data_dir": self.data_dir,
            "metainfo_dir": self.metainfo_dir,
            "layer": "infrastructure_pro",
            "service": self.__class__.__name__,
            "operation_id": f"{operation}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "module": "storage",
            "component": "storage_service",
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

    def save(
        self,
        data: pd.DataFrame,
        data_name: str,
        field_values: Dict[str, str] = None,
        mode: str = None,
        update_key: str = None,
        **kwargs,
    ) -> bool:
        """保存数据

        根据元数据配置保存数据到对应的文件结构中。

        Args:
            data: 要保存的数据
            data_name: 数据名称
            field_values: 字段值映射，用于直接指定动态层的值
            mode: 更新模式，如果为None则使用元数据中的默认值
                可选值："overwrite"（覆盖）、"append"（追加）或"update"（智能更新）
            update_key: 当mode为'update'时，用于比较的列名，只有该列值大于文件最后一行对应值的数据才会被追加
            **kwargs: 额外参数，传递给底层保存函数
                - index: 是否保存行索引，默认False

        Returns:
            bool: 保存是否成功

        Raises:
            StorageError: 保存失败时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始保存数据: {data_name}")
            logger.info(
                f"StorageService开始保存数据: {data_name}, rows={len(data)}, field_values={field_values}, mode={mode}, update_key={update_key}"
            )

            # 加载或创建数据集
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                error_msg = f"数据集不存在: {data_name}"
                logger.error(error_msg)
                user_logger.error(f"保存数据失败: {error_msg}")
                raise StorageError(error_msg)

            # 执行保存操作
            try:
                # 子日志记录由dataset.save()内部处理，无需在这里重复记录详细操作日志
                dataset.save(data, field_values, mode, update_key)

                # 记录成功日志
                user_logger.info(f"成功保存数据: {data_name}, 共{len(data)}行")
                return True
            except Exception as e:
                error_msg = f"保存数据失败: {str(e)}"
                # 不再重复记录具体错误日志，因为dataset.save()内部已经记录
                user_logger.error(f"保存数据失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("save", data_name, e)
            error_msg = f"保存数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"保存数据时发生错误: {data_name} - {str(e)}")
            raise StorageError(error_msg)

    def query(
        self, data_name: str, field_values: Dict[str, str] = None, **kwargs
    ) -> Optional[pd.DataFrame]:
        """加载数据

        根据元数据配置和字段值加载数据。

        Args:
            data_name: 数据名称
            field_values: 字段值映射，用于定位具体文件
            **kwargs: 额外参数，传递给底层加载函数
                - sort_by: 排序字段
                - parallel: 是否并行加载
                - max_workers: 最大工作线程数
                - columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            Optional[pd.DataFrame]: 加载的数据，文件不存在时返回None

        Raises:
            StorageError: 加载失败时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始加载数据: {data_name}")

            # 设置默认参数
            sort_by = kwargs.pop("sort_by", None)
            parallel = kwargs.pop("parallel", True)
            max_workers = kwargs.pop("max_workers", None)
            columns = kwargs.pop("columns", None)

            logger.info(
                f"StorageService开始查询数据: {data_name}, field_values={field_values}, sort_by={sort_by}, parallel={parallel}, columns={columns}"
            )

            # 加载数据集
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                error_msg = f"数据集不存在: {data_name}"
                logger.error(error_msg)
                user_logger.error(f"加载数据失败: {error_msg}")
                raise StorageError(error_msg)

            # 执行查询操作
            try:
                # 子日志记录由dataset.query()内部处理，无需在这里重复记录详细操作日志
                data = dataset.query(
                    field_values, sort_by, parallel, max_workers, columns
                )

                # 如果查询结果为空DataFrame，则记录警告
                if data.empty:
                    user_logger.warning(f"查询的数据为空: {data_name}")
                else:
                    # 记录成功日志（不重复记录详细信息）
                    user_logger.info(f"成功加载数据: {data_name}, 共{len(data)}行")

                return data
            except Exception as e:
                error_msg = f"加载数据失败: {str(e)}"
                # 不再重复记录具体错误日志，因为dataset.query()内部已经记录
                user_logger.error(f"加载数据失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("load", data_name, e)
            error_msg = f"加载数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"加载数据时发生错误: {data_name} - {str(e)}")
            raise StorageError(error_msg)

    def delete(self, data_name: str, field_values: Dict[str, str] = None) -> bool:
        """删除数据

        根据元数据配置和字段值删除数据文件。

        Args:
            data_name: 数据名称
            field_values: 字段值映射，用于定位具体文件。如果为None则删除整个数据集。

        Returns:
            bool: 删除是否成功

        Raises:
            StorageError: 删除失败时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始删除数据: {data_name}")
            logger.info(
                f"StorageService开始删除数据: {data_name}, field_values={field_values}"
            )

            # 加载数据集
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                # 数据集不存在，当作已删除处理
                logger.warning(f"数据集不存在，无需删除: {data_name}")
                user_logger.info(f"数据集不存在，无需删除: {data_name}")
                return True

            # 使用Dataset类的delete方法执行删除操作
            try:
                # 子日志记录由dataset.delete()内部处理，无需在这里重复记录详细操作日志
                result = dataset.delete(field_values)

                # 记录成功日志
                if field_values is None:
                    user_logger.info(f"成功删除数据集: {data_name}")
                else:
                    user_logger.info(f"成功删除数据: {data_name}")

                return result
            except Exception as e:
                error_msg = f"删除数据失败: {str(e)}"
                # 不再重复记录具体错误日志，因为dataset.delete()内部已经记录
                user_logger.error(f"删除数据失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("delete", data_name, e)
            error_msg = f"删除数据失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"删除数据时发生错误: {data_name} - {str(e)}")
            raise StorageError(error_msg)

    def exists(self, data_name: str, field_values: Dict[str, str] = None) -> bool:
        """检查数据是否存在

        根据元数据配置和字段值检查数据文件是否存在。

        Args:
            data_name: 数据名称
            field_values: 字段值映射，用于定位具体文件

        Returns:
            bool: 数据是否存在

        Raises:
            StorageError: 检查失败时抛出
        """
        try:
            logger.info(f"检查数据是否存在: {data_name}, field_values={field_values}")

            # 检查数据集是否存在
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                logger.debug(f"数据集不存在: {data_name}")
                return False

            # 使用Dataset类的exists方法检查数据是否存在
            # 子日志记录由dataset.exists()内部处理，无需在这里重复记录详细操作日志
            return dataset.exists(field_values)

        except Exception as e:
            context = self._log_operation_context("exists", data_name, e)
            error_msg = f"检查文件存在性失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            raise StorageError(error_msg)

    def _get_dataset(self, data_name: str) -> Dataset:
        """获取数据集对象

        Args:
            data_name: 数据集名称

        Returns:
            Dataset: 数据集对象

        Raises:
            FileNotFoundError: 数据集不存在时抛出
        """
        logger.debug(f"获取数据集对象: {data_name}")
        return Dataset.load_dataset(data_name, self.data_dir, self.metainfo_dir)

    def create_dataset(
        self,
        name: str,
        dtypes: Dict,
        format: str = None,
        structure_fields: List[str] = None,
        update_mode: str = None,
    ) -> Dataset:
        """创建新的数据集

        创建数据集前会检查参数有效性，并验证数据集文件夹和元数据文件是否已存在。
        如果已存在则会抛出错误，避免意外覆盖现有数据。

        Args:
            name: 数据集名称
            dtypes: 数据类型配置，不能为空
            format: 文件格式，默认使用配置中的default_format
            structure_fields: 文件结构字段列表，用于确定文件层级结构
            update_mode: 更新模式，可选值："append"（追加）、"overwrite"（覆盖）或"update"（智能更新），默认为"append"

        Returns:
            Dataset: 创建的数据集对象

        Raises:
            StorageError: 参数无效或文件/文件夹已存在时抛出
        """
        try:
            # 记录用户日志
            user_logger.info(f"开始创建数据集: {name}")
            # 计算层级数 (层级数=结构字段数+1)
            dataset_level = len(structure_fields) + 1 if structure_fields else 1
            logger.info(
                f"StorageService开始创建数据集: name={name}, level={dataset_level}, format={format}, update_mode={update_mode}"
            )

            # 检查dtypes是否为空
            if dtypes is None or len(dtypes) == 0:
                error_msg = f"数据类型配置(dtypes)不能为空"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

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

            # 检查数据集文件夹是否已存在
            dataset_folder = os.path.join(self.data_dir, name)
            if os.path.exists(dataset_folder):
                error_msg = f"数据集文件夹已存在: {name}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 检查元数据文件是否已存在
            meta_file = os.path.join(self.metainfo_dir, f"{name}.yaml")
            if os.path.exists(meta_file):
                error_msg = f"数据集元数据文件已存在: {name}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 创建元数据字典
            meta_info = {
                "name": name,
                "format": format,
                "dtypes": dtypes,
                "update_mode": update_mode,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # 如果有结构字段，添加dataset部分
            if structure_fields:
                meta_info["dataset"] = {"structure_fields": structure_fields}

            # 验证元数据是否满足要求
            if not MetaInfo.is_valid_dict(meta_info):
                error_msg = f"无效的元数据格式: {name}"
                logger.error(error_msg)
                user_logger.error(error_msg)
                raise StorageError(error_msg)

            # 创建数据集
            # 子日志记录由Dataset.create_dataset()内部处理，无需在这里重复记录详细操作日志
            dataset = Dataset.create_dataset(
                self.data_dir, self.metainfo_dir, meta_info
            )

            # 记录成功日志
            user_logger.info(f"成功创建数据集: {name}, 层级结构: {dataset_level}")

            return dataset

        except Exception as e:
            # 如果是已知的StorageError，直接抛出
            if isinstance(e, StorageError):
                raise

            # 其他异常，记录详细信息并包装为StorageError
            context = self._log_operation_context("create_dataset", name, e)
            error_msg = f"创建数据集失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"创建数据集时发生错误: {name} - {str(e)}")
            raise StorageError(error_msg)

    def read_last_line(
        self, data_name: str, field_values: Dict[str, str] = None
    ) -> Optional[pd.DataFrame]:
        """读取数据集文件的最后一行数据

        根据元数据配置和字段值读取对应的文件的最后一行数据，用于智能更新模式下获取数据的最新记录。

        Args:
            data_name: 数据集名称
            field_values: 字段值映射，用于定位具体文件

        Returns:
            Optional[pd.DataFrame]: 包含最后一行数据的DataFrame，文件不存在或为空则返回None

        Raises:
            StorageError: 读取失败时抛出
        """
        try:
            logger.info(
                f"读取数据集文件最后一行: {data_name}, field_values={field_values}"
            )

            # 获取数据集对象
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                error_msg = f"数据集不存在: {data_name}"
                logger.error(error_msg)
                user_logger.error(f"读取数据最后一行失败: {error_msg}")
                raise StorageError(error_msg)

            # 使用Dataset类的read_last_line方法读取最后一行
            try:
                # 子日志记录由dataset.read_last_line()内部处理，无需在这里重复记录详细操作日志
                last_line_df = dataset.read_last_line(field_values)

                if last_line_df is None or last_line_df.empty:
                    logger.info(f"数据集文件为空或不存在: {data_name}")
                    return None

                logger.info(f"成功读取数据集文件最后一行: {data_name}")
                return last_line_df

            except FileNotFoundError as e:
                logger.warning(f"指定的文件不存在: {str(e)}")
                return None

            except Exception as e:
                error_msg = f"读取数据最后一行失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"读取数据最后一行失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("read_last_line", data_name, e)
            error_msg = f"读取数据最后一行失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"读取数据最后一行时发生错误: {data_name} - {str(e)}")
            raise StorageError(error_msg)

    def get_dataset(self, data_name: str) -> Dataset:
        """获取数据集对象（公开接口）

        Args:
            data_name: 数据集名称

        Returns:
            Dataset: 数据集对象

        Raises:
            StorageError: 数据集不存在时抛出
        """
        try:
            return self._get_dataset(data_name)
        except FileNotFoundError as e:
            error_msg = f"数据集不存在: {data_name}"
            logger.error(error_msg)
            raise StorageError(error_msg)

    def read_last_n_lines(
        self, data_name: str, n: int, field_values: Dict[str, str] = None
    ) -> Optional[pd.DataFrame]:
        """读取数据集文件的最后n行数据

        根据元数据配置和字段值读取对应的文件的最后n行数据，用于智能更新模式下批量比较数据。

        Args:
            data_name: 数据集名称
            n: 需要读取的行数
            field_values: 字段值映射，用于定位具体文件

        Returns:
            Optional[pd.DataFrame]: 包含最后n行数据的DataFrame，文件不存在或为空则返回None

        Raises:
            StorageError: 读取失败时抛出
        """
        try:
            if n <= 0:
                error_msg = f"n必须是正整数，当前值为: {n}"
                logger.error(error_msg)
                raise StorageError(error_msg)

            logger.info(
                f"读取数据集文件最后{n}行: {data_name}, field_values={field_values}"
            )

            # 获取数据集对象
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                error_msg = f"数据集不存在: {data_name}"
                logger.error(error_msg)
                user_logger.error(f"读取数据最后{n}行失败: {error_msg}")
                raise StorageError(error_msg)

            # 使用Dataset类的read_last_n_lines方法读取最后n行
            try:
                # 子日志记录由dataset.read_last_n_lines()内部处理
                last_n_lines_df = dataset.read_last_n_lines(n, field_values)

                if last_n_lines_df is None:
                    logger.info(f"数据集文件为空或不存在: {data_name}")
                    return None
                elif last_n_lines_df.empty:
                    logger.info(f"数据集文件只有表头: {data_name}")

                logger.info(
                    f"成功读取数据集文件最后{n}行: {data_name}, 返回行数: {len(last_n_lines_df)}"
                )
                return last_n_lines_df

            except FileNotFoundError as e:
                logger.warning(f"指定的文件不存在: {str(e)}")
                return None

            except ValueError as e:
                error_msg = f"读取数据最后{n}行参数错误: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"读取数据最后{n}行失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

            except Exception as e:
                error_msg = f"读取数据最后{n}行失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"读取数据最后{n}行失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context(f"read_last_{n}_lines", data_name, e)
            error_msg = f"读取数据最后{n}行失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"读取数据最后{n}行时发生错误: {data_name} - {str(e)}")
            raise StorageError(error_msg)

    def get_header(
        self, data_name: str, field_values: Dict[str, str] = None
    ) -> Optional[List[str]]:
        """获取数据集文件的表头（列名）

        根据元数据配置和字段值获取对应文件的表头信息。

        Args:
            data_name: 数据集名称
            field_values: 字段值映射，用于定位具体文件

        Returns:
            Optional[List[str]]: 文件表头列名列表，如果文件不存在或为空则返回None

        Raises:
            StorageError: 获取表头失败时抛出
        """
        try:
            logger.info(
                f"开始获取数据集文件表头: {data_name}, field_values={field_values}"
            )

            # 获取数据集对象
            try:
                dataset = self._get_dataset(data_name)
            except FileNotFoundError:
                error_msg = f"数据集不存在: {data_name}"
                logger.error(error_msg)
                user_logger.error(f"获取文件表头失败: {error_msg}")
                raise StorageError(error_msg)

            # 获取文件表头
            try:
                header = dataset.get_header(field_values)

                if header is None:
                    logger.warning(f"文件为空或不存在: {data_name}")
                    return None

                logger.info(f"成功获取数据集文件表头: {data_name}, 列数: {len(header)}")
                return header

            except FileNotFoundError as e:
                logger.warning(f"指定的文件不存在: {str(e)}")
                return None

            except Exception as e:
                error_msg = f"获取文件表头失败: {str(e)}"
                logger.error(error_msg)
                user_logger.error(f"获取文件表头失败: {data_name} - {str(e)}")
                raise StorageError(error_msg)

        except Exception as e:
            context = self._log_operation_context("get_header", data_name, e)
            error_msg = f"获取文件表头失败: {str(e)}"
            logger.error(error_msg, extra={"storage_context": context})
            user_logger.error(f"获取文件表头时发生错误: {data_name} - {str(e)}")
            raise StorageError(error_msg)
