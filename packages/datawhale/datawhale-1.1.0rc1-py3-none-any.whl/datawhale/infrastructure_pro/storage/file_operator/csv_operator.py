#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV文件读取器

提供CSV文件的读取、查询和保存功能。
"""

import os
import pandas as pd
import numpy as np
import logging
from io import StringIO
from typing import Dict, List, Optional, Union, Any

# 配置日志
logger = logging.getLogger(__name__)


class CSVOperator:
    """
    CSV文件读取器

    提供对CSV文件的读取、查询和保存功能。

    Attributes:
        dtypes: 列数据类型字典，指定CSV文件中各列的数据类型
    """

    def __init__(self, dtypes: Dict[str, str]):
        """
        初始化CSV读取器

        Args:
            dtypes: 列数据类型字典，键为列名，值为数据类型（如'string', 'float64', 'int64'等）
        """
        self.dtypes = dtypes

    def _create_empty_dataframe_with_header(
        self, header: str, file_path: str
    ) -> pd.DataFrame:
        """
        创建一个只有表头的空DataFrame

        Args:
            header: CSV文件的表头行
            file_path: CSV文件路径，用于日志

        Returns:
            包含表头但没有数据的DataFrame
        """
        # 创建一个空的DataFrame，但包含正确的列名
        empty_df = pd.DataFrame(columns=header.split(","))

        # 应用数据类型转换
        for col in empty_df.columns:
            if col in self.dtypes:
                dtype = self.dtypes[col]
                try:
                    if dtype == "float64" or dtype == "float":
                        empty_df[col] = empty_df[col].astype("float64")
                    elif dtype == "int64" or dtype == "int":
                        empty_df[col] = empty_df[col].astype("int64")
                    elif dtype == "string" or dtype == "str":
                        empty_df[col] = empty_df[col].astype("string")
                except Exception as e:
                    logger.warning(f"转换列 {col} 到类型 {dtype} 时出错: {str(e)}")

        logger.info(f"文件只有表头，返回空DataFrame: {file_path}")
        return empty_df

    def read_header(self, file_path: str) -> Optional[List[str]]:
        """
        读取CSV文件的表头（列名）

        Args:
            file_path: CSV文件的绝对路径

        Returns:
            表头列名列表，如果文件为空或不存在则返回None

        Raises:
            FileNotFoundError: 文件不存在时抛出
            Exception: 读取过程中发生错误时抛出
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                header_line = f.readline().strip()
                if not header_line:
                    # 文件为空
                    logger.warning(f"文件为空，没有表头: {file_path}")
                    return None

                # 返回列名列表
                header_columns = header_line.split(",")
                logger.info(f"成功读取文件表头，共{len(header_columns)}列: {file_path}")
                return header_columns
        except FileNotFoundError:
            # 直接向上传递文件不存在异常
            raise
        except Exception as e:
            error_msg = f"读取文件表头失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def query(self, file_path: str, fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        查询CSV文件数据

        Args:
            file_path: CSV文件的绝对路径
            fields: 需要选择的字段列表，默认为None表示选择所有字段

        Returns:
            包含查询结果的DataFrame

        Raises:
            FileNotFoundError: 文件不存在时抛出
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 首先读取CSV文件的表头，确定文件中有哪些列
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                header_line = f.readline().strip()
                if not header_line:
                    # 文件为空，返回空DataFrame
                    return pd.DataFrame()

                # 获取文件中实际存在的列
                file_columns = header_line.split(",")
        except Exception as e:
            logger.error(f"读取文件表头失败: {str(e)}")
            raise ValueError(f"读取文件表头失败: {str(e)}")

        # 如果未指定字段，则使用所有在dtypes中定义的字段
        if fields is None:
            fields = list(self.dtypes.keys())

        # 过滤掉文件中不存在的列，同时检查字段是否在dtypes中定义
        valid_fields = []
        for field in fields:
            if field not in self.dtypes:
                raise ValueError(f"字段 '{field}' 不在dtypes定义中")
            if field in file_columns:
                valid_fields.append(field)
            else:
                logger.warning(
                    f"字段 '{field}' 在dtypes中定义但在文件 {file_path} 中不存在，将被忽略"
                )

        # 如果没有有效字段，返回空DataFrame
        if not valid_fields:
            logger.warning(f"没有有效的字段可以读取，返回空DataFrame")
            return pd.DataFrame(columns=fields)

        # 只读取需要的且在文件中存在的列以提高效率
        usecols = valid_fields
        dtype_dict = {field: self.dtypes[field] for field in valid_fields}

        # 读取文件
        df = pd.read_csv(file_path, usecols=usecols, dtype=dtype_dict)

        # 如果原始fields中有文件不存在的列，为这些列添加空值列
        missing_fields = [field for field in fields if field not in valid_fields]
        for field in missing_fields:
            # 根据dtypes中的类型创建适当类型的空列
            dtype = self.dtypes[field]
            if dtype in ["float64", "float"]:
                df[field] = np.nan
            elif dtype in ["int64", "int"]:
                df[field] = np.nan
            else:
                df[field] = None

        return df

    def read_last_line(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        读取CSV文件的最后一行

        使用块读取策略高效获取文件最后一行，适用于大文件

        Args:
            file_path: CSV文件的绝对路径

        Returns:
            包含最后一行数据的DataFrame，如果文件为空返回None，
            如果文件只有表头则返回一个只有表头的空DataFrame

        Raises:
            FileNotFoundError: 文件不存在时抛出
            Exception: 读取过程中发生错误时抛出
        """
        try:
            # 直接调用read_last_n_lines方法获取最后一行
            result = self.read_last_n_lines(file_path, 1)
            # 记录成功日志（如果read_last_n_lines返回结果，它会记录自己的日志）
            if result is not None and not result.empty:
                logger.info(f"成功读取文件最后一行：{file_path}")
            elif result is not None and result.empty:
                logger.info(f"文件只有表头，返回空DataFrame：{file_path}")
            return result
        except FileNotFoundError:
            # 直接向上传递文件不存在异常
            raise
        except Exception as e:
            error_msg = f"读取文件最后一行失败：{str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def read_last_n_lines(self, file_path: str, n: int) -> Optional[pd.DataFrame]:
        """
        读取CSV文件的最后n行

        使用块读取策略高效获取文件最后n行，适用于大文件

        Args:
            file_path: CSV文件的绝对路径
            n: 需要读取的行数

        Returns:
            包含最后n行数据的DataFrame，如果文件为空或不存在返回None

        Raises:
            FileNotFoundError: 文件不存在时抛出
            ValueError: n不是正整数时抛出
            Exception: 读取过程中发生错误时抛出
        """
        if n <= 0:
            raise ValueError("n必须是正整数")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            # 首先尝试读取文件头部获取列名
            with open(file_path, "r", encoding="utf-8") as f:
                # 读取第一行（表头）
                header = f.readline().strip()
                if not header:  # 文件为空
                    logger.warning(f"文件为空，无表头: {file_path}")
                    return None

                # 定位到文件末尾
                f.seek(0, 2)
                file_size = f.tell()

                if file_size <= len(header) + 1:  # 只有表头
                    return self._create_empty_dataframe_with_header(header, file_path)

                # 设置初始块大小，至少4KB或根据n进行调整
                initial_block_size = max(4096, n * 200)  # 增加每行假设字节数
                block_size = initial_block_size

                # 读取足够的数据以包含至少n行
                lines = []
                current_pos = file_size

                while (
                    len(lines) <= n + 1 and current_pos > len(header) + 2
                ):  # +1是为了考虑可能的空行，+2是为了确保我们读取足够的数据
                    # 增加块大小，每次翻倍，但不超过文件大小
                    read_size = min(block_size, current_pos)
                    current_pos = current_pos - read_size

                    # 读取数据块
                    f.seek(current_pos)
                    block = f.read(read_size)

                    # 拆分为行并添加到lines列表的开头
                    block_lines = block.split("\n")

                    # 处理块边界的行连接问题
                    if lines and block_lines[-1] != "":
                        # 如果当前块的最后一行是不完整的，需要与下一块的第一行连接
                        lines[0] = block_lines[-1] + lines[0]
                        block_lines = block_lines[:-1]

                    # 将其余完整行添加到列表前面
                    if block_lines:
                        lines = block_lines + lines

                    # 如果已经到达文件开头，跳出循环
                    if current_pos <= len(header) + 2:
                        break

                    # 动态增加块大小，以更快地读取大文件
                    block_size *= 2

                # 移除表头（如果读取到了）和可能的空行
                if current_pos <= len(header) + 2:
                    # 如果我们从文件开头读取，需要跳过表头
                    lines = [line for line in lines[1:] if line.strip()]
                else:
                    # 否则只过滤空行
                    lines = [line for line in lines if line.strip()]

                # 如果文件行数小于n，则使用所有行；否则只取最后n行
                if len(lines) <= n:
                    last_n_lines = lines
                else:
                    last_n_lines = lines[-n:]

                if not last_n_lines:
                    return None

                # 列名
                columns = header.split(",")

                # 处理每一行，考虑CSV中可能存在的引号内逗号
                rows_data = []
                for line in last_n_lines:
                    if not line.strip():
                        continue

                    # 尝试使用pandas直接解析该行，但不进行自动类型转换
                    try:
                        # 使用dtype=str确保所有列数据被当作字符串读取，避免自动类型转换
                        parsed_line = pd.read_csv(
                            StringIO(line), header=None, dtype=str
                        )
                        if not parsed_line.empty:
                            data = parsed_line.iloc[0].tolist()

                            # 如果解析后的列数与预期不符，尝试简单的逗号分割
                            if len(data) != len(columns):
                                data = line.split(",")
                    except Exception:
                        # 如果pandas解析失败，尝试简单的逗号分割
                        data = line.split(",")

                    # 如果列数仍不匹配，则跳过该行
                    if len(data) != len(columns):
                        logger.warning(f"行数据与列数不匹配，跳过此行: {line}")
                        continue

                    rows_data.append(data)

                if not rows_data:
                    return None

                # 创建DataFrame，先把所有列都当作字符串
                df = pd.DataFrame(rows_data, columns=columns)

                # 应用数据类型转换，但仅对dtypes中指定为数值类型的列进行转换
                for col in df.columns:
                    if col in self.dtypes:
                        dtype = self.dtypes[col]
                        try:
                            if dtype == "float64" or dtype == "float":
                                df[col] = pd.to_numeric(
                                    df[col], errors="coerce"
                                ).astype("float64")
                            elif dtype == "int64" or dtype == "int":
                                df[col] = pd.to_numeric(
                                    df[col], errors="coerce"
                                ).astype("int64")
                            elif dtype == "string" or dtype == "str":
                                # 确保字符串类型的列保持原样，不进行数值转换
                                df[col] = df[col].astype("string")
                        except Exception as e:
                            logger.warning(
                                f"转换列 {col} 到类型 {dtype} 时出错: {str(e)}"
                            )
                            # 如果转换失败，保持原始字符串格式
                            df[col] = df[col].astype("string")

                logger.info(f"成功读取文件最后 {len(df)} 行: {file_path}")
                return df

        except Exception as e:
            error_msg = f"读取文件最后 {n} 行失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def save(
        self,
        file_path: str,
        data: pd.DataFrame,
        mode: str = "overwrite",
        update_key: Optional[str] = None,
    ) -> None:
        """
        保存数据到CSV文件

        Args:
            file_path: CSV文件的绝对路径
            data: 要保存的DataFrame数据
            mode: 保存模式，'overwrite'表示覆盖，'append'表示追加，'update'表示智能更新，默认为'overwrite'
            update_key: 当mode为'update'时，用于比较的列名，只有该列值大于文件最后一行对应值的数据才会被追加

        Raises:
            ValueError: mode参数不正确或update模式下未指定update_key时抛出
        """
        if mode not in ["overwrite", "append", "update"]:
            raise ValueError("mode参数必须为'overwrite'、'append'或'update'")

        # 'update'模式下必须提供update_key
        if mode == "update" and update_key is None:
            raise ValueError("在'update'模式下必须提供update_key参数")

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 检查数据列是否与dtypes一致
        for column in data.columns:
            if column not in self.dtypes:
                raise ValueError(f"数据列 '{column}' 不在dtypes定义中")

        # 根据mode决定写入方式
        if mode == "overwrite":
            data.to_csv(file_path, index=False)
        elif mode == "append":
            # 如果文件不存在，则创建新文件
            if not os.path.exists(file_path):
                data.to_csv(file_path, index=False)
            else:
                # 读取现有文件的第一行（表头）
                with open(file_path, "r", encoding="utf-8") as f:
                    header = f.readline().strip()
                    if not header:  # 文件为空
                        data.to_csv(file_path, index=False)
                        return

                    # 检查列名是否匹配
                    existing_columns = header.split(",")
                    if existing_columns != list(data.columns):
                        raise ValueError(
                            f"新数据的列与现有文件不匹配。现有列：{existing_columns}，新数据列：{list(data.columns)}"
                        )

                # 追加到现有文件
                data.to_csv(file_path, mode="a", header=False, index=False)
        else:  # mode == 'update'
            # 如果文件不存在，则创建新文件
            if not os.path.exists(file_path):
                data.to_csv(file_path, index=False)
                logger.info(f"文件不存在，创建新文件: {file_path}")
                return

            # 检查update_key是否在数据列中
            if update_key not in data.columns:
                raise ValueError(f"更新键 '{update_key}' 不在数据列中")

            # 首先检查表头列名是否匹配
            with open(file_path, "r", encoding="utf-8") as f:
                header = f.readline().strip()
                if header:  # 如果文件有表头
                    existing_columns = header.split(",")
                    if existing_columns != list(data.columns):
                        raise ValueError(
                            f"新数据的列与现有文件不匹配。现有列：{existing_columns}，新数据列：{list(data.columns)}"
                        )

            try:
                # 读取文件最后一行
                last_row = self.read_last_line(file_path)

                if last_row is None or last_row.empty:
                    # 文件为空或只有表头，已经检查了列名匹配，直接写入所有数据
                    data.to_csv(file_path, mode="a", header=False, index=False)
                    logger.info(f"文件为空或只有表头，写入所有数据: {file_path}")
                    return

                # 检查update_key是否在文件的列中
                if update_key not in last_row.columns:
                    raise ValueError(f"更新键 '{update_key}' 不在目标文件的列中")

                # 获取最后一行的update_key值
                last_value = last_row[update_key].iloc[0]

                # 筛选出update_key值大于last_value的行
                new_data = data[data[update_key] > last_value].copy()

                if len(new_data) > 0:
                    # 追加新数据到文件
                    new_data.to_csv(file_path, mode="a", header=False, index=False)
                    logger.info(f"更新了{len(new_data)}行数据到文件: {file_path}")
                else:
                    logger.info(f"没有需要更新的数据: {file_path}")

            except Exception as e:
                error_msg = f"更新数据到文件失败: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
