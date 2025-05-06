#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import concurrent.futures

# 模块内的导入使用相对导入
from .dataset import Dataset
from .metainfo.panel_metainfo import PanelMetaInfo
from .layers.layers import Layers
from .file_operator.csv_operator import CSVOperator


class Panel(Dataset):
    """面板数据类

    扩展了Dataset类，专门用于处理面板数据。
    面板数据通常以日期为索引，实体ID为列名，值为特定指标。

    支持多层文件夹结构，但最后一层是面板数据，其中有一列指定为日期列（索引列），
    一列指定为实体列（如实体ID），以及一个或多个值列。

    属性:
        name: 面板数据名称
        folder: 数据存储根目录
        meta_folder: 元数据存储目录
        meta_info: 面板数据元数据信息对象
        layers: 层级配置对象
        index_col: 索引列名称（日期列）
        entity_col_name: 实体列名称（存储实体ID的列名）
        value_dtype: 值数据类型
    """

    def __init__(
        self,
        name: str = None,
        folder: str = None,
        meta_folder: str = None,
        meta_info: PanelMetaInfo = None,
        layers=None,
    ):
        """初始化面板数据对象

        Args:
            name: 面板数据名称
            folder: 数据存储根目录
            meta_folder: 元数据存储目录
            meta_info: 面板数据元数据信息对象
            layers: 层级配置对象
        """
        # 调用父类初始化方法
        super().__init__(
            name=name,
            folder=folder,
            meta_folder=meta_folder,
            meta_info=meta_info,
            layers=layers,
        )

        # 添加面板数据特有的属性
        if isinstance(meta_info, PanelMetaInfo):
            self.index_col = meta_info.index_col
            self.entity_col_name = meta_info.entity_col_name
            self.value_dtype = meta_info.value_dtype
        else:
            self.index_col = None
            self.entity_col_name = "entity_id"  # 更通用的默认值
            self.value_dtype = "float64"

    @property
    def default_value_col(self) -> str:
        """获取默认的值列名称

        Returns:
            str: 默认值列名称 'value'
        """
        return "value"

    @classmethod
    def create_panel(
        cls,
        name: str,
        folder: str,
        meta_folder: str,
        index_col: str,
        value_dtype: str,
        entity_col_name: str = "entity_id",
        format: str = None,
        structure_fields: List[str] = None,
        update_mode: str = None,
    ) -> "Panel":
        """创建新的面板数据

        创建一个新的面板数据对象，初始化存储结构并生成元数据文件。
        面板数据采用结构化目录格式存储，文件路径基于structure_fields定义的层次结构。

        ### 存储结构说明
        - 基本目录：{folder}/{name}/
        - 结构化路径：若structure_fields=['region', 'indicator']，则文件存储在：
          {folder}/{name}/{region_value}/{indicator_value}.csv
        - 文件格式：CSV文件以宽格式存储，行索引为日期，列为实体ID

        ### 元数据作用
        元数据存储在{meta_folder}/{name}.yaml，包含以下关键信息：
        - 面板基本信息(名称、创建时间等)
        - 数据结构定义(索引列、实体列、字段结构等)
        - 存储格式和更新策略
        元数据文件用于后续加载和管理面板数据

        Args:
            name: 面板数据名称，会成为目录名的一部分
            folder: 数据存储根目录，所有数据文件将存储在此目录下的子文件夹中
            meta_folder: 元数据存储目录，元数据YAML文件将保存在此
            index_col: 索引列名称，通常是日期列的列名，如"date"
            value_dtype: 值数据类型，如"float64"，定义了数值数据的存储类型
            entity_col_name: 实体列名称，存储实体ID的列名，默认为'entity_id'
            format: 文件格式，默认为csv，目前仅支持CSV格式
            structure_fields: 文件结构字段列表，定义了文件的目录结构层次，如['region', 'indicator']
            update_mode: 更新模式，可选值：'overwrite'(覆盖)、'append'(追加)、'update'(智能更新)，默认为'append'

        Returns:
            Panel: 创建的面板数据对象

        Raises:
            ValueError: 当参数无效或面板数据已存在时抛出

        Example:
            >>> panel = Panel.create_panel(
            ...     name="stock_prices",
            ...     folder="/data/panels",
            ...     meta_folder="/data/metadata",
            ...     index_col="date",
            ...     value_dtype="float64",
            ...     entity_col_name="stock_id",
            ...     structure_fields=["market", "indicator"]
            ... )
        """
        # 创建元数据信息
        meta_info = PanelMetaInfo(
            name=name,
            index_col=index_col,
            value_dtype=value_dtype,
            entity_col_name=entity_col_name,
            format=format,
            structure_fields=structure_fields,
            update_mode=update_mode,
        )

        # 创建元数据文件
        meta_path = meta_info.to_yaml(meta_folder)

        # 创建层级配置
        layers = Layers(fields=structure_fields)

        # 确保面板数据目录存在
        panel_folder = os.path.join(folder, name)
        os.makedirs(panel_folder, exist_ok=True)

        # 创建面板数据实例
        panel = cls(
            name=name,
            folder=folder,
            meta_folder=meta_folder,
            layers=layers,
            meta_info=meta_info,
        )

        return panel

    @classmethod
    def load_panel(cls, name: str, folder: str, meta_folder: str) -> "Panel":
        """加载现有的面板数据

        Args:
            name: 面板数据名称
            folder: 数据存储根目录
            meta_folder: 元数据存储目录

        Returns:
            Panel: 加载的面板数据对象

        Raises:
            FileNotFoundError: 当元数据文件不存在时抛出
            ValueError: 当元数据无效时抛出
        """
        # 构建元数据文件路径
        meta_path = os.path.join(meta_folder, f"{name}.yaml")

        # 检查元数据文件是否存在
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"面板数据元数据文件不存在: {meta_path}")

        # 加载元数据信息
        meta_info = PanelMetaInfo.from_yaml(meta_path)

        # 创建层级配置
        layers = Layers(fields=meta_info.structure_fields)

        # 创建面板数据实例
        panel = cls(
            name=name,
            folder=folder,
            meta_folder=meta_folder,
            layers=layers,
            meta_info=meta_info,
        )

        return panel

    def save(
        self,
        data: pd.DataFrame,
        field_values: Dict[str, str] = None,
        mode: str = None,
        update_key: str = None,
        batch_size: int = None,
    ):
        """保存面板数据

        将数据保存到面板存储系统中，支持多种数据格式和更新模式。
        数据将始终以宽格式（面板格式）保存，自动处理长格式到宽格式的转换。

        ### 文件路径生成逻辑
        基于field_values和structure_fields构建文件路径：
        1. 基本路径：{folder}/{name}/
        2. 若structure_fields=['region', 'indicator']，field_values={'region': 'Asia', 'indicator': 'price'}
           则生成的路径为：{folder}/{name}/Asia/price.csv
        3. 如果field_values中缺少structure_fields中的某字段，会导致错误

        ### 更新模式说明
        1. overwrite(覆盖模式)：
           - 完全覆盖现有文件，丢弃原有所有数据
           - 不要求新旧数据的列结构一致
           - 适用于完全重建数据的场景

        2. append(追加模式)：
           - 将新数据直接追加到现有文件末尾
           - 要求新旧数据的列结构完全一致
           - 可能导致重复数据(如相同日期的数据被重复添加)
           - 适用于增量添加新日期数据的场景

        3. update(更新模式)：
           - 根据update_key(通常是日期列)智能合并数据
           - 对已存在的数据根据key进行更新，不存在的则追加
           - 要求update_key在新旧数据中都存在
           - 适用于既要更新现有数据又要添加新数据的场景

        Args:
            data: 要保存的面板数据DataFrame，支持宽格式或长格式
            field_values: 存储路径的字段值映射，如{'region': 'Asia', 'indicator': 'price'}
            mode: 更新模式，可选值：'overwrite'、'append'、'update'，如果为None，则使用meta_info中定义的update_mode
            update_key: 当mode为'update'时，用于比较和更新的键列名，通常是日期列
            batch_size: 当需要进行批量比较时，指定读取的最后n行数据，可优化大文件处理性能

        Raises:
            ValueError: 当数据格式不正确、更新模式无效或表头不匹配时抛出

        Example:
            >>> panel.save(
            ...     data=price_data,
            ...     field_values={"region": "Asia", "indicator": "price"},
            ...     mode="update",
            ...     update_key="date"
            ... )
        """
        logger = logging.getLogger(__name__)

        # 确保索引列存在
        if self.index_col not in data.columns:
            raise ValueError(f"索引列 {self.index_col} 不在数据列中")

        # 确保数据是面板格式（至少包含索引列和一个实体列）
        if len(data.columns) < 2:
            raise ValueError("数据列数量不足，至少需要索引列和一个实体列")

        # 判断数据格式：是宽格式还是长格式
        if self.entity_col_name in data.columns:
            # 长格式数据，需要转换为宽格式
            data = self.to_wide_format(data)

        # 构建完整的数据类型字典（面板数据特有）
        complete_dtypes = self._build_complete_dtypes_from_dataframe(data)

        # 确定保存模式
        save_mode = mode if mode is not None else self.meta_info.update_mode

        # 验证保存参数
        self._validate_save_params(data, save_mode, update_key)

        # 获取文件路径
        file_path, file_ext = self._get_file_path(field_values)

        # 只支持CSV格式
        if file_ext != "csv":
            logger.error(f"不支持的文件格式: {file_ext}，面板数据仅支持CSV格式")
            raise ValueError(f"不支持的文件格式: {file_ext}，面板数据仅支持CSV格式")

        # 创建CSVOperator读取CSV文件，使用面板数据特有的dtypes
        csv_operator = CSVOperator(complete_dtypes)

        # 检查文件是否已存在
        if os.path.exists(file_path):
            logger.debug(f"文件已存在，使用{save_mode}模式保存: {file_path}")

            # 根据不同的更新模式处理表头匹配
            if save_mode == "overwrite":
                # 覆盖模式直接覆盖文件，不需要检查表头
                logger.debug(f"覆盖模式: 直接覆盖文件，不检查表头")
                csv_operator.save(file_path, data, "overwrite")

                # 更新元信息并保存
                self.meta_info.to_yaml(self.meta_folder)
                logger.info(
                    f"数据保存成功: dataset={self.name}, rows={len(data)}, file={file_path}"
                )
                return

            elif save_mode == "append":
                # 追加模式必须进行表头匹配检查
                headers_match = self._validate_header_match(file_path, data)

                if not headers_match:
                    logger.error(f"追加模式: 表头不匹配，无法追加数据: {file_path}")
                    raise ValueError(f"追加模式: 表头不匹配，无法追加数据: {file_path}")

                # 直接追加
                csv_operator.save(file_path, data, "append")

                # 更新元信息并保存
                self.meta_info.to_yaml(self.meta_folder)
                logger.info(
                    f"数据保存成功: dataset={self.name}, rows={len(data)}, file={file_path}"
                )
                return

            elif save_mode == "update":
                # update模式下，不论列名是否匹配，都使用update_key进行更新
                try:
                    # 确保更新键存在
                    if update_key is None:
                        logger.error("更新模式需要指定update_key参数")
                        raise ValueError("更新模式需要指定update_key参数")

                    # 创建适合现有文件的CSVOperator
                    # 首先尝试读取文件头，获取所有列名
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            header = f.readline().strip()
                            existing_columns = header.split(",")

                        # 为现有列创建数据类型字典
                        existing_dtypes = {self.index_col: "string"}
                        for col in existing_columns:
                            if col != self.index_col:
                                existing_dtypes[col] = self.value_dtype

                        # 使用现有列创建CSVOperator
                        file_csv_operator = CSVOperator(existing_dtypes)

                        # 读取现有数据
                        existing_data = file_csv_operator.query(file_path)

                        if existing_data.empty:
                            # 如果文件为空，直接保存新数据
                            csv_operator = CSVOperator(complete_dtypes)
                            csv_operator.save(file_path, data, "overwrite")
                            logger.info(
                                f"数据保存成功: dataset={self.name}, rows={len(data)}, file={file_path}"
                            )
                            # 更新元信息并保存
                            self.meta_info.to_yaml(self.meta_folder)
                            return
                    else:
                        # 文件不存在，直接保存新数据
                        csv_operator.save(file_path, data, "overwrite")
                        logger.info(
                            f"数据保存成功: dataset={self.name}, rows={len(data)}, file={file_path}"
                        )
                        # 更新元信息并保存
                        self.meta_info.to_yaml(self.meta_folder)
                        return

                    # 将update_key设置为索引以便于合并
                    existing_data_indexed = existing_data.set_index(update_key)
                    new_data_indexed = data.set_index(update_key)

                    # 获取已存在的索引和新数据的索引
                    existing_indices = set(existing_data_indexed.index)
                    new_indices = set(new_data_indexed.index)

                    # 处理更新逻辑
                    # 1. 需要更新的行：已存在的行需要更新
                    indices_to_update = existing_indices.intersection(new_indices)
                    # 2. 需要追加的行：不存在的行需要追加
                    indices_to_append = new_indices.difference(existing_indices)

                    # 创建结果数据框架，初始为现有数据
                    result_data = existing_data_indexed.copy()

                    # 更新已存在的行
                    if indices_to_update:
                        for idx in indices_to_update:
                            # 只更新新数据中存在的列，保留其他列的原始值
                            for col in new_data_indexed.columns:
                                if col in result_data.columns:
                                    result_data.at[idx, col] = new_data_indexed.at[
                                        idx, col
                                    ]
                                else:
                                    # 如果列不存在，添加新列
                                    result_data[col] = None
                                    result_data.at[idx, col] = new_data_indexed.at[
                                        idx, col
                                    ]

                    # 追加新行
                    if indices_to_append:
                        # 确保新行的DataFrame具有与result_data相同的列
                        rows_to_append = new_data_indexed.loc[list(indices_to_append)]

                        # 在追加前确保所有列都存在
                        for col in result_data.columns:
                            if col not in rows_to_append.columns:
                                rows_to_append[col] = None

                        # 添加新行到结果DataFrame
                        result_data = pd.concat([result_data, rows_to_append])

                    # 重置索引并保存
                    result_data = result_data.reset_index()

                    # 更新数据类型字典，包含所有列
                    updated_dtypes = self._build_complete_dtypes_from_dataframe(
                        result_data
                    )
                    updated_csv_operator = CSVOperator(updated_dtypes)

                    # 保存结果
                    updated_csv_operator.save(file_path, result_data, "overwrite")

                    logger.info(
                        f"数据保存成功: dataset={self.name}, rows={len(result_data)}, file={file_path}"
                    )
                    # 更新元信息并保存
                    self.meta_info.to_yaml(self.meta_folder)
                    return
                except Exception as e:
                    logger.error(f"更新数据失败: {str(e)}")
                    raise

            else:
                logger.error(f"不支持的更新模式: {save_mode}")
                raise ValueError(f"不支持的更新模式: {save_mode}")

        else:
            logger.debug(f"文件不存在，创建新文件: {file_path}")
            # 新文件，直接写入
            csv_operator.save(file_path, data, "overwrite")

        # 更新元信息并保存
        # to_yaml方法会自动更新updated_at字段并保存元信息到yaml文件
        self.meta_info.to_yaml(self.meta_folder)
        logger.info(
            f"数据保存成功: dataset={self.name}, rows={len(data)}, file={file_path}"
        )

    def _build_complete_dtypes_from_dataframe(
        self, data: pd.DataFrame
    ) -> Dict[str, str]:
        """构建完整的数据类型映射，包括索引列和所有实体列（基于DataFrame）

        为面板数据的所有列创建一个统一的数据类型映射字典。
        这个映射字典用于CSV文件的读写操作，确保数据类型一致性。

        ### 数据类型分配规则
        1. 索引列(通常是日期列)：设置为'string'类型，以保持日期格式一致性
        2. 所有实体列：统一设置为value_dtype指定的类型(通常是'float64')
        3. 结构字段列：这些列在数据保存时不作为类型映射的一部分，而是编码在文件路径中

        Args:
            data: 要处理的面板数据DataFrame（宽格式），如果为None只返回基本的索引列类型

        Returns:
            Dict[str, str]: 完整的数据类型映射，键为列名，值为数据类型字符串

        Example:
            {
                'date': 'string',      # 索引列
                'AAPL': 'float64',     # 实体列
                'MSFT': 'float64',     # 实体列
                'GOOG': 'float64'      # 实体列
            }
        """
        # 开始时只包含索引列
        complete_dtypes = {self.index_col: "string"}

        if data is None:
            return complete_dtypes

        # 获取除索引列外的所有列（实体列）
        entity_columns = [col for col in data.columns if col != self.index_col]

        # 为每个实体列设置相同的类型
        for col in entity_columns:
            complete_dtypes[col] = self.value_dtype

        return complete_dtypes

    def _build_complete_dtypes_from_file(self, file_path: str) -> Dict[str, str]:
        """构建完整的数据类型映射，包括索引列和所有实体列（基于文件）

        通过读取文件的头部，为所有列创建一个统一的数据类型映射字典。
        这个方法特别适用于从现有文件创建数据类型映射的场景。

        ### 数据类型分配规则
        1. 索引列(通常是日期列)：设置为'string'类型
        2. 所有其他列(实体列)：统一设置为value_dtype指定的类型(通常是'float64')

        Args:
            file_path: 要处理的文件路径，用于提取列名

        Returns:
            Dict[str, str]: 完整的数据类型映射，键为列名，值为数据类型字符串

        Note:
            如果文件不存在、为空或读取失败，将返回一个只包含索引列的基本字典
        """
        # 开始时只包含索引列的基本数据类型
        complete_dtypes = {self.index_col: "string"}

        try:
            # 尝试从文件头部获取所有列名，然后为其构建dtypes
            with open(file_path, "r", encoding="utf-8") as f:
                header = f.readline().strip()
                if header:
                    columns = header.split(",")
                    for col in columns:
                        if col != self.index_col:
                            complete_dtypes[col] = self.value_dtype
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"从文件构建数据类型映射失败: {file_path}, 错误: {str(e)}")
            # 返回基本映射

        return complete_dtypes

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
            # 从文件路径中提取字段值
            extracted_fields = self.layers.extract_field_values(
                file_path, self.folder, self.name
            )

            # 首先检查空列表情况
            if columns is not None and len(columns) == 0:
                # 如果是空列表，则不进行列筛选，返回所有列
                columns = None

            # 根据文件扩展名选择读取方法
            file_ext = os.path.splitext(file_path)[1].lower()

            # 如果未提供dtypes，为此文件构建特定的dtypes
            if dtypes is None:
                dtypes = self._build_complete_dtypes_from_file(file_path)
                if dtypes is None:
                    dtypes = self.meta_info.dtypes

            # 如果指定了columns，先过滤出在dtypes中存在的列
            valid_columns = None
            if columns is not None:
                valid_columns = []
                for col in columns:
                    if col in dtypes:
                        valid_columns.append(col)
                    # 不在dtypes中的列不处理，与Dataset类行为一致

                # 确保索引列总是包含在内
                if self.index_col not in valid_columns and valid_columns:
                    valid_columns.append(self.index_col)

                # 如果没有有效列，至少应包含索引列
                if not valid_columns:
                    valid_columns = [self.index_col]

            if file_ext == ".csv":
                # 使用CSVOperator读取CSV文件
                csv_operator = CSVOperator(dtypes)
                df = csv_operator.query(file_path, valid_columns)

                # 如果DataFrame为空但需要索引列，则创建一个只有索引列的空DataFrame
                if df.empty and valid_columns and self.index_col in valid_columns:
                    return pd.DataFrame(columns=[self.index_col])
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")

            # 将提取的字段值添加到DataFrame中
            for field, value in extracted_fields.items():
                # 如果文件中已经有这个列，或者columns不为None且不包含这个字段，则跳过
                if field in df.columns or (
                    columns is not None and field not in columns
                ):
                    continue
                # 只添加列在valid_columns中的字段值
                if valid_columns is None or field in valid_columns:
                    df[field] = value

            return df
        except Exception as e:
            raise ValueError(f"读取文件{file_path}时发生错误: {str(e)}")

    def query(
        self,
        field_values: Dict[str, Union[str, List[str], Any]] = None,
        sort_by: Optional[str] = None,
        parallel: bool = True,
        max_workers: int = None,
        columns: List[str] = None,
        dtypes: Dict[str, str] = None,
    ) -> pd.DataFrame:
        """根据字段值查询面板数据

        查询匹配指定字段值的面板数据，支持精确匹配和部分匹配。

        ### 文件匹配逻辑
        1. 完全匹配：提供与structure_fields完全对应的field_values时，精确匹配单个文件
        2. 部分匹配：提供部分字段值时，匹配所有满足条件的文件
           例如：structure_fields=['region', 'indicator']
           - field_values={'region': 'Asia'} 会匹配所有Asia区域的所有指标文件
           - field_values={'indicator': 'price'} 会匹配所有区域的price指标文件
        3. 空匹配：不提供field_values或提供空字典时，匹配所有文件

        ### 多文件处理
        当匹配多个文件时：
        1. 默认并行读取所有匹配的文件(可通过parallel参数控制)
        2. 读取后自动合并为一个DataFrame
        3. 合并过程自动添加字段值列(如region列、indicator列)便于区分数据来源
        4. 合并结果可按指定列排序(通过sort_by参数)

        ### 返回数据格式
        始终返回宽格式的面板数据，格式为：
        - 一列日期列(index_col指定的列名)
        - 多列实体数据列(列名即为实体ID)
        - 结构字段列(如region、indicator列)，值为对应文件的field_value值

        Args:
            field_values: 字段名到字段值的映射，用于文件匹配过滤
                可提供精确值或值列表，如{'region': 'Asia'}或{'region': ['Asia', 'Europe']}
            sort_by: 排序字段名，结果会按此字段排序，通常为日期列
            parallel: 是否使用并行读取，默认为True，可加速大量文件读取
            max_workers: 最大并行工作线程数，None表示使用默认值(CPU核心数*5)
            columns: 需要选择的列名列表，默认为None表示选择所有列
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用自动构建的完整数据类型字典

        Returns:
            pd.DataFrame: 查询结果DataFrame，宽格式的面板数据
            如果没有找到匹配数据则返回空DataFrame

        Example:
            >>> # 查询亚洲地区的所有价格数据
            >>> price_data = panel.query(
            ...     field_values={"region": "Asia", "indicator": "price"},
            ...     sort_by="date"
            ... )
            >>>
            >>> # 查询多个地区的价格数据
            >>> multi_region_data = panel.query(
            ...     field_values={"region": ["Asia", "Europe"], "indicator": "price"}
            ... )
        """
        logger = logging.getLogger(__name__)

        logger.info(
            f"开始查询面板数据: panel={self.name}, field_values={field_values}, sort_by={sort_by}, parallel={parallel}, columns={columns}"
        )

        # 查找匹配的文件
        all_files = self._find_matching_files(field_values)

        # 如果没有找到文件，返回空DataFrame
        if not all_files:
            logger.warning(
                f"未找到匹配的文件: panel={self.name}, field_values={field_values}"
            )
            return pd.DataFrame()

        # 过滤掉无效文件
        valid_files = all_files

        # 如果没有有效文件，返回空DataFrame
        if not valid_files:
            logger.warning(f"没有有效的文件需要处理: panel={self.name}")
            return pd.DataFrame()

        # 根据parallel参数决定使用并行处理还是串行处理
        if parallel and len(valid_files) > 1:
            # 使用父类的并行处理方法，传入columns参数
            dataframes = self._process_files_parallel(
                valid_files, max_workers, dtypes, None, columns
            )
        else:
            # 使用父类的串行处理方法，传入columns参数
            dataframes = self._process_files_serial(valid_files, dtypes, None, columns)

        # 如果没有读取到任何数据，返回空DataFrame
        if not dataframes:
            logger.warning(f"未能读取到任何有效数据: panel={self.name}")
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

        # 记录DataFrame的属性，便于后续处理
        result.attrs["entity_col_name"] = self.entity_col_name
        result.attrs["index_col"] = self.index_col

        logger.info(f"查询完成: panel={self.name}, 获取{len(result)}行数据")
        return result

    def to_wide_format(self, data: pd.DataFrame, value_col: str = None) -> pd.DataFrame:
        """将长格式数据转换为宽格式（面板格式）

        转换长格式（实体ID在一列中）的数据为宽格式（实体ID作为列名）。
        这种转换对于时间序列分析非常有用，使每个实体数据成为单独的列。

        ### 长格式数据示例 (输入)
        ```
        date       | entity_id    | value
        --------------------------------
        2023-01-01 | entity1      | 1.1
        2023-01-01 | entity2      | 2.1
        2023-01-02 | entity1      | 1.2
        2023-01-02 | entity2      | 2.2
        ```

        ### 宽格式数据示例 (输出)
        ```
        date       | entity1  | entity2
        ----------------------------
        2023-01-01 | 1.1      | 2.1
        2023-01-02 | 1.2      | 2.2
        ```

        ### 转换过程
        1. 识别索引列(通常是日期列)和实体列
        2. 使用pandas.pivot函数进行透视
        3. 重置索引，将日期列从索引变回普通列

        Args:
            data: 长格式的DataFrame
            value_col: 值列名称，即包含数值的列，如果为None则使用默认值列名'value'

        Returns:
            pd.DataFrame: 转换后的宽格式(面板格式)数据

        Raises:
            ValueError: 当必要的列(索引列、实体列或值列)不存在时抛出

        Example:
            >>> # 转换长格式数据为宽格式
            >>> long_data = pd.DataFrame({
            ...     'date': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02'],
            ...     'entity_id': ['entity1', 'entity2', 'entity1', 'entity2'],
            ...     'value': [1.1, 2.1, 1.2, 2.2]
            ... })
            >>> wide_data = panel.to_wide_format(long_data)
        """
        if data.empty:
            return data

        # 确保索引列存在
        if self.index_col not in data.columns:
            raise ValueError(f"索引列 {self.index_col} 不在数据列中")

        # 确保实体列存在
        if self.entity_col_name not in data.columns:
            # 如果已经是宽格式，直接返回
            return data

        # 使用默认值列名或指定的值列名
        value_col = value_col or self.default_value_col

        # 确保值列存在
        if value_col not in data.columns:
            raise ValueError(f"值列 {value_col} 不在数据列中")

        # 转换为宽格式
        wide_data = data.pivot(
            index=self.index_col, columns=self.entity_col_name, values=value_col
        )

        # 重置索引，使日期成为普通列
        wide_data = wide_data.reset_index()

        return wide_data

    def get_all_entities(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> List[str]:
        """获取所有实体ID列表

        获取匹配指定条件的数据中所有实体的ID列表。
        实体列表基于面板数据中的列名，不包括索引列和字段值列。

        ### 实体识别逻辑
        1. 获取匹配field_values的文件表头
        2. 从表头中提取所有非索引列和非字段列
        3. 返回这些列名作为实体ID列表

        Args:
            field_values: 查询条件字段值映射，用于筛选特定数据范围
                如果为None或空，则查询所有数据

        Returns:
            List[str]: 所有实体ID列表
            如果没有匹配数据或数据为空，返回空列表

        Example:
            >>> # 获取特定区域所有股票代码
            >>> stocks = panel.get_all_entities(field_values={"region": "Asia"})
            >>> print(f"亚洲市场的股票数量: {len(stocks)}")
        """
        # 获取表头，而不是查询整个数据集
        headers = self.get_header(field_values)

        if headers is None or len(headers) == 0:
            return []

        # 获取所有非索引列（实体列）
        entity_columns = [col for col in headers if col != self.index_col]

        # 还需要排除可能包含在表头中的字段值列
        if self.meta_info and self.meta_info.structure_fields:
            entity_columns = [
                col
                for col in entity_columns
                if col not in self.meta_info.structure_fields
            ]

        return entity_columns

    def get_entity_data(
        self, entity_id: str, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> pd.Series:
        """获取特定实体的数据序列

        提取特定实体在匹配条件下的完整时间序列数据。
        返回一个pandas.Series对象，索引为日期，值为该实体在各日期的数据。

        ### 数据提取逻辑
        1. 查询匹配field_values的数据
        2. 检查实体ID是否存在于数据的列中
        3. 将日期列设置为索引
        4. 提取实体列的数据作为Series返回

        Args:
            entity_id: 实体标识符（列名），如股票代码"AAPL"
            field_values: 查询条件字段值映射，用于筛选特定数据范围
                如果为None或空，则查询所有数据

        Returns:
            pd.Series: 特定实体的数据序列，索引为日期
            如果实体不存在或没有匹配数据，返回空Series

        Example:
            >>> # 获取特定股票的价格数据
            >>> aapl_prices = panel.get_entity_data(
            ...     entity_id="AAPL",
            ...     field_values={"indicator": "price"}
            ... )
            >>> print(f"AAPL最新价格: {aapl_prices.iloc[-1]}")
        """
        # 查询数据
        data = self.query(field_values)

        if data.empty:
            return pd.Series(name=entity_id)

        # 确保实体列存在
        if entity_id not in data.columns:
            return pd.Series(name=entity_id)

        # 设置索引并返回实体数据
        data = data.set_index(self.index_col)
        series = data[entity_id]
        series.name = entity_id  # 确保返回的Series的名称设置为entity_id
        return series

    def get_date_data(
        self, date: str, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> pd.Series:
        """获取特定日期的横截面数据

        提取特定日期下所有实体的横截面数据。
        返回一个pandas.Series对象，索引为实体ID，值为各实体在该日期的数据。

        ### 数据提取逻辑
        1. 查询匹配field_values的数据
        2. 筛选特定日期的数据行
        3. 从该行提取所有非索引列的数据
        4. 返回包含所有实体值的Series

        Args:
            date: 日期字符串，需与索引列中的日期格式匹配
            field_values: 查询条件字段值映射，用于筛选特定数据范围
                如果为None或空，则查询所有数据

        Returns:
            pd.Series: 特定日期的横截面数据，索引为实体ID
            如果日期不存在或没有匹配数据，返回空Series

        Example:
            >>> # 获取特定日期所有股票的价格数据
            >>> prices_20230103 = panel.get_date_data(
            ...     date="2023-01-03",
            ...     field_values={"indicator": "price"}
            ... )
            >>> print(f"当日最高价股票: {prices_20230103.idxmax()}")
        """
        # 查询数据
        data = self.query(field_values)

        if data.empty:
            return pd.Series(name=date)

        # 确保日期列和日期值存在
        if self.index_col not in data.columns:
            return pd.Series(name=date)

        # 按日期筛选
        date_data = data[data[self.index_col] == date]

        if date_data.empty:
            return pd.Series(name=date)

        # 转换为Series格式，行索引为实体，值为对应的数据
        result = date_data.iloc[0]
        # 排除索引列
        result = result.drop(self.index_col)
        # 确保返回的Series的名称设置为date
        result.name = date

        return result

    def get_panel_stats(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> Dict[str, Any]:
        """获取面板数据统计信息

        计算匹配条件的面板数据的综合统计信息，包括行数、列数、缺失值比例等。
        这对于评估数据质量和分析数据结构很有用。

        ### 统计指标说明
        1. date_count: 日期行数，表示时间序列长度
        2. entity_count: 实体列数，表示横截面宽度
        3. total_cells: 总单元格数(日期数 × 实体数)
        4. non_null_count: 非空单元格数量
        5. null_count: 空单元格数量
        6. null_ratio: 空值比例，空单元格数/总单元格数
        7. first_date: 数据中的第一个日期
        8. last_date: 数据中的最后一个日期
        9. row_count: 数据总行数
        10. date_range: 数据的日期范围，包含(first_date, last_date)

        ### 计算逻辑
        1. 查询匹配field_values的数据
        2. 将日期列设置为索引
        3. 计算各种统计指标
        4. 返回包含所有统计结果的字典

        Args:
            field_values: 查询条件字段值映射，用于筛选特定数据范围
                如果为None或空，则查询所有数据

        Returns:
            Dict[str, Any]: 包含各种统计指标的字典
            如果没有匹配数据，返回包含零值的统计字典

        Example:
            >>> # 获取亚洲市场价格数据的统计信息
            >>> stats = panel.get_panel_stats(
            ...     field_values={"region": "Asia", "indicator": "price"}
            ... )
            >>> print(f"数据完整度: {(1-stats['null_ratio'])*100:.2f}%")
        """
        # 查询数据，数据已经是宽格式
        data = self.query(field_values)

        if data.empty:
            return {
                "date_count": 0,
                "entity_count": 0,
                "total_cells": 0,
                "non_null_count": 0,
                "null_count": 0,
                "null_ratio": 0.0,
                "first_date": None,
                "last_date": None,
                "row_count": 0,
                "date_range": (None, None),
            }

        # 设置索引列为索引
        data = data.set_index(self.index_col)

        # 计算统计信息
        date_count = len(data.index)
        entity_count = len(data.columns)
        total_cells = date_count * entity_count
        non_null_count = data.count().sum()
        null_count = total_cells - non_null_count
        null_ratio = null_count / total_cells if total_cells > 0 else 0.0
        first_date = str(data.index[0]) if date_count > 0 else None
        last_date = str(data.index[-1]) if date_count > 0 else None
        row_count = date_count  # 行数等于日期数
        date_range = (first_date, last_date)  # 日期范围元组

        # 返回统计信息
        return {
            "date_count": date_count,
            "entity_count": entity_count,
            "total_cells": total_cells,
            "non_null_count": non_null_count,
            "null_count": null_count,
            "null_ratio": null_ratio,
            "first_date": first_date,
            "last_date": last_date,
            "row_count": row_count,
            "date_range": date_range,
        }

    def __str__(self) -> str:
        """返回面板数据对象的字符串表示

        Returns:
            str: 面板数据对象的字符串表示
        """
        return f"Panel(name={self.name}, index_col={self.index_col}, entity_col_name={self.entity_col_name}, value_dtype={self.value_dtype})"

    def delete(self, field_values: Dict[str, Union[str, List[str]]] = None) -> bool:
        """删除面板数据

        根据提供的字段值删除匹配的面板数据文件或目录。

        ### 删除逻辑说明
        1. 精确删除：提供完整的字段值映射时，只删除匹配的特定文件
        2. 批量删除：提供部分字段值时，删除所有匹配的文件和其所在目录
           - 例如structure_fields=['region', 'indicator']时：
           - field_values={'region': 'Asia'} 会删除Asia目录及其下所有文件
           - field_values={'indicator': 'price'} 会删除所有区域下的price.csv文件
        3. 完全删除：不提供field_values或提供空字典时，删除整个面板数据目录和元数据文件

        ### 递归删除行为
        1. 删除文件后，如果其父目录变为空目录，会自动删除该空目录
        2. 递归向上检查并删除空目录，直到面板根目录
        3. 当删除整个面板数据时，会同时删除元数据文件

        ### 异常处理
        当文件无法删除时（如文件被占用），会记录错误但不中断操作，继续删除其他匹配文件

        Args:
            field_values: 字段名到字段值的映射，用于定位要删除的文件或目录
                可提供具体值或值列表，如{'region': 'Asia'}或{'region': ['Asia', 'Europe']}
                如果为None或空字典，则删除整个面板数据和元数据

        Returns:
            bool: 删除操作是否成功完成

        Example:
            >>> # 删除特定指标的数据
            >>> panel.delete(field_values={"indicator": "price"})
            >>>
            >>> # 删除特定区域的所有数据
            >>> panel.delete(field_values={"region": "Asia"})
            >>>
            >>> # 删除整个面板数据及元数据
            >>> panel.delete()
        """
        # 调用父类的delete方法，该方法已实现完整的删除逻辑
        return super().delete(field_values)

    def exists(self, field_values: Dict[str, Union[str, List[str]]] = None) -> bool:
        """检查指定字段值的面板数据是否存在

        验证给定字段值组合的面板数据文件是否存在。

        ### 存在性检查逻辑
        1. 精确检查：提供完整field_values时，检查特定文件是否存在
           例如field_values={'region': 'Asia', 'indicator': 'price'}检查Asia区域的价格数据文件

        2. 批量检查：提供部分field_values时，检查是否存在任何匹配的文件
           例如field_values={'region': 'Asia'}检查是否存在任何Asia区域的数据文件

        3. 整体检查：不提供field_values或提供空字典时，检查面板数据目录是否存在

        ### 文件匹配规则
        - 生成文件路径时会根据structure_fields的顺序构建匹配模式
        - 对于部分field_values，使用通配符匹配缺失部分
        - 支持单值或值列表的field_values，如{'region': 'Asia'}或{'region': ['Asia', 'Europe']}

        Args:
            field_values: 字段名到字段值的映射，用于定位要检查的文件
                如果为None或空字典，则检查整个面板数据目录是否存在

        Returns:
            bool: 指定的数据是否存在

        Example:
            >>> # 检查特定区域和指标的数据是否存在
            >>> panel.exists(field_values={"region": "Asia", "indicator": "price"})
            >>>
            >>> # 检查特定区域的任何数据是否存在
            >>> panel.exists(field_values={"region": "Asia"})
            >>>
            >>> # 检查多个区域的数据是否存在
            >>> panel.exists(field_values={"region": ["Asia", "Europe"]})
        """
        # 调用父类的exists方法
        return super().exists(field_values)

    def read_last_line(
        self,
        field_values: Optional[Dict[str, str]] = None,
        dtypes: Dict[str, str] = None,
    ) -> Optional[pd.DataFrame]:
        """读取指定面板文件的最后一行数据

        根据字段值确定面板数据文件，并读取该文件的最后一行。这对于智能更新模式下检查最新记录特别有用。
        与Dataset类的read_last_line不同，Panel类需要处理面板特有的宽格式数据结构（日期为行，实体为列）。

        Args:
            field_values: 字段名到字段值的映射，用于定位具体文件。如果是单层结构面板，可以为None
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用meta_info中的dtypes

        Returns:
            包含最后一行数据的DataFrame，如果文件不存在或为空则返回None
            返回的是宽格式数据，其中一行包含了某个日期下所有实体的数据

        Raises:
            ValueError: 当field_values不足以确定唯一文件，或文件格式不支持时抛出
            FileNotFoundError: 当指定的文件不存在时抛出
        """
        # 日志记录
        logger = getattr(self, "logger", logging.getLogger(__name__))
        logger.info(
            f"开始读取面板文件最后一行: panel={self.name}, field_values={field_values}"
        )

        if field_values is None:
            field_values = {}

        # 获取文件路径
        try:
            file_path, file_ext = self._get_file_path(field_values)
        except Exception as e:
            error_msg = f"构建面板文件路径失败: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"面板文件不存在: {file_path}")
            raise FileNotFoundError(f"面板文件不存在: {file_path}")

        try:
            # 如果未提供dtypes，使用_build_complete_dtypes_from_file方法构建数据类型字典
            if dtypes is None:
                dtypes = self._build_complete_dtypes_from_file(file_path)

            # 根据文件格式读取最后一行
            if file_ext == "csv":
                # 使用CSVOperator读取CSV文件的最后一行
                csv_operator = CSVOperator(dtypes)
                last_line_df = csv_operator.read_last_line(file_path)

                if last_line_df is not None and not last_line_df.empty:
                    # 使用layers从文件路径中提取字段值并添加到DataFrame中
                    extracted_fields = self.layers.extract_field_values(
                        file_path, self.folder, self.name
                    )

                    # 将提取的字段值添加到DataFrame中
                    for field, value in extracted_fields.items():
                        # 如果DataFrame中已经有同名列，跳过添加
                        if field not in last_line_df.columns:
                            last_line_df[field] = value

                    logger.info(f"成功读取面板文件最后一行: {file_path}")
                    return last_line_df
                else:
                    logger.info(f"面板文件为空或只有表头: {file_path}")
                    return last_line_df
            else:
                logger.error(f"不支持的文件格式: {file_ext}")
                raise ValueError(f"不支持的文件格式: {file_ext}")

        except Exception as e:
            # 捕获并处理读取过程中的异常
            if isinstance(e, FileNotFoundError):
                raise e
            else:
                error_msg = f"读取面板文件最后一行失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def read_last_n_lines(
        self,
        n: int,
        field_values: Optional[Dict[str, str]] = None,
        dtypes: Dict[str, str] = None,
    ) -> Optional[pd.DataFrame]:
        """读取指定面板文件的最后n行数据

        根据字段值确定面板数据文件，并读取该文件的最后n行。这对于数据分析和智能更新模式特别有用。
        与Dataset类的read_last_n_lines不同，Panel类需要处理面板特有的宽格式数据结构（日期为行，实体为列）。

        Args:
            n: 需要读取的行数
            field_values: 字段名到字段值的映射，用于定位具体文件。如果是单层结构面板，可以为None
            dtypes: 数据类型字典，指定各列的数据类型，如果为None则使用meta_info中的dtypes

        Returns:
            包含最后n行数据的DataFrame，如果文件为空返回None，
            如果文件只有表头则返回一个只有表头的空DataFrame
            返回的是宽格式数据，其中每行代表一个日期下所有实体的数据

        Raises:
            ValueError: 当n不是正整数、field_values不足以确定唯一文件，或文件格式不支持时抛出
            FileNotFoundError: 当指定的文件不存在时抛出
        """
        # 日志记录
        logger = getattr(self, "logger", logging.getLogger(__name__))
        logger.info(
            f"开始读取面板文件最后{n}行: panel={self.name}, field_values={field_values}"
        )

        if n <= 0:
            error_msg = "n必须是正整数"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if field_values is None:
            field_values = {}

        # 获取文件路径
        try:
            file_path, file_ext = self._get_file_path(field_values)
        except Exception as e:
            error_msg = f"构建面板文件路径失败: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"面板文件不存在: {file_path}")
            raise FileNotFoundError(f"面板文件不存在: {file_path}")

        try:
            # 如果未提供dtypes，使用_build_complete_dtypes_from_file方法构建数据类型字典
            if dtypes is None:
                dtypes = self._build_complete_dtypes_from_file(file_path)

            # 根据文件格式读取最后n行
            if file_ext == "csv":
                # 使用CSVOperator读取CSV文件的最后n行
                csv_operator = CSVOperator(dtypes)
                last_n_lines_df = csv_operator.read_last_n_lines(file_path, n)

                if last_n_lines_df is not None and not last_n_lines_df.empty:
                    # 使用layers从文件路径中提取字段值并添加到DataFrame中
                    extracted_fields = self.layers.extract_field_values(
                        file_path, self.folder, self.name
                    )

                    # 将提取的字段值添加到DataFrame中
                    for field, value in extracted_fields.items():
                        # 如果DataFrame中已经有同名列，跳过添加
                        if field not in last_n_lines_df.columns:
                            last_n_lines_df[field] = value

                    # 如果索引列在数据列中，将其设置为索引
                    if self.index_col in last_n_lines_df.columns:
                        # 确保索引列类型适合作为索引（如果是日期，确保格式正确）
                        try:
                            if self.meta_info.dtypes.get(self.index_col) in [
                                "datetime",
                                "datetime64",
                                "date",
                            ]:
                                last_n_lines_df[self.index_col] = pd.to_datetime(
                                    last_n_lines_df[self.index_col]
                                )
                        except Exception as e:
                            logger.warning(
                                f"转换索引列 {self.index_col} 到日期类型时出错: {str(e)}"
                            )

                    logger.info(f"成功读取面板文件最后{n}行: {file_path}")
                    return last_n_lines_df
                else:
                    logger.info(f"面板文件为空或只有表头: {file_path}")
                    return last_n_lines_df
            else:
                logger.error(f"不支持的文件格式: {file_ext}")
                raise ValueError(f"不支持的文件格式: {file_ext}")

        except Exception as e:
            # 捕获并处理读取过程中的异常
            if isinstance(e, FileNotFoundError):
                raise e
            elif isinstance(e, ValueError) and "n必须是正整数" in str(e):
                raise e
            else:
                error_msg = f"读取面板文件最后{n}行失败: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def get_header(
        self, field_values: Dict[str, Union[str, List[str]]] = None
    ) -> Optional[List[str]]:
        """获取指定面板文件的表头（列名）

        根据字段值确定面板数据文件，并读取该文件的表头。

        Args:
            field_values: 字段值映射，用于定位具体文件。如果是单层结构面板，可以为None

        Returns:
            Optional[List[str]]: 文件表头列名列表，如果文件不存在或为空则返回None

        Raises:
            ValueError: 当field_values不足以确定唯一文件，或文件格式不支持时抛出
            FileNotFoundError: 当指定的文件不存在时抛出
        """
        # 调用父类的同名方法
        return super().get_header(field_values)
