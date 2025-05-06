#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd
from typing import List, Optional, Dict, Union, Any, Tuple
import concurrent.futures

# 模块内的导入使用相对导入
from .layers.layers import Layers
from .metainfo.metainfo import MetaInfo
from .file_operator.csv_operator import CSVOperator

# 从顶层模块导入
from datawhale.logging import get_system_logger

# 系统日志记录器，用于详细技术日志
logger = get_system_logger(__name__)


class Dataset:
    """数据集对象

    表示一个具有多层文件结构的数据集。

    属性:
        layers: 层级结构对象
        level: 文件层级数
    """

    def __init__(
        self,
        name: str = None,
        folder: str = None,
        meta_folder: str = None,
        meta_info: MetaInfo = None,
        layers: Layers = None,
    ):
        self.name = name
        self.folder = folder
        self.meta_folder = meta_folder

        # 初始化元信息和层级结构
        self.meta_info = meta_info
        self.layers = layers

        logger.debug(
            f"Dataset初始化: name={name}, folder={folder}, meta_folder={meta_folder}"
        )

    @classmethod
    def create_dataset(cls, folder: str, meta_folder: str, meta_info: dict):
        """从元信息创建数据集，创建数据集文件夹和元信息文件

        Args:
            meta_info: 元信息字典
            meta_folder: 元信息文件夹的绝对路径
            folder: 数据集所在的上级文件夹的绝对路径
        """
        logger.info(f"开始创建数据集: folder={folder}, meta_folder={meta_folder}")
        # 验证元信息
        if not MetaInfo.is_valid_dict(meta_info):
            logger.error(f"无效的元信息格式: {meta_info}")
            raise ValueError("无效的元信息格式")

        # 创建元信息对象
        meta_info_obj = MetaInfo.from_dict(meta_info)

        # 在meta_folder中保存元信息文件
        os.makedirs(meta_folder, exist_ok=True)
        meta_info_obj.to_yaml(meta_folder)
        logger.debug(f"已保存元信息文件到: {meta_folder}")

        # 在folder中创建数据集文件夹
        dataset_folder = os.path.join(folder, meta_info_obj.name)
        os.makedirs(dataset_folder, exist_ok=True)
        logger.debug(f"已创建数据集文件夹: {dataset_folder}")

        # 创建Dataset实例并设置基本属性
        dataset = cls(
            name=meta_info_obj.name,
            folder=folder,
            meta_folder=meta_folder,
            meta_info=meta_info_obj,
            layers=Layers(meta_info_obj.structure_fields),
        )

        logger.info(f"数据集创建成功: {meta_info_obj.name}")
        return dataset

    @classmethod
    def load_dataset(cls, name: str, folder: str, meta_folder: str):
        """加载数据集对象, 从meta_folder中加载元信息文件，从folder中加载数据集文件夹

        Args:
            name: 数据集名称
            folder: 数据集所在的上级文件夹的绝对路径
            meta_folder: 元信息文件夹的绝对路径
        """
        logger.info(
            f"开始加载数据集: name={name}, folder={folder}, meta_folder={meta_folder}"
        )
        # 构建元信息文件路径
        meta_file_path = os.path.join(meta_folder, f"{name}.yaml")

        # 检查元信息文件是否存在
        if not os.path.exists(meta_file_path):
            logger.error(f"元信息文件不存在: {meta_file_path}")
            raise FileNotFoundError(f"元信息文件不存在: {meta_file_path}")

        # 检查数据集文件夹是否存在
        dataset_folder = os.path.join(folder, name)
        if not os.path.exists(dataset_folder):
            logger.error(f"数据集文件夹不存在: {dataset_folder}")
            raise FileNotFoundError(f"数据集文件夹不存在: {dataset_folder}")

        # 加载元信息文件
        meta_info = MetaInfo.from_yaml(meta_file_path)
        logger.debug(f"已加载元信息文件: {meta_file_path}")

        # 创建Dataset实例并设置基本属性
        dataset = cls(
            name=name,
            folder=folder,
            meta_folder=meta_folder,
            meta_info=meta_info,
            layers=Layers(meta_info.structure_fields),  # 直接在构造函数中创建层级结构
        )

        logger.info(f"数据集加载成功: {name}")
        return dataset

    def _validate_save_params(
        self, data: pd.DataFrame, save_mode: str, update_key: str = None
    ) -> None:
        """验证保存参数的有效性

        Args:
            data: 要保存的数据
            save_mode: 保存模式
            update_key: 更新键

        Raises:
            ValueError: 当参数无效时抛出
        """
        # 验证保存模式是否有效
        if save_mode not in ["overwrite", "append", "update"]:
            logger.error(f"无效的保存模式: {save_mode}")
            raise ValueError(
                f"无效的保存模式: {save_mode}，有效值为'overwrite'、'append'或'update'"
            )

        # 如果是update模式，但未提供update_key，则使用错误处理
        if save_mode == "update" and update_key is None:
            logger.error(f"在'update'模式下必须提供update_key参数")
            raise ValueError(f"在'update'模式下必须提供update_key参数")

        # 如果是update模式，检查update_key是否在数据列中
        if save_mode == "update" and update_key is not None:
            if update_key not in data.columns:
                logger.error(f"更新键 '{update_key}' 不在数据列中")
                raise ValueError(f"更新键 '{update_key}' 不在数据列中")

    def _get_file_path(self, field_values: Dict[str, str]) -> Tuple[str, str]:
        """根据字段值构建文件路径

        Args:
            field_values: 字段值映射

        Returns:
            Tuple[str, str]: 文件路径和文件扩展名
        """
        # 单层结构数据集的特殊处理
        if not field_values and self.meta_info.dataset_level == 1:
            # 使用默认路径
            file_ext = self.meta_info.format.lower()
            file_path = os.path.join(self.folder, self.name, f"data.{file_ext}")
            logger.debug(f"单层数据集，使用默认文件路径: {file_path}")
        else:
            # 使用layers验证字段值
            self.layers.validate_field_values(field_values)

            # 确定文件扩展名
            file_ext = self.meta_info.format.lower()

            # 使用layers构建文件路径（不含扩展名）
            file_path_without_ext = self.layers.build_file_path(
                self.folder, self.name, field_values
            )

            # 添加文件扩展名
            file_path = f"{file_path_without_ext}.{file_ext}"
            logger.debug(f"目标文件路径: {file_path}")

        return file_path, file_ext

    def _validate_header_match(self, file_path: str, data: pd.DataFrame) -> bool:
        """验证CSV文件表头与新数据列是否匹配

        Args:
            file_path: 文件路径
            data: 要保存的数据

        Returns:
            bool: 如果表头匹配返回True，否则返回False
        """
        with open(file_path, "r", encoding="utf-8") as f:
            header = f.readline().strip()
            if header:  # 如果文件有表头
                existing_columns = header.split(",")
                if existing_columns != list(data.columns):
                    logger.error(
                        f"新数据的列与现有文件不匹配。现有列：{existing_columns}，新数据列：{list(data.columns)}"
                    )
                    return False
                return True
            return True  # 如果文件为空或没有表头，默认返回True

    def _process_update_mode_batch(
        self, data: pd.DataFrame, last_rows: pd.DataFrame, update_key: str
    ) -> Tuple[pd.DataFrame, str]:
        """处理批量更新模式的数据

        Args:
            data: 要保存的数据
            last_rows: 文件中的最后几行数据
            update_key: 更新键

        Returns:
            Tuple[pd.DataFrame, str]: 处理后的数据和更新后的保存模式
        """
        # 如果没有读取到数据，直接覆盖
        if last_rows is None or last_rows.empty:
            logger.debug(f"文件为空或只有表头，写入所有数据")
            return data, "overwrite"

        # 检查update_key是否在文件的列中
        if update_key not in last_rows.columns:
            logger.error(f"更新键 '{update_key}' 不在目标文件的列中")
            raise ValueError(f"更新键 '{update_key}' 不在目标文件的列中")

        # 获取最后一行的update_key值
        last_value = last_rows[update_key].max()

        # 筛选出update_key值大于last_value的行
        new_data_gt = data[data[update_key] > last_value].copy()

        # 找出等于last_value的数据并进行比较
        equal_last_value_data = data[data[update_key] == last_value].copy()
        equal_last_value_existing = last_rows[
            last_rows[update_key] == last_value
        ].copy()

        # 如果有等于last_value的数据需要比较
        if not equal_last_value_data.empty:
            logger.debug(
                f"发现{len(equal_last_value_data)}行等于最大值{last_value}的数据，进行去重比较"
            )

            # 确保两个DataFrame有相同的列用于比较
            compare_columns = [
                col
                for col in equal_last_value_data.columns
                if col in equal_last_value_existing.columns
            ]
            if len(compare_columns) == 0:
                logger.warning(f"无法进行比较，新旧数据没有共同列")
            else:
                # 标记在equal_last_value_existing中已存在的记录
                def row_exists(row):
                    query_str = " & ".join(
                        [f'({col} == @row["{col}"])' for col in compare_columns]
                    )
                    matches = equal_last_value_existing.query(query_str)
                    return len(matches) > 0

                # 找出不在现有数据中的新记录
                equal_last_value_unique = equal_last_value_data[
                    ~equal_last_value_data.apply(row_exists, axis=1)
                ]
                logger.debug(
                    f"发现{len(equal_last_value_unique)}行等于最大值但不在现有数据中的记录"
                )

                # 将新记录添加到new_data_gt
                if len(equal_last_value_unique) > 0:
                    new_data = pd.concat(
                        [new_data_gt, equal_last_value_unique], ignore_index=True
                    )
                else:
                    new_data = new_data_gt
        else:
            new_data = new_data_gt

        if len(new_data) > 0:
            # 只追加新数据
            logger.debug(f"筛选出{len(new_data)}行新数据进行追加")
            return new_data, "append"
        else:
            logger.info(f"没有需要更新的新数据")
            return None, None

    def _process_update_mode_single(
        self, data: pd.DataFrame, last_row: pd.DataFrame, update_key: str
    ) -> Tuple[pd.DataFrame, str]:
        """处理单行更新模式的数据

        Args:
            data: 要保存的数据
            last_row: 文件中的最后一行数据
            update_key: 更新键

        Returns:
            Tuple[pd.DataFrame, str]: 处理后的数据和更新后的保存模式
        """
        # 如果没有读取到数据，直接覆盖
        if last_row is None or last_row.empty:
            logger.debug(f"文件为空或只有表头，写入所有数据")
            return data, "overwrite"

        # 检查update_key是否在文件的列中
        if update_key not in last_row.columns:
            logger.error(f"更新键 '{update_key}' 不在目标文件的列中")
            raise ValueError(f"更新键 '{update_key}' 不在目标文件的列中")

        # 获取最后一行的update_key值
        last_value = last_row[update_key].iloc[0]

        # 筛选出update_key值大于last_value的行
        new_data_gt = data[data[update_key] > last_value].copy()

        # 找出等于last_value的数据并进行比较
        equal_last_value_data = data[data[update_key] == last_value].copy()

        # 如果有等于last_value的数据需要比较
        if not equal_last_value_data.empty:
            logger.debug(
                f"发现{len(equal_last_value_data)}行等于最大值{last_value}的数据，进行去重比较"
            )

            # 确保两个DataFrame有相同的列用于比较
            compare_columns = [
                col for col in equal_last_value_data.columns if col in last_row.columns
            ]
            if len(compare_columns) == 0:
                logger.warning(f"无法进行比较，新旧数据没有共同列")
            else:
                # 标记在last_row中已存在的记录
                def row_exists(row):
                    query_str = " & ".join(
                        [f'({col} == @row["{col}"])' for col in compare_columns]
                    )
                    matches = last_row.query(query_str)
                    return len(matches) > 0

                # 找出不在现有数据中的新记录
                equal_last_value_unique = equal_last_value_data[
                    ~equal_last_value_data.apply(row_exists, axis=1)
                ]
                logger.debug(
                    f"发现{len(equal_last_value_unique)}行等于最大值但不在现有数据中的记录"
                )

                # 将新记录添加到new_data_gt
                if len(equal_last_value_unique) > 0:
                    new_data = pd.concat(
                        [new_data_gt, equal_last_value_unique], ignore_index=True
                    )
                else:
                    new_data = new_data_gt
        else:
            new_data = new_data_gt

        if len(new_data) > 0:
            # 只追加新数据
            logger.debug(f"筛选出{len(new_data)}行新数据进行追加")
            return new_data, "append"
        else:
            logger.info(f"没有需要更新的新数据")
            return None, None

    def save(
        self,
        data: pd.DataFrame,
        field_values: Dict[str, str] = None,
        mode: str = None,
        update_key: str = None,
        batch_size: int = None,
        dtypes: Dict[str, str] = None,
    ):
        """保存数据到数据集

        Args:
            data: 数据框
            field_values: 字段值映射，用于定位具体文件。对于单层数据集，可以为None
            mode: 保存模式，可选值：'overwrite'（覆盖）、'append'（追加）或'update'（智能更新）。
                 如果为None，则使用meta_info中定义的update_mode
            update_key: 当mode为'update'时，用于比较的列名，只有该列值大于文件最后一行对应值的数据才会被追加
            batch_size: 当需要进行批量比较时，指定读取的最后n行数据，默认为None表示只读取最后一行
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用meta_info中的dtypes
        """
        logger.info(f"开始保存数据: dataset={self.name}, rows={len(data)}")
        logger.debug(
            f"保存参数: field_values={field_values}, mode={mode}, update_key={update_key}, batch_size={batch_size}"
        )

        if field_values is None:
            field_values = {}

        # 确定保存模式
        save_mode = mode if mode is not None else self.meta_info.update_mode

        # 验证保存参数
        self._validate_save_params(data, save_mode, update_key)

        # 获取文件路径
        file_path, file_ext = self._get_file_path(field_values)

        # 如果未提供dtypes，使用默认值
        if dtypes is None:
            dtypes = self.meta_info.dtypes

        # 根据文件格式和更新模式保存数据
        if file_ext == "csv":
            # 创建CSVOperator读取CSV文件
            csv_operator = CSVOperator(dtypes)

            # 检查文件是否已存在
            if os.path.exists(file_path):
                logger.debug(f"文件已存在，使用{save_mode}模式保存: {file_path}")

                # 检查表头列名是否匹配
                if self._validate_header_match(file_path, data):
                    # 如果是update模式，需要处理数据更新逻辑
                    if save_mode == "update":
                        try:
                            # 根据是否提供batch_size来决定使用read_last_line还是read_last_n_lines
                            if batch_size is not None and batch_size > 0:
                                logger.debug(
                                    f"使用批量更新模式，读取最后{batch_size}行"
                                )
                                # 使用Dataset的read_last_n_lines方法获取最后batch_size行数据
                                last_rows = self.read_last_n_lines(
                                    batch_size, field_values, dtypes
                                )

                                # 处理批量更新
                                new_data, save_mode = self._process_update_mode_batch(
                                    data, last_rows, update_key
                                )

                                # 如果没有新数据需要更新，直接返回
                                if new_data is None:
                                    # 更新元信息并保存
                                    self.meta_info.to_yaml(self.meta_folder)
                                    return  # 没有需要更新的数据，直接返回

                                data = new_data

                            else:
                                # 使用Dataset的read_last_line方法获取最后一行数据
                                last_row = self.read_last_line(field_values, dtypes)

                                # 处理单行更新
                                new_data, save_mode = self._process_update_mode_single(
                                    data, last_row, update_key
                                )

                                # 如果没有新数据需要更新，直接返回
                                if new_data is None:
                                    # 更新元信息并保存
                                    self.meta_info.to_yaml(self.meta_folder)
                                    return  # 没有需要更新的数据，直接返回

                                data = new_data

                        except FileNotFoundError:
                            # 文件不存在，应该已经在前面的检查中排除，以防万一
                            logger.warning(f"文件不存在，将创建新文件: {file_path}")
                            save_mode = "overwrite"  # 切换为overwrite模式

                        except Exception as e:
                            logger.error(f"更新数据失败: {str(e)}")
                            raise ValueError(f"更新数据失败: {str(e)}")

                    # 使用确定的保存模式
                    csv_operator.save(file_path, data, save_mode, update_key)
                else:
                    logger.error(f"表头不匹配，无法保存数据: {file_path}")
                    raise ValueError(f"表头不匹配，无法保存数据: {file_path}")
            else:
                logger.debug(f"文件不存在，创建新文件: {file_path}")
                # 新文件，直接写入
                csv_operator.save(file_path, data, "overwrite")
        else:
            # 对于其他格式的文件可以扩展这里的代码
            logger.error(f"不支持的文件格式: {file_ext}")
            raise ValueError(f"不支持的文件格式: {file_ext}")

        # 更新元信息并保存
        # to_yaml方法会自动更新updated_at字段并保存元信息到yaml文件
        self.meta_info.to_yaml(self.meta_folder)
        logger.info(
            f"数据保存成功: dataset={self.name}, rows={len(data)}, file={file_path}"
        )

    def exists(self, field_values: Dict[str, str] = None) -> bool:
        """检查数据是否存在

        Args:
            field_values: 字段值映射，用于定位具体文件
        """
        logger.info(
            f"检查数据是否存在: dataset={self.name}, field_values={field_values}"
        )

        if field_values is None:
            # 仅检查数据集文件夹是否存在
            dataset_folder = os.path.join(self.folder, self.name)
            exists = os.path.exists(dataset_folder)
            logger.debug(f"检查数据集文件夹: {dataset_folder}, 结果: {exists}")
            return exists

        # 构建查询路径
        patterns = self._get_match_pattern(field_values)
        logger.debug(f"查询模式: {patterns}")

        # 检查是否有匹配的文件
        for pattern in patterns:
            glob_pattern = os.path.join(self.folder, pattern)
            # 添加通配符以匹配所有支持的文件格式
            matched_files = glob.glob(f"{glob_pattern}.*")
            if matched_files:
                logger.debug(f"找到匹配文件: {matched_files}")
                return True

            # 检查是否存在没有扩展名的文件或目录
            matched_items = glob.glob(glob_pattern)
            if matched_items:
                logger.debug(f"找到匹配项: {matched_items}")
                return True

        logger.debug(f"未找到匹配项: {field_values}")
        return False

    def _add_dataset_name_prefix(self, pattern: str) -> str:
        """为模式添加数据集名称前缀

        Args:
            pattern: 原始匹配模式

        Returns:
            添加了数据集名称前缀的模式
        """
        return os.path.join(self.name, pattern) if pattern else self.name

    def _get_match_pattern(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> List[str]:
        """根据部分字段值生成用于glob匹配的模式

        对于未提供值的字段，使用通配符*代替。
        支持字段值为单个值或值列表，始终返回模式列表。
        root值固定为数据集名称，不可被覆盖。

        例如，对于三层结构root->code->date:
        - 当提供code=1时，将生成["{name}/1/*"]
        - 当提供code=[1,2]时，将生成["{name}/1/*", "{name}/2/*"]

        Args:
            field_values: 部分字段名到字段值的映射，可以为None表示不指定任何字段。
                          字段值可以是单个值或值列表。

        Returns:
            用于glob匹配的模式字符串列表（相对于根目录）
        """
        # 准备要传递给layers的field_values
        if field_values is None:
            layer_field_values = {"root": self.name}
        else:
            # 创建field_values的副本，避免修改原始输入
            layer_field_values = field_values.copy()

            # 始终使用数据集名称作为root值，忽略用户可能提供的root值
            layer_field_values["root"] = self.name

        logger.debug(f"生成匹配模式: field_values={layer_field_values}")
        # 调用layers的get_match_pattern方法
        patterns = self.layers.get_match_pattern(layer_field_values)
        logger.debug(f"生成的匹配模式: {patterns}")
        return patterns

    def _find_matching_files(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> List[str]:
        """根据字段值查询匹配的文件列表

        Args:
            field_values: 字段名到字段值的映射

        Returns:
            匹配的文件路径列表
        """
        logger.debug(f"查找匹配文件: dataset={self.name}, field_values={field_values}")

        # 单层数据集特殊处理
        if not field_values and self.meta_info.dataset_level == 1:
            # 使用默认路径
            file_ext = self.meta_info.format.lower()
            file_path = os.path.join(self.folder, self.name, f"data.{file_ext}")
            logger.debug(f"单层数据集，使用默认文件路径: {file_path}")

            if os.path.exists(file_path):
                logger.debug(f"找到单层数据集文件: {file_path}")
                return [file_path]
            else:
                logger.warning(f"单层数据集文件不存在: {file_path}")
                return []

        # 多层数据集的处理逻辑
        # 获取匹配模式
        patterns = self._get_match_pattern(field_values)

        # 获取父目录路径（根目录）
        base_dir = self.folder

        # 用于存储找到的所有文件
        all_files = []

        # 对每个模式进行匹配
        for pattern in patterns:
            # 构建完整的glob模式
            glob_pattern = os.path.join(base_dir, pattern)
            logger.debug(f"使用glob模式: {glob_pattern}")

            # 添加通配符以匹配所有支持的文件格式
            matched_files = glob.glob(f"{glob_pattern}.*")

            # 如果没有找到带扩展名的文件，尝试匹配没有扩展名的文件
            if not matched_files:
                matched_files = glob.glob(glob_pattern)

            all_files.extend(matched_files)

        logger.debug(f"找到匹配文件: {len(all_files)} 个文件")
        return all_files

    def _process_file(
        self, file_path: str, dtypes: Dict[str, str] = None, columns: List[str] = None
    ) -> pd.DataFrame:
        """处理单个文件并返回数据

        Args:
            file_path: 文件路径
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用meta_info中的dtypes
            columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            pd.DataFrame: 读取的数据

        Raises:
            ValueError: 当文件格式不支持或读取文件发生错误时抛出
        """
        try:
            logger.debug(f"处理文件: {file_path}")
            # 根据文件扩展名选择读取方法
            file_ext = os.path.splitext(file_path)[1].lower()

            # 如果未提供dtypes，使用默认值
            if dtypes is None:
                dtypes = self.meta_info.dtypes

            if file_ext == ".csv":
                # 使用CSVOperator读取CSV文件
                csv_operator = CSVOperator(dtypes)
                df = csv_operator.query(file_path, columns)
            else:
                logger.error(f"不支持的文件格式: {file_ext}")
                raise ValueError(f"不支持的文件格式: {file_ext}")

            # 使用layers从文件路径中提取字段值
            extracted_fields = self.layers.extract_field_values(
                file_path, self.folder, self.name
            )
            logger.debug(f"从文件路径提取的字段值: {extracted_fields}")

            # 将提取的字段值添加到DataFrame中
            for field, value in extracted_fields.items():
                # 如果需要选择特定列且该字段不在选择列表中，或者DataFrame中已经有同名列，则跳过添加
                if (
                    columns is not None and field not in columns
                ) or field in df.columns:
                    continue
                df[field] = value

            return df
        except Exception as e:
            logger.error(f"读取文件失败: {file_path}, 错误: {str(e)}")
            raise ValueError(f"读取文件{file_path}时发生错误: {str(e)}")

    def _process_files_parallel(
        self,
        files: List[str],
        max_workers: int = None,
        dtypes: Dict[str, str] = None,
        file_dtypes_map: Dict[str, Dict[str, str]] = None,
        columns: List[str] = None,
    ) -> List[pd.DataFrame]:
        """并行处理多个文件

        Args:
            files: 文件路径列表
            max_workers: 最大工作线程数
            dtypes: 数据类型字典，指定各列的数据类型
            file_dtypes_map: 文件路径到数据类型字典的映射，优先级高于dtypes
            columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            List[pd.DataFrame]: 读取的数据列表

        Raises:
            ValueError: 当读取文件发生错误时抛出
        """
        logger.debug(f"使用并行处理读取{len(files)}个文件")
        dataframes = []

        # 使用ThreadPoolExecutor并行读取文件
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务并获取future对象
            future_to_file = {}

            # 根据是否提供file_dtypes_map来决定如何提交任务
            for file_path in files:
                # 如果有file_dtypes_map并且file_path在其中，则使用对应的dtypes
                if file_dtypes_map and file_path in file_dtypes_map:
                    file_dtypes = file_dtypes_map[file_path]
                    future = executor.submit(
                        self._process_file, file_path, file_dtypes, columns
                    )
                else:
                    # 否则使用统一的dtypes
                    future = executor.submit(
                        self._process_file, file_path, dtypes, columns
                    )
                future_to_file[future] = file_path

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    df = future.result()
                    dataframes.append(df)
                except Exception as e:
                    # 在并行处理中捕获并重新抛出异常
                    logger.error(f"并行处理文件失败: {file_path}, 错误: {str(e)}")
                    raise ValueError(f"读取文件{file_path}时发生错误: {str(e)}")

        return dataframes

    def _process_files_serial(
        self,
        files: List[str],
        dtypes: Dict[str, str] = None,
        file_dtypes_map: Dict[str, Dict[str, str]] = None,
        columns: List[str] = None,
    ) -> List[pd.DataFrame]:
        """串行处理多个文件

        Args:
            files: 文件路径列表
            dtypes: 数据类型字典，指定各列的数据类型
            file_dtypes_map: 文件路径到数据类型字典的映射，优先级高于dtypes
            columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            List[pd.DataFrame]: 读取的数据列表
        """
        logger.debug(f"使用串行处理读取{len(files)}个文件")
        dataframes = []

        # 串行处理文件
        for file_path in files:
            # 如果有file_dtypes_map并且file_path在其中，则使用对应的dtypes
            if file_dtypes_map and file_path in file_dtypes_map:
                file_dtypes = file_dtypes_map[file_path]
                df = self._process_file(file_path, file_dtypes, columns)
            else:
                # 否则使用统一的dtypes
                df = self._process_file(file_path, dtypes, columns)
            dataframes.append(df)

        return dataframes

    def query(
        self,
        field_values: Dict[str, Union[str, List[str], Any]] = None,
        sort_by: Optional[str] = None,
        parallel: bool = True,
        max_workers: int = None,
        columns: List[str] = None,
    ) -> pd.DataFrame:
        """根据字段值查询数据

        Args:
            field_values: 字段名到字段值的映射
            sort_by: 排序字段名，可选
            parallel: 是否使用并行读取，默认为True
            max_workers: 最大并行工作线程数，None表示使用默认值(CPU核心数*5)
            columns: 需要选择的列名列表，默认为None表示选择所有列

        Returns:
            查询结果DataFrame，如果没有找到匹配数据则返回空DataFrame

        Raises:
            ValueError: 当文件格式不支持或读取文件发生错误时抛出
        """
        logger.info(
            f"开始查询数据: dataset={self.name}, field_values={field_values}, sort_by={sort_by}, parallel={parallel}, columns={columns}"
        )

        # 查找匹配的文件
        all_files = self._find_matching_files(field_values)

        # 如果没有找到文件，返回空DataFrame
        if not all_files:
            logger.warning(
                f"未找到匹配的文件: dataset={self.name}, field_values={field_values}"
            )
            return pd.DataFrame()

        # 使用meta_info中的dtypes
        dtypes = self.meta_info.dtypes

        # 如果指定了columns，确保这些列在dtypes中存在
        if columns is not None:
            # 用于保存在dtypes中存在的列
            valid_columns = []
            for col in columns:
                if col in dtypes:
                    valid_columns.append(col)
                else:
                    logger.warning(f"列 {col} 不在dtypes中，将被忽略")

            # 更新columns为有效的列列表
            columns = valid_columns if valid_columns else None

        # 根据parallel参数决定是否使用并行处理
        if parallel and len(all_files) > 1:
            dataframes = self._process_files_parallel(
                all_files, max_workers, dtypes, None, columns
            )
        else:
            dataframes = self._process_files_serial(all_files, dtypes, None, columns)

        # 如果没有读取到任何数据，返回空DataFrame
        if not dataframes:
            logger.warning(f"未能读取到任何数据: {self.name}")
            return pd.DataFrame()

        # 合并所有DataFrame
        result = pd.concat(dataframes, ignore_index=True)

        # 如果指定了排序字段，对结果进行排序
        if sort_by is not None:
            if sort_by in result.columns:
                logger.debug(f"对结果按{sort_by}进行排序")
                result = result.sort_values(by=sort_by)
            else:
                logger.error(f"排序字段{sort_by}不存在于查询结果中")
                raise ValueError(f"排序字段{sort_by}不存在于查询结果中")

        logger.info(f"查询完成: dataset={self.name}, 获取{len(result)}行数据")
        return result

    def read_last_line(
        self,
        field_values: Optional[Dict[str, str]] = None,
        dtypes: Dict[str, str] = None,
    ) -> Optional[pd.DataFrame]:
        """读取指定文件的最后一行数据

        根据字段值确定数据文件，并读取该文件的最后一行。这对于智能更新模式下检查最新记录特别有用。

        Args:
            field_values: 字段名到字段值的映射，用于定位具体文件。如果是单层结构数据集，可以为None
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用meta_info中的dtypes

        Returns:
            包含最后一行数据的DataFrame，如果文件不存在或为空则返回None

        Raises:
            ValueError: 当field_values不足以确定唯一文件，或文件格式不支持时抛出
            FileNotFoundError: 当指定的文件不存在时抛出
        """
        logger.info(
            f"开始读取文件最后一行: dataset={self.name}, field_values={field_values}"
        )

        if field_values is None:
            field_values = {}

        # 单层结构数据集的特殊处理
        if not field_values and self.meta_info.dataset_level == 1:
            # 使用默认路径定位单一文件
            file_ext = self.meta_info.format.lower()
            file_path = os.path.join(self.folder, self.name, f"data.{file_ext}")
            logger.debug(f"单层数据集，使用默认文件路径: {file_path}")
        else:
            try:
                # 使用layers验证字段值
                self.layers.validate_field_values(field_values)

                # 确定文件扩展名
                file_ext = self.meta_info.format.lower()

                # 使用layers构建文件路径（不含扩展名）
                file_path_without_ext = self.layers.build_file_path(
                    self.folder, self.name, field_values
                )

                # 添加文件扩展名
                file_path = f"{file_path_without_ext}.{file_ext}"
                logger.debug(f"目标文件路径: {file_path}")
            except Exception as e:
                error_msg = f"构建文件路径失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            # 如果未提供dtypes，使用默认值
            if dtypes is None:
                dtypes = self.meta_info.dtypes

            # 根据文件格式读取最后一行
            if file_ext == "csv":
                # 使用CSVOperator读取CSV文件的最后一行
                csv_operator = CSVOperator(dtypes)
                last_line_df = csv_operator.read_last_line(file_path)

                if last_line_df is not None:
                    # 使用layers从文件路径中提取字段值
                    extracted_fields = self.layers.extract_field_values(
                        file_path, self.folder, self.name
                    )
                    logger.debug(f"从文件路径提取的字段值: {extracted_fields}")

                    # 将提取的字段值添加到DataFrame中
                    for field, value in extracted_fields.items():
                        # 如果DataFrame中已经有同名列，跳过添加
                        if field not in last_line_df.columns:
                            last_line_df[field] = value

                logger.info(f"成功读取文件最后一行: {file_path}")
                return last_line_df
            else:
                # 对于其他格式的文件可以扩展这里的代码
                logger.error(f"不支持的文件格式: {file_ext}")
                raise ValueError(f"不支持的文件格式: {file_ext}")

        except Exception as e:
            # 捕获并处理读取过程中的异常
            if isinstance(e, FileNotFoundError):
                raise e
            else:
                error_msg = f"读取文件最后一行失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def read_last_n_lines(
        self,
        n: int,
        field_values: Optional[Dict[str, str]] = None,
        dtypes: Dict[str, str] = None,
    ) -> Optional[pd.DataFrame]:
        """读取指定文件的最后n行数据

        根据字段值确定数据文件，并读取该文件的最后n行。这对于数据分析和智能更新模式特别有用。

        Args:
            n: 需要读取的行数
            field_values: 字段名到字段值的映射，用于定位具体文件。如果是单层结构数据集，可以为None
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用meta_info中的dtypes

        Returns:
            包含最后n行数据的DataFrame，如果文件为空返回None，
            如果文件只有表头则返回一个只有表头的空DataFrame

        Raises:
            ValueError: 当n不是正整数、field_values不足以确定唯一文件，或文件格式不支持时抛出
            FileNotFoundError: 当指定的文件不存在时抛出
        """
        logger.info(
            f"开始读取文件最后{n}行: dataset={self.name}, field_values={field_values}"
        )

        if n <= 0:
            error_msg = "n必须是正整数"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if field_values is None:
            field_values = {}

        # 单层结构数据集的特殊处理
        if not field_values and self.meta_info.dataset_level == 1:
            # 使用默认路径定位单一文件
            file_ext = self.meta_info.format.lower()
            file_path = os.path.join(self.folder, self.name, f"data.{file_ext}")
            logger.debug(f"单层数据集，使用默认文件路径: {file_path}")
        else:
            try:
                # 使用layers验证字段值
                self.layers.validate_field_values(field_values)

                # 确定文件扩展名
                file_ext = self.meta_info.format.lower()

                # 使用layers构建文件路径（不含扩展名）
                file_path_without_ext = self.layers.build_file_path(
                    self.folder, self.name, field_values
                )

                # 添加文件扩展名
                file_path = f"{file_path_without_ext}.{file_ext}"
                logger.debug(f"目标文件路径: {file_path}")
            except Exception as e:
                error_msg = f"构建文件路径失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            # 如果未提供dtypes，使用默认值
            if dtypes is None:
                dtypes = self.meta_info.dtypes

            # 根据文件格式读取最后n行
            if file_ext == "csv":
                # 使用CSVOperator读取CSV文件的最后n行
                csv_operator = CSVOperator(dtypes)
                last_n_lines_df = csv_operator.read_last_n_lines(file_path, n)

                if last_n_lines_df is not None:
                    # 使用layers从文件路径中提取字段值
                    extracted_fields = self.layers.extract_field_values(
                        file_path, self.folder, self.name
                    )
                    logger.debug(f"从文件路径提取的字段值: {extracted_fields}")

                    # 将提取的字段值添加到DataFrame中
                    for field, value in extracted_fields.items():
                        # 如果DataFrame中已经有同名列，跳过添加
                        if field not in last_n_lines_df.columns:
                            last_n_lines_df[field] = value

                logger.info(f"成功读取文件最后{n}行: {file_path}")
                return last_n_lines_df
            else:
                # 对于其他格式的文件可以扩展这里的代码
                logger.error(f"不支持的文件格式: {file_ext}")
                raise ValueError(f"不支持的文件格式: {file_ext}")

        except Exception as e:
            # 捕获并处理读取过程中的异常
            if isinstance(e, FileNotFoundError):
                raise e
            elif isinstance(e, ValueError) and "n必须是正整数" in str(e):
                raise e
            else:
                error_msg = f"读取文件最后{n}行失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def get_header(
        self,
        field_values: Optional[Dict[str, str]] = None,
    ) -> Optional[List[str]]:
        """获取指定文件的表头（列名）

        根据字段值确定数据文件，并读取该文件的表头。

        Args:
            field_values: 字段名到字段值的映射，用于定位具体文件。如果是单层结构数据集，可以为None

        Returns:
            Optional[List[str]]: 文件表头列名列表，如果文件不存在或为空则返回None

        Raises:
            ValueError: 当field_values不足以确定唯一文件，或文件格式不支持时抛出
            FileNotFoundError: 当指定的文件不存在时抛出
        """
        logger.info(
            f"开始读取文件表头: dataset={self.name}, field_values={field_values}"
        )

        if field_values is None:
            field_values = {}

        # 获取文件路径
        try:
            file_path, file_ext = self._get_file_path(field_values)
        except Exception as e:
            error_msg = f"构建文件路径失败: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            # 根据文件格式读取表头
            if file_ext == "csv":
                # 使用CSVOperator读取CSV文件的表头
                csv_operator = CSVOperator(self.meta_info.dtypes)
                header = csv_operator.read_header(file_path)

                if header:
                    logger.info(f"成功读取文件表头: {file_path}, 列数: {len(header)}")
                else:
                    logger.warning(f"文件为空或无表头: {file_path}")

                return header
            else:
                # 对于其他格式的文件可以扩展这里的代码
                logger.error(f"不支持的文件格式: {file_ext}")
                raise ValueError(f"不支持的文件格式: {file_ext}")

        except Exception as e:
            # 捕获并处理读取过程中的异常
            if isinstance(e, FileNotFoundError):
                raise e
            else:
                error_msg = f"读取文件表头失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def delete(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> bool:
        """删除数据

        根据字段值删除对应的数据文件。如果不提供字段值，则删除整个数据集（包括所有文件和数据集文件夹）。
        当删除整个数据集时，也会删除对应的元数据YAML文件。

        Args:
            field_values: 字段名到字段值的映射，用于定位要删除的文件。如果为None，则删除整个数据集。

        Returns:
            bool: 删除操作是否成功

        Raises:
            ValueError: 当删除文件发生错误时抛出
        """
        logger.info(f"开始删除数据: dataset={self.name}, field_values={field_values}")

        try:
            # 如果field_values为None，删除整个数据集
            if field_values is None:
                # 删除数据集文件夹
                dataset_folder = os.path.join(self.folder, self.name)
                if os.path.exists(dataset_folder):
                    # 使用shutil.rmtree递归删除整个目录及其内容
                    import shutil

                    logger.debug(f"删除数据集文件夹: {dataset_folder}")
                    shutil.rmtree(dataset_folder)

                # 删除元数据YAML文件
                if self.meta_folder:
                    meta_file = os.path.join(self.meta_folder, f"{self.name}.yaml")
                    if os.path.exists(meta_file):
                        logger.debug(f"删除元数据文件: {meta_file}")
                        os.remove(meta_file)

                logger.info(f"已删除整个数据集: {self.name}")
                # 返回删除成功
                return True
            else:
                # 如果数据集文件夹不存在，无需删除
                dataset_folder = os.path.join(self.folder, self.name)
                if not os.path.exists(dataset_folder):
                    logger.warning(f"数据集文件夹不存在，无需删除: {dataset_folder}")
                    return True

            # 查找匹配的文件
            all_files = self._find_matching_files(field_values)

            # 如果没有找到文件，直接返回成功（没有需要删除的内容）
            if not all_files:
                logger.info(f"未找到匹配的文件，无需删除: field_values={field_values}")
                return True

            # 删除所有匹配的文件
            for file_path in all_files:
                if os.path.exists(file_path):
                    logger.debug(f"删除文件: {file_path}")
                    os.remove(file_path)

            # 删除可能为空的目录
            self._clean_empty_directories()

            logger.info(
                f"删除数据成功: dataset={self.name}, 删除{len(all_files)}个文件"
            )
            # 返回删除成功
            return True

        except Exception as e:
            # 捕获并处理删除过程中的异常
            logger.error(f"删除数据失败: {str(e)}")
            raise ValueError(f"删除数据时发生错误: {str(e)}")

    def _clean_empty_directories(self):
        """清理数据集中的空目录

        在删除文件后，可能会留下空的目录。这个方法会递归清理数据集中的空目录。
        """
        dataset_folder = os.path.join(self.folder, self.name)
        if not os.path.exists(dataset_folder):
            return

        logger.debug(f"开始清理空目录: {dataset_folder}")

        # 定义递归清理空目录的函数
        def clean_empty_dir(dir_path):
            # 如果目录不存在，直接返回
            if not os.path.exists(dir_path):
                return

            # 检查目录是否为空
            items = os.listdir(dir_path)

            # 先递归处理子目录
            for item in items:
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    clean_empty_dir(item_path)

            # 重新检查目录是否为空（可能在上面的递归中已经被清空）
            items = os.listdir(dir_path)

            # 如果目录为空且不是数据集根目录，则删除
            if len(items) == 0 and dir_path != dataset_folder:
                logger.debug(f"删除空目录: {dir_path}")
                os.rmdir(dir_path)

        # 清理数据集目录中的空目录
        clean_empty_dir(dataset_folder)
        logger.debug(f"空目录清理完成")

    def __str__(self) -> str:
        """返回数据集的字符串表示

        Returns:
            数据集名称和层级数的字符串表示
        """
        level = self.meta_info.dataset_level if self.meta_info else 0
        return f"Dataset(name={self.name}, level={level})"
