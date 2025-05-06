#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DataWhale 存储接口模块

为存储服务提供简洁易用的用户接口，支持Dataset多层数据集管理。

主要功能:
- 创建数据集
- 保存数据到数据集
- 从数据集查询数据
- 删除数据集或数据集中的文件
- 检查数据集中的数据是否存在

提供两种接口:
1. 基础接口: 直接操作Dataset对象(create_dataset, save, query, delete, exists)
2. DataWhale本地存储接口: 使用StorageService进行操作(dw_create_dataset, dw_save, dw_query, dw_delete, dw_exists)
"""

from typing import Dict, Optional, List, Any, Union
import pandas as pd
import os

# 模块内的导入使用相对导入
from .dataset import Dataset
from .storage_service import StorageService
from .panel import Panel
from .panel_storage_service import PanelStorageService
import logging
import glob

# 创建全局变量，但不立即初始化
_storage_service_instance = None
_panel_storage_service_instance = None


def _get_storage_service():
    """获取StorageService单例实例

    使用懒加载方式，只有在首次调用时才会创建实例

    Returns:
        StorageService: 存储服务实例
    """
    global _storage_service_instance
    if _storage_service_instance is None:
        # 首次调用时初始化
        _storage_service_instance = StorageService()
        logging.debug("StorageService实例已按需初始化")
    return _storage_service_instance


def _get_panel_storage_service():
    """获取PanelStorageService单例实例

    使用懒加载方式，只有在首次调用时才会创建实例

    Returns:
        PanelStorageService: 面板存储服务实例
    """
    global _panel_storage_service_instance
    if _panel_storage_service_instance is None:
        # 首次调用时初始化
        _panel_storage_service_instance = PanelStorageService()
        logging.debug("PanelStorageService实例已按需初始化")
    return _panel_storage_service_instance


def create_dataset(
    name: str,
    format: str = "csv",
    structure_fields: List[str] = None,
    update_mode: str = "append",
    dtypes: Dict = None,
    data_folder: str = None,
    meta_folder: str = None,
) -> Optional[Dataset]:
    """
    创建多层数据集

    Args:
        name: 数据集名称
        format: 文件格式，默认为"csv"
        structure_fields: 用于生成动态层的字段列表，决定文件层级结构(层级数=字段数+1)
        update_mode: 更新模式，可选值："append"（追加）、"overwrite"（覆盖）或"update"（智能更新），默认为"append"
        dtypes: 数据类型映射字典
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Optional[Dataset]: 创建的数据集对象，如果创建失败则返回None

    Examples:
        >>> dataset = create_dataset(
        ...     name="stocks_daily",
        ...     format="csv",
        ...     structure_fields=["code", "trade_date"],
        ...     update_mode="append",
        ...     dtypes={
        ...         "code": "object",
        ...         "trade_date": "object",
        ...         "open": "float64",
        ...         "close": "float64",
        ...         "volume": "float64"
        ...     },
        ...     data_folder="/path/to/data",
        ...     meta_folder="/path/to/meta"
        ... )
    """
    # 验证路径参数
    if data_folder is None or meta_folder is None:
        raise ValueError("必须提供data_folder和meta_folder的绝对路径")

    try:
        # 构建元信息字典
        meta_info = {
            "name": name,
            "format": format,
            "update_mode": update_mode,
            "dtypes": dtypes or {},
        }

        # 如果有结构字段，添加dataset部分
        if structure_fields:
            meta_info["dataset"] = {"structure_fields": structure_fields}

        # 创建数据集
        dataset = Dataset.create_dataset(
            folder=data_folder, meta_folder=meta_folder, meta_info=meta_info
        )

        return dataset
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"创建数据集失败: {str(e)}")
        return None


def save(
    data: pd.DataFrame,
    dataset_name: str,
    field_values: Dict[str, str] = None,
    mode: str = None,
    update_key: str = None,
    data_folder: str = None,
    meta_folder: str = None,
    **kwargs,
) -> bool:
    """
    保存数据到多层数据集

    Args:
        data: 要保存的DataFrame数据
        dataset_name: 数据集名称
        field_values: 字段值映射，用于指定动态层的值
        mode: 保存模式，可选值："overwrite"（覆盖）、"append"（追加）或"update"（智能更新）
              如果为None，则使用数据集默认的更新模式
        update_key: 当mode为'update'时，用于比较的列名，只有该列值大于文件最后一行对应值的数据才会被追加
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供
        **kwargs: 额外参数

    Returns:
        bool: 保存是否成功

    Examples:
        >>> df = pd.DataFrame({
        ...     'code': ['000001'],
        ...     'trade_date': ['2023-01-01'],
        ...     'open': [10.1],
        ...     'close': [10.2],
        ...     'volume': [1000]
        ... })
        >>> save(df, "stocks_daily", field_values={'code': '000001', 'trade_date': '2023-01-01'},
        ...      data_folder="/path/to/data", meta_folder="/path/to/meta")

        # 使用智能更新模式（只追加更新键值大于已有数据的记录）
        >>> save(df, "stocks_daily", field_values={'code': '000001'}, mode="update",
        ...      update_key="trade_date", data_folder="/path/to/data", meta_folder="/path/to/meta")
    """
    try:
        # 验证路径参数
        if data_folder is None or meta_folder is None:
            raise ValueError("必须提供data_folder和meta_folder的绝对路径")

        # 加载数据集
        dataset = Dataset.load_dataset(
            name=dataset_name, folder=data_folder, meta_folder=meta_folder
        )

        # 保存数据
        dataset.save(data, field_values, mode, update_key)
        return True
    except Exception as e:
        print(f"保存数据失败: {str(e)}")
        return False


def query(
    dataset_name: str,
    field_values: Dict[str, Union[str, List[str]]] = None,
    sort_by: str = None,
    parallel: bool = True,
    data_folder: str = None,
    meta_folder: str = None,
    columns: List[str] = None,
    **kwargs,
) -> Optional[pd.DataFrame]:
    """
    从多层数据集查询数据

    Args:
        dataset_name: 数据集名称
        field_values: 字段值映射，用于指定要查询的数据路径
        sort_by: 排序字段
        parallel: 是否使用并行查询，默认为True
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供
        columns: 需要选择的列名列表，默认为None表示选择所有列
        **kwargs: 额外参数

    Returns:
        Optional[pd.DataFrame]: 查询结果，如果查询失败则返回None

    Examples:
        >>> df = query("stocks_daily", field_values={'code': '000001'},
        ...            data_folder="/path/to/data", meta_folder="/path/to/meta")
        >>> df = query("stocks_daily", field_values={'code': ['000001', '000002']},
        ...            data_folder="/path/to/data", meta_folder="/path/to/meta")
    """
    # 验证路径参数
    if data_folder is None or meta_folder is None:
        raise ValueError("必须提供data_folder和meta_folder的绝对路径")

    try:
        # 加载数据集
        dataset = Dataset.load_dataset(
            name=dataset_name, folder=data_folder, meta_folder=meta_folder
        )

        # 查询数据
        return dataset.query(field_values, sort_by, parallel, columns=columns, **kwargs)
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"查询数据失败: {str(e)}")
        return None


def delete(
    dataset_name: str,
    field_values: Dict[str, str] = None,
    data_folder: str = None,
    meta_folder: str = None,
) -> bool:
    """
    从多层数据集删除数据

    Args:
        dataset_name: 数据集名称
        field_values: 字段值映射，用于指定要删除的数据路径
                     如果为None，则删除整个数据集
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        bool: 删除是否成功

    Examples:
        >>> delete("stocks_daily", field_values={'code': '000001', 'trade_date': '2023-01-01'},
        ...        data_folder="/path/to/data", meta_folder="/path/to/meta")
        >>> delete("stocks_daily", data_folder="/path/to/data", meta_folder="/path/to/meta")  # 删除整个数据集
    """
    try:
        # 验证路径参数
        if data_folder is None or meta_folder is None:
            raise ValueError("必须提供data_folder和meta_folder的绝对路径")

        # 加载数据集
        dataset = Dataset.load_dataset(
            name=dataset_name, folder=data_folder, meta_folder=meta_folder
        )

        # 删除数据
        return dataset.delete(field_values)
    except Exception as e:
        print(f"删除数据失败: {str(e)}")
        return False


def exists(
    dataset_name: str,
    field_values: Dict[str, str] = None,
    data_folder: str = None,
    meta_folder: str = None,
) -> bool:
    """
    检查多层数据集或其中的数据是否存在

    Args:
        dataset_name: 数据集名称
        field_values: 字段值映射，用于指定要检查的数据路径
                     如果为None，则只检查数据集是否存在
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        bool: 数据集或指定数据是否存在

    Examples:
        >>> exists("stocks_daily", data_folder="/path/to/data", meta_folder="/path/to/meta")
        >>> exists("stocks_daily", field_values={'code': '000001', 'trade_date': '2023-01-01'},
        ...        data_folder="/path/to/data", meta_folder="/path/to/meta")
    """
    # 验证路径参数
    if data_folder is None or meta_folder is None:
        raise ValueError("必须提供data_folder和meta_folder的绝对路径")

    try:
        try:
            # 尝试加载数据集
            dataset = Dataset.load_dataset(
                name=dataset_name, folder=data_folder, meta_folder=meta_folder
            )

            # 如果只需检查数据集是否存在，直接返回True
            if field_values is None:
                return True

            # 检查指定数据是否存在
            return dataset.exists(field_values)
        except Exception:
            # 数据集加载失败，表示数据集不存在
            return False
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception:
        return False


# ============ DataWhale本地存储接口 ============


def dw_create_dataset(
    name: str,
    dtypes: Dict,
    format: str = None,
    structure_fields: List[str] = None,
    update_mode: str = None,
) -> Dataset:
    """
    创建DataWhale本地数据集(使用配置的存储路径)

    Args:
        name: 数据集名称
        dtypes: 数据类型配置，必须提供
        format: 文件格式，默认使用配置中的default_format
        structure_fields: 文件结构字段列表，决定文件层级结构(层级数=字段数+1)
        update_mode: 更新模式，可选值："append"（追加）、"overwrite"（覆盖）或"update"（智能更新），默认为"append"

    Returns:
        Dataset: 创建的数据集对象

    Examples:
        >>> dataset = dw_create_dataset(
        ...     name="stocks_daily",
        ...     dtypes={
        ...         "code": "object",
        ...         "trade_date": "object",
        ...         "open": "float64",
        ...         "close": "float64",
        ...         "volume": "float64"
        ...     },
        ...     structure_fields=["code", "trade_date"],
        ...     update_mode="append"
        ... )
    """
    return _get_storage_service().create_dataset(
        name=name,
        dtypes=dtypes,
        format=format,
        structure_fields=structure_fields,
        update_mode=update_mode,
    )


def dw_save(
    data: pd.DataFrame,
    data_name: str,
    field_values: Dict[str, str] = None,
    mode: str = None,
    update_key: str = None,
    **kwargs,
) -> bool:
    """
    保存数据到DataWhale本地数据集

    Args:
        data: 要保存的DataFrame数据
        data_name: 数据集名称
        field_values: 字段值映射，用于指定动态层的值
        mode: 保存模式，可选值："overwrite"（覆盖）、"append"（追加）或"update"（智能更新）
             如果为None，则使用数据集默认的更新模式
        update_key: 当mode为'update'时，用于比较的列名，只有该列值大于文件最后一行对应值的数据才会被追加
        **kwargs: 额外参数

    Returns:
        bool: 保存是否成功

    Examples:
        >>> df = pd.DataFrame({
        ...     'code': ['000001'],
        ...     'trade_date': ['2023-01-01'],
        ...     'open': [10.1],
        ...     'close': [10.2],
        ...     'volume': [1000]
        ... })
        >>> dw_save(df, "stocks_daily", field_values={'code': '000001', 'trade_date': '2023-01-01'})

        # 使用智能更新模式（只追加更新键值大于已有数据的记录）
        >>> dw_save(df, "stocks_daily", field_values={'code': '000001'}, mode="update", update_key="trade_date")
    """
    # 检查update_key和mode之间的关系
    if mode == "update" and update_key is None:
        raise ValueError("当mode为'update'时，必须提供update_key参数")

    # 如果提供了update_key，自动将mode设置为"update"
    if update_key is not None and mode is None:
        mode = "update"

    # 准备传递给storage_service.save的参数
    save_args = {
        "data": data,
        "data_name": data_name,
        "field_values": field_values,
    }

    # 只有当mode不为None时才添加mode参数
    if mode is not None:
        save_args["mode"] = mode

    # 只有当update_key不为None时才添加update_key参数
    if update_key is not None:
        save_args["update_key"] = update_key

    # 加入其他额外参数
    save_args.update(kwargs)

    # 调用底层存储服务
    return _get_storage_service().save(**save_args)


def dw_query(
    data_name: str, field_values: Dict[str, Union[str, List[str]]] = None, **kwargs
) -> Optional[pd.DataFrame]:
    """
    从DataWhale本地数据集查询数据

    Args:
        data_name: 数据集名称
        field_values: 字段值映射，用于指定要查询的数据路径
        **kwargs: 额外参数
            - sort_by: 排序字段
            - parallel: 是否使用并行查询，默认为True
            - max_workers: 最大工作线程数

    Returns:
        Optional[pd.DataFrame]: 查询结果，如果查询失败则返回None

    Examples:
        >>> df = dw_query("stocks_daily", field_values={'code': '000001'})
        >>> df = dw_query("stocks_daily", field_values={'code': ['000001', '000002']}, sort_by="trade_date")
    """
    return _get_storage_service().query(
        data_name=data_name, field_values=field_values, **kwargs
    )


def dw_delete(data_name: str, field_values: Dict[str, str] = None) -> bool:
    """
    从DataWhale本地数据集删除数据

    Args:
        data_name: 数据集名称
        field_values: 字段值映射，用于指定要删除的数据路径。如果为None，则删除整个数据集。

    Returns:
        bool: 删除是否成功

    Examples:
        >>> dw_delete("stocks_daily", field_values={'code': '000001', 'trade_date': '2023-01-01'})
        >>> dw_delete("stocks_daily")  # 删除整个数据集
    """
    return _get_storage_service().delete(data_name=data_name, field_values=field_values)


def dw_exists(data_name: str, field_values: Dict[str, str] = None) -> bool:
    """
    检查DataWhale本地数据集或其中的数据是否存在

    Args:
        data_name: 数据集名称
        field_values: 字段值映射，用于指定要检查的数据路径。如果为None，则只检查数据集是否存在。

    Returns:
        bool: 数据集或指定数据是否存在

    Examples:
        >>> dw_exists("stocks_daily")
        >>> dw_exists("stocks_daily", field_values={'code': '000001', 'trade_date': '2023-01-01'})
    """
    return _get_storage_service().exists(data_name=data_name, field_values=field_values)


def query_last_line(
    dataset_name: str,
    field_values: Dict[str, str] = None,
    data_folder: str = None,
    meta_folder: str = None,
) -> Optional[pd.DataFrame]:
    """
    从多层数据集获取文件的最后一行数据

    Args:
        dataset_name: 数据集名称
        field_values: 字段值映射，用于定位具体文件
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Optional[pd.DataFrame]: 包含最后一行数据的DataFrame，如果文件不存在或为空则返回None

    Examples:
        >>> last_row = query_last_line("stocks_daily", field_values={'code': '000001'},
        ...                          data_folder="/path/to/data", meta_folder="/path/to/meta")
    """
    # 验证路径参数
    if data_folder is None or meta_folder is None:
        raise ValueError("必须提供data_folder和meta_folder的绝对路径")

    try:
        # 加载数据集
        dataset = Dataset.load_dataset(
            name=dataset_name, folder=data_folder, meta_folder=meta_folder
        )

        # 读取最后一行
        return dataset.read_last_line(field_values)

    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"读取数据最后一行失败: {str(e)}")
        return None


def query_last_n_lines(
    dataset_name: str,
    n: int,
    field_values: Dict[str, str] = None,
    data_folder: str = None,
    meta_folder: str = None,
) -> Optional[pd.DataFrame]:
    """
    从多层数据集获取文件的最后n行数据

    可以高效读取指定文件的最后n行数据，无需加载整个文件。
    对于大文件数据分析、数据校验和智能更新场景特别有用。

    Args:
        dataset_name: 数据集名称
        n: 需要读取的行数
        field_values: 字段值映射，用于定位具体文件
        data_folder: 数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Optional[pd.DataFrame]: 包含最后n行数据的DataFrame
                              如果文件不存在则返回None
                              如果文件为空（只有表头）则返回只有表头的空DataFrame

    Examples:
        >>> last_rows = query_last_n_lines(
        ...     "stocks_daily",
        ...     5,
        ...     field_values={'code': '000001'},
        ...     data_folder="/path/to/data",
        ...     meta_folder="/path/to/meta"
        ... )
    """
    # 验证路径参数
    if data_folder is None or meta_folder is None:
        raise ValueError("必须提供data_folder和meta_folder的绝对路径")

    try:
        # 加载数据集
        dataset = Dataset.load_dataset(
            name=dataset_name, folder=data_folder, meta_folder=meta_folder
        )

        # 读取最后n行
        return dataset.read_last_n_lines(n, field_values)

    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"读取数据最后{n}行失败: {str(e)}")
        return None


def dw_query_last_line(
    data_name: str,
    field_values: Dict[str, str] = None,
) -> Optional[pd.DataFrame]:
    """
    从DataWhale本地数据集获取文件的最后一行数据

    Args:
        data_name: 数据集名称
        field_values: 字段值映射，用于定位具体文件

    Returns:
        Optional[pd.DataFrame]: 包含最后一行数据的DataFrame，如果文件不存在或为空则返回None

    Examples:
        >>> last_row = dw_query_last_line("stocks_daily", field_values={'code': '000001'})
    """
    try:
        return _get_storage_service().read_last_line(
            data_name=data_name, field_values=field_values
        )
    except Exception as e:
        print(f"读取数据最后一行失败: {str(e)}")
        return None


def dw_query_last_n_lines(
    data_name: str,
    n: int,
    field_values: Dict[str, str] = None,
) -> Optional[pd.DataFrame]:
    """
    从DataWhale本地数据集获取文件的最后n行数据

    可以高效读取指定文件的最后n行数据，无需加载整个文件。
    这对于大文件数据分析、数据校验和智能更新场景特别有用。
    使用配置好的本地存储路径，简化调用。

    Args:
        data_name: 数据集名称
        n: 需要读取的行数，必须是正整数
        field_values: 字段值映射，用于定位具体文件

    Returns:
        Optional[pd.DataFrame]: 包含最后n行数据的DataFrame
                              如果文件不存在则返回None
                              如果文件为空（只有表头）则返回只有表头的空DataFrame

    Raises:
        ValueError: 当n不是正整数时抛出

    Examples:
        >>> # 读取股票数据的最后5行
        >>> last_rows = dw_query_last_n_lines("stocks_daily", 5, field_values={'code': '000001'})
        >>>
        >>> # 读取单层数据集的最后10行
        >>> last_rows = dw_query_last_n_lines("simple_dataset", 10)
    """
    # 直接验证n的值，不合法直接抛出异常
    if n <= 0:
        raise ValueError(f"n必须是正整数，当前值为: {n}")

    try:
        return _get_storage_service().read_last_n_lines(
            data_name=data_name, n=n, field_values=field_values
        )
    except Exception as e:
        print(f"读取数据最后{n}行失败: {str(e)}")
        return None


def infer_dtypes(data: pd.DataFrame) -> Dict[str, str]:
    """
    根据数据自动推断字段类型

    分析DataFrame的每一列，根据实际数据自动推断适合的数据类型。
    支持的类型映射:
    - 整数类型 -> 'int64'
    - 浮点类型 -> 'float64'
    - 字符串/对象类型 -> 'string'
    - 布尔类型 -> 'bool'
    - 日期时间类型 -> 'datetime64'

    Args:
        data: 待分析的数据框

    Returns:
        Dict[str, str]: 字段名到类型字符串的映射字典

    Examples:
        >>> df = pd.DataFrame({
        ...     'code': ['000001', '000002'],
        ...     'price': [10.5, 20.8],
        ...     'volume': [10000, 20000]
        ... })
        >>> dtypes = infer_dtypes(df)
        >>> print(dtypes)
        {'code': 'string', 'price': 'float64', 'volume': 'int64'}

    Raises:
        TypeError: 当输入不是pandas DataFrame时
    """
    # 从MetaInfo类使用该方法
    from .metainfo.metainfo import MetaInfo

    return MetaInfo.infer_dtypes_from_data(data)


# ============ 面板数据接口 ============


def panel_create(
    name: str,
    index_col: str,
    value_dtype: str,
    entity_col_name: str = "entity_id",
    format: str = "csv",
    structure_fields: List[str] = None,
    update_mode: str = "append",
    panel_folder: str = None,
    meta_folder: str = None,
) -> Optional[Panel]:
    """
    创建面板数据

    Args:
        name: 面板数据名称
        index_col: 索引列名称，通常为日期列
        value_dtype: 值的数据类型
        entity_col_name: 实体ID列名称，默认为'entity_id'
        format: 文件格式，默认为"csv"
        structure_fields: 用于生成动态层的字段列表
        update_mode: 更新模式，可选值："append"（追加）、"overwrite"（覆盖）或"update"（智能更新），默认为"append"
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Optional[Panel]: 创建的面板数据对象，如果创建失败则返回None

    Examples:
        >>> panel = panel_create(
        ...     name="stock_prices",
        ...     index_col="trade_date",
        ...     value_dtype="float64",
        ...     entity_col_name="entity_id",
        ...     format="csv",
        ...     structure_fields=["market", "indicator"],
        ...     update_mode="append",
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
    """
    # 验证路径参数
    if panel_folder is None or meta_folder is None:
        raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

    try:
        # 构建元信息字典
        meta_info = {
            "name": name,
            "type": "panel",
            "format": format,
            "update_mode": update_mode,
            "panel": {
                "index_col": index_col,
                "value_dtype": value_dtype,
                "entity_col_name": entity_col_name,
            },
            "dtypes": {},
        }

        # 如果有结构字段，添加dataset部分
        if structure_fields:
            meta_info["dataset"] = {"structure_fields": structure_fields}

        # 创建面板数据
        panel = Panel.create_panel(
            name=name,
            folder=panel_folder,
            meta_folder=meta_folder,
            index_col=index_col,
            value_dtype=value_dtype,
            entity_col_name=entity_col_name,
            format=format,
            structure_fields=structure_fields,
            update_mode=update_mode,
        )

        return panel
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"创建面板数据失败: {str(e)}")
        return None


def panel_save(
    data: pd.DataFrame,
    panel_name: str,
    field_values: Dict[str, str] = None,
    mode: str = None,
    update_key: str = None,
    panel_folder: str = None,
    meta_folder: str = None,
    **kwargs,
) -> bool:
    """
    保存数据到面板数据

    Args:
        data: 要保存的DataFrame数据
        panel_name: 面板数据名称
        field_values: 字段值映射，用于指定动态层的值
        mode: 保存模式，可选值："overwrite"（覆盖）、"append"（追加）或"update"（智能更新）
             如果为None，则使用面板数据默认的更新模式
        update_key: 当mode为'update'时，用于比较的列名，
                   只有该列值大于文件最后一行对应值的数据才会被追加
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供
        **kwargs: 额外参数

    Returns:
        bool: 保存是否成功

    Examples:
        >>> df = pd.DataFrame({
        ...     'date': ['2023-01-01', '2023-01-02'],
        ...     'entity_id': ['AAPL', 'AAPL'],
        ...     'value': [150.1, 151.2]
        ... })
        >>> panel_save(df, "stock_prices", field_values={'market': 'US', 'indicator': 'price'},
        ...            panel_folder="/path/to/panel", meta_folder="/path/to/meta")

        # 使用智能更新模式（只追加日期大于已有数据的记录）
        >>> panel_save(df, "stock_prices", field_values={'market': 'US'}, mode="update",
        ...            update_key="date", panel_folder="/path/to/panel", meta_folder="/path/to/meta")
    """
    # 验证路径参数
    if panel_folder is None or meta_folder is None:
        raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

    try:
        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 保存数据
        panel.save(data, field_values, mode, update_key, **kwargs)
        return True
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"保存数据到面板失败: {str(e)}")
        return False


def panel_query(
    panel_name: str,
    field_values: Dict[str, Union[str, List[str]]] = None,
    sort_by: str = None,
    parallel: bool = True,
    panel_folder: str = None,
    meta_folder: str = None,
    columns: List[str] = None,
    **kwargs,
) -> Optional[pd.DataFrame]:
    """从面板数据查询数据（宽格式）

    查询匹配指定字段值的面板数据，支持精确匹配和部分匹配。
    始终返回宽格式的面板数据，格式为：日期列+多个实体列。

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于筛选特定数据路径
                    如{'market': 'US', 'indicator': 'price'}，可以提供单值或列表
        sort_by: 排序字段，通常是索引列（日期列）
        parallel: 是否并行处理，默认为True
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供
        columns: 需要选择的列名列表，默认为None表示选择所有列
        **kwargs: 其他查询参数

    Returns:
        pd.DataFrame: 查询结果，如果没有匹配的数据则返回None

    Examples:
        >>> prices = panel_query("stock_prices",
        ...                      field_values={"market": "US", "indicator": "price"},
        ...                      sort_by="date",
        ...                      panel_folder="/path/to/panel",
        ...                      meta_folder="/path/to/meta")
        >>> # 只选择特定股票的价格数据
        >>> prices = panel_query("stock_prices",
        ...                      field_values={"market": "US", "indicator": "price"},
        ...                      columns=["date", "AAPL", "MSFT"],
        ...                      panel_folder="/path/to/panel",
        ...                      meta_folder="/path/to/meta")
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f"查询面板数据: panel={panel_name}, field_values={field_values}, sort_by={sort_by}, columns={columns}"
    )

    try:
        # 验证路径参数
        if panel_folder is None or meta_folder is None:
            raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 执行查询，传入columns参数
        result = panel.query(
            field_values=field_values,
            sort_by=sort_by,
            parallel=parallel,
            columns=columns,
            **kwargs,
        )

        # 如果结果为空DataFrame，返回None
        if result.empty:
            return None

        return result
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        logger.error(f"查询面板数据失败: {str(e)}")
        print(f"查询面板数据失败: {str(e)}")
        return None


def panel_delete(
    panel_name: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
) -> bool:
    """
    从面板数据删除数据

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于指定要删除的数据路径
                     如果为None，则删除整个面板数据
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        bool: 删除是否成功

    Examples:
        >>> panel_delete("stock_prices", field_values={'market': 'US', 'indicator': 'price'},
        ...              panel_folder="/path/to/panel", meta_folder="/path/to/meta")
        >>> panel_delete("stock_prices", panel_folder="/path/to/panel", meta_folder="/path/to/meta")  # 删除整个面板数据
    """
    # 验证路径参数
    if panel_folder is None or meta_folder is None:
        raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

    try:
        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 删除数据
        return panel.delete(field_values)
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"删除面板数据失败: {str(e)}")
        return False


def panel_exists(
    panel_name: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
) -> bool:
    """检查面板数据是否存在

    验证给定字段值组合的面板数据文件是否存在，支持精确检查、批量检查和整体检查。

    ### 存在性检查逻辑
    1. 精确检查：提供完整field_values时，检查特定文件是否存在
       例如field_values={'region': 'Asia', 'indicator': 'price'}检查亚洲区域的价格数据文件

    2. 批量检查：提供部分field_values时，检查是否存在任何匹配的文件
       例如field_values={'region': 'Asia'}检查是否存在任何亚洲区域的数据文件

    3. 整体检查：不提供field_values或提供空字典时，检查面板数据目录和元数据文件是否存在

    ### 文件匹配规则
    - 生成文件路径时会根据structure_fields的顺序构建匹配模式
    - 对于部分field_values，使用通配符匹配缺失部分
    - 支持单值或值列表的field_values，如{'region': 'Asia'}或{'region': ['Asia', 'Europe']}

    Args:
        panel_name: 面板数据名称
        field_values: 字段名到字段值的映射，用于定位要检查的文件
            如果为None或空字典，则检查整个面板数据目录是否存在
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        bool: 指定的面板数据是否存在

    Examples:
        >>> # 检查特定区域和指标的数据是否存在
        >>> exists = panel_exists("stock_prices",
        ...                       field_values={"region": "Asia", "indicator": "price"},
        ...                       panel_folder="/path/to/panel", meta_folder="/path/to/meta")

        >>> # 检查特定区域的任何数据是否存在
        >>> exists = panel_exists("stock_prices",
        ...                      field_values={"region": "Asia"},
        ...                      panel_folder="/path/to/panel", meta_folder="/path/to/meta")

        >>> # 检查面板数据是否存在
        >>> exists = panel_exists("stock_prices",
        ...                      panel_folder="/path/to/panel", meta_folder="/path/to/meta")
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f"检查面板数据是否存在: panel={panel_name}, field_values={field_values}"
    )

    # 验证路径参数
    if panel_folder is None or meta_folder is None:
        raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

    try:
        # 检查面板数据目录是否存在
        panel_dir = os.path.join(panel_folder, panel_name)

        # 如果没有提供field_values，只检查面板数据目录是否存在
        if field_values is None or not field_values:
            exists = os.path.exists(panel_dir)
            logger.debug(f"检查面板数据目录是否存在: {panel_dir}, 结果: {exists}")
            return exists

        try:
            # 尝试加载面板数据
            panel = Panel.load_panel(
                name=panel_name, folder=panel_folder, meta_folder=meta_folder
            )

            # 使用Panel.exists方法进行检查
            return panel.exists(field_values)

        except Exception as e:
            logger.error(f"加载面板数据失败: {panel_name}, 错误: {str(e)}")
            # 面板数据加载失败，返回False
            return False

    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        logger.error(f"检查面板数据存在性时发生错误: {str(e)}")
        return False


def panel_get_all_entities(
    panel_name: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
) -> List[str]:
    """获取面板数据中所有实体ID列表

    获取匹配指定条件的面板数据中所有实体的ID列表。
    实体列表基于面板数据中的列名，不包括索引列和字段值列。

    ### 实体识别逻辑
    1. 查询匹配field_values的面板数据
    2. 从结果DataFrame的列中提取所有非索引列和非字段列
    3. 返回这些列名作为实体ID列表

    ### 应用场景
    - 获取股票面板中的所有股票代码
    - 获取指定区域的所有公司ID
    - 动态生成实体选择器的选项列表

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于筛选特定数据范围
            如果为None或空，则查询所有数据
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        List[str]: 所有实体ID列表
        如果没有匹配数据或数据为空，返回空列表

    Examples:
        >>> # 获取美国市场所有股票代码
        >>> stocks = panel_get_all_entities(
        ...     panel_name="stock_prices",
        ...     field_values={"market": "US"},
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
        >>> print(f"美国市场的股票数量: {len(stocks)}")
        >>> print(f"股票列表前5个: {stocks[:5]}")
    """
    try:
        # 验证路径参数
        if panel_folder is None or meta_folder is None:
            raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 获取所有实体
        return panel.get_all_entities(field_values)
    except Exception as e:
        print(f"获取面板数据实体列表失败: {str(e)}")
        return []


def panel_get_entity_data(
    panel_name: str,
    entity_id: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
) -> Optional[pd.Series]:
    """获取特定实体的数据序列

    提取特定实体在匹配条件下的完整时间序列数据。
    返回一个pandas.Series对象，索引为日期，值为该实体在各日期的数据。

    ### 数据提取逻辑
    1. 查询匹配field_values的面板数据
    2. 检查实体ID是否存在于数据的列中
    3. 将日期列设置为索引
    4. 提取实体列的数据作为Series返回

    ### 应用场景
    - 提取单个股票的价格时间序列
    - 分析特定产品的销售趋势
    - 可视化单一实体的数据变化

    Args:
        panel_name: 面板数据名称
        entity_id: 实体标识符（列名），如股票代码"AAPL"
        field_values: 字段值映射，用于筛选特定数据范围
            如果为None或空，则查询所有数据
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Optional[pd.Series]: 特定实体的数据序列，索引为日期，名称为实体ID
        如果实体不存在或没有匹配数据，返回None

    Examples:
        >>> # 获取特定股票的价格数据
        >>> aapl_prices = panel_get_entity_data(
        ...     panel_name="stock_prices",
        ...     entity_id="AAPL",
        ...     field_values={"market": "US", "indicator": "price"},
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
        >>> print(f"AAPL最新价格: {aapl_prices.iloc[-1]}")
        >>> # 绘制价格曲线
        >>> import matplotlib.pyplot as plt
        >>> aapl_prices.plot(title="AAPL股价走势")
        >>> plt.show()
    """
    try:
        # 验证路径参数
        if panel_folder is None or meta_folder is None:
            raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 获取实体数据
        return panel.get_entity_data(entity_id, field_values)
    except Exception as e:
        print(f"获取实体数据失败: {str(e)}")
        return None


def panel_get_date_data(
    panel_name: str,
    date: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
) -> Optional[pd.Series]:
    """获取特定日期的横截面数据

    提取特定日期下所有实体的横截面数据。
    返回一个pandas.Series对象，索引为实体ID，值为各实体在该日期的数据。

    ### 数据提取逻辑
    1. 查询匹配field_values的面板数据
    2. 筛选特定日期的数据行
    3. 从该行提取所有非索引列的数据
    4. 返回包含所有实体值的Series，索引为实体ID

    ### 应用场景
    - 分析特定日期所有股票的表现
    - 对比某一天不同地区的销售数据
    - 研究某个时间点的市场截面特征

    Args:
        panel_name: 面板数据名称
        date: 日期字符串，需与索引列中的日期格式匹配
        field_values: 字段值映射，用于筛选特定数据范围
            如果为None或空，则查询所有数据
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Optional[pd.Series]: 特定日期的横截面数据，索引为实体ID，名称为日期字符串
        如果日期不存在或没有匹配数据，返回None

    Examples:
        >>> # 获取特定日期所有股票的价格数据
        >>> prices_20230103 = panel_get_date_data(
        ...     panel_name="stock_prices",
        ...     date="2023-01-03",
        ...     field_values={"market": "US", "indicator": "price"},
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
        >>> print(f"当日最高价股票: {prices_20230103.idxmax()}")
        >>> print(f"当日最低价股票: {prices_20230103.idxmin()}")
        >>> # 绘制横截面分布图
        >>> import matplotlib.pyplot as plt
        >>> prices_20230103.plot.bar(title="2023-01-03股价分布")
        >>> plt.show()
    """
    try:
        # 验证路径参数
        if panel_folder is None or meta_folder is None:
            raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 获取日期数据
        return panel.get_date_data(date, field_values)
    except Exception as e:
        print(f"获取日期数据失败: {str(e)}")
        return None


def panel_get_stats(
    panel_name: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
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

    ### 计算逻辑
    1. 查询匹配field_values的面板数据
    2. 将日期列设置为索引
    3. 计算各种统计指标
    4. 返回包含所有统计结果的字典

    ### 应用场景
    - 评估数据完整性和质量
    - 监控数据收集进度
    - 生成数据质量报告

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于筛选特定数据范围
            如果为None或空，则统计所有数据
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供

    Returns:
        Dict[str, Any]: 包含各种统计指标的字典
        如果没有匹配数据，返回包含零值的统计字典

    Examples:
        >>> # 获取美国市场价格数据的统计信息
        >>> stats = panel_get_stats(
        ...     panel_name="stock_prices",
        ...     field_values={"market": "US", "indicator": "price"},
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
        >>> print(f"数据完整度: {(1-stats['null_ratio'])*100:.2f}%")
        >>> print(f"时间序列长度: {stats['date_count']}天")
        >>> print(f"实体数量: {stats['entity_count']}个股票")
    """
    try:
        # 验证路径参数
        if panel_folder is None or meta_folder is None:
            raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 获取统计信息
        return panel.get_panel_stats(field_values)
    except Exception as e:
        print(f"获取面板数据统计信息失败: {str(e)}")
        # 返回默认统计信息
        return {
            "date_count": 0,
            "entity_count": 0,
            "total_cells": 0,
            "non_null_count": 0,
            "null_count": 0,
            "null_ratio": 0.0,
        }


# ============ DataWhale本地面板数据接口 ============


def dw_create_panel(
    name: str,
    index_col: str,
    value_dtype: str,
    entity_col_name: str = "entity_id",
    format: str = None,
    structure_fields: List[str] = None,
    update_mode: str = None,
) -> Panel:
    """创建面板数据（内部API）

    创建一个新的面板数据对象，初始化存储结构并生成元数据文件。
    此函数是panel_create的封装，使用系统配置中的存储路径，供DataWhale内部使用。

    ### 面板数据特点
    - 以日期为索引、实体为列的二维表格结构
    - 支持多层文件夹组织，便于按字段分类存储
    - 可动态扩展列数（添加新实体）和行数（添加新日期）

    ### 参数说明
    Args:
        name: 面板数据名称，会成为目录名的一部分
        index_col: 索引列名称，通常是日期列的列名，如"date"
        value_dtype: 值数据类型，如"float64"，定义了数值数据的存储类型
        entity_col_name: 实体列名称，存储实体ID的列名，默认为'entity_id'
        format: 文件格式，默认使用配置中的默认格式，目前仅支持CSV
        structure_fields: 文件结构字段列表，定义文件目录结构，如['market', 'indicator']
        update_mode: 更新模式，可选值：'overwrite'、'append'、'update'，默认使用配置中的默认值

    Returns:
        Panel: 创建的面板数据对象

    Raises:
        StorageError: 当参数无效或面板数据已存在时抛出

    Examples:
        >>> panel = dw_create_panel(
        ...     name="stock_prices",
        ...     index_col="date",
        ...     value_dtype="float64",
        ...     entity_col_name="stock_id",
        ...     structure_fields=["market"],
        ...     update_mode="append"
        ... )
        >>> print(f"面板数据 {panel.name} 创建成功")
    """
    return _get_panel_storage_service().create_panel(
        name=name,
        index_col=index_col,
        value_dtype=value_dtype,
        entity_col_name=entity_col_name,
        format=format,
        structure_fields=structure_fields,
        update_mode=update_mode,
    )


def dw_panel_save(
    data: pd.DataFrame,
    panel_name: str,
    field_values: Dict[str, str] = None,
    mode: str = None,
    update_key: str = None,
    **kwargs,
) -> bool:
    """保存数据到面板（内部API）

    将数据保存到面板存储系统中，支持多种数据格式和更新模式。
    此函数是panel_save的封装，使用系统配置中的存储路径，供DataWhale内部使用。

    ### 数据格式支持
    - 宽格式数据：日期为行，实体ID为列（原始面板格式）
    - 长格式数据：包含日期列、实体ID列和值列的扁平表格（会自动转换为宽格式存储）

    ### 更新模式说明
    1. overwrite(覆盖模式)：完全覆盖现有文件，丢弃原有所有数据
    2. append(追加模式)：将新数据直接追加到现有文件末尾
    3. update(更新模式)：根据update_key智能合并数据，更新已存在数据并追加新数据

    Args:
        data: 要保存的DataFrame数据（宽格式或长格式）
        panel_name: 面板数据名称
        field_values: 字段值映射，用于指定动态层的值
        mode: 保存模式，可选值："overwrite"（覆盖）、"append"（追加）或"update"（智能更新）
              如果为None，则使用面板数据默认的更新模式
        update_key: 当mode为'update'时，用于比较的列名，通常是日期列
        **kwargs: 额外参数
            - batch_size: 批量处理时的批次大小

    Returns:
        bool: 保存是否成功

    Raises:
        StorageError: 当保存操作失败时抛出

    Examples:
        >>> # 保存宽格式数据
        >>> df_wide = pd.DataFrame({
        ...     'date': ['2023-01-01', '2023-01-02'],
        ...     'AAPL': [150.1, 151.2],
        ...     'MSFT': [250.5, 252.3],
        ...     'GOOG': [2800.3, 2850.1]
        ... })
        >>> success = dw_panel_save(df_wide, "stock_prices",
        ...                        field_values={'market': 'US', 'indicator': 'price'})
        >>>
        >>> # 保存长格式数据，使用update模式
        >>> df_long = pd.DataFrame({
        ...     'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        ...     'entity_id': ['AAPL', 'AAPL', 'AAPL'],
        ...     'value': [150.1, 151.2, 153.5]
        ... })
        >>> success = dw_panel_save(df_long, "stock_prices",
        ...                        field_values={'market': 'US', 'indicator': 'price'},
        ...                        mode="update", update_key="date")
    """
    # 检查update_key和mode之间的关系
    if mode == "update" and update_key is None:
        raise ValueError("当mode为'update'时，必须提供update_key参数")

    # 准备传递给panel_storage_service.save的参数
    save_args = {
        "data": data,
        "panel_name": panel_name,
        "field_values": field_values,
    }

    # 只有当mode不为None时才添加mode参数
    if mode is not None:
        save_args["mode"] = mode

    # 只有当update_key不为None时才添加update_key参数
    if update_key is not None:
        save_args["update_key"] = update_key

    # 加入其他额外参数
    save_args.update(kwargs)

    # 调用底层存储服务
    return _get_panel_storage_service().save(**save_args)


def dw_panel_query(
    panel_name: str,
    field_values: Dict[str, Union[str, List[str]]] = None,
    sort_by: str = None,
    parallel: bool = True,
    max_workers: int = None,
    columns: List[str] = None,
) -> Optional[pd.DataFrame]:
    """从DataWhale本地面板数据查询数据

    查询匹配指定字段值的DataWhale本地面板数据，支持精确匹配和部分匹配。
    采用宽格式（面板格式）返回，其中行为日期，列为实体。

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于筛选特定数据，可以提供单值或列表值
            例如 {'market': 'US'} 或 {'market': ['US', 'EU']}
        sort_by: 排序字段，通常是索引列(日期列)
        parallel: 是否使用并行处理，默认为True，加快多文件处理速度
        max_workers: 并行处理的最大工作线程数，None表示使用默认值
        columns: 需要选择的列名列表，默认为None表示选择所有列

    Returns:
        pd.DataFrame: 查询结果，宽格式的面板数据
        如果没有匹配数据则返回None

    Examples:
        >>> # 查询美国市场的价格数据，按日期排序
        >>> prices = dw_panel_query(
        ...     panel_name="stock_prices",
        ...     field_values={"market": "US", "indicator": "price"},
        ...     sort_by="date"
        ... )
        >>> # 只选择特定股票的价格数据
        >>> prices = dw_panel_query(
        ...     panel_name="stock_prices",
        ...     field_values={"market": "US", "indicator": "price"},
        ...     columns=["date", "AAPL", "MSFT"]
        ... )
    """
    result = _get_panel_storage_service().query(
        panel_name=panel_name,
        field_values=field_values,
        sort_by=sort_by,
        parallel=parallel,
        max_workers=max_workers,
        columns=columns,
    )
    return result


def dw_panel_delete(panel_name: str, field_values: Dict[str, str] = None) -> bool:
    """从DataWhale本地面板数据删除数据

    删除匹配指定字段值的DataWhale本地面板数据。
    如果未提供field_values，则删除整个面板。

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于筛选要删除的特定数据

    Returns:
        bool: 删除是否成功

    Examples:
        >>> dw_panel_delete("stock_prices", field_values={'market': 'US'})
        >>> dw_panel_delete("stock_prices")  # 删除整个面板数据
    """
    return _get_panel_storage_service().delete(
        panel_name=panel_name, field_values=field_values
    )


def dw_panel_exists(panel_name: str, field_values: Dict[str, str] = None) -> bool:
    """检查DataWhale本地面板数据是否存在

    检查指定名称的面板数据或其中的特定数据是否存在。

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于检查特定数据的存在性
            如果为None，则只检查面板数据是否存在

    Returns:
        bool: 面板数据或指定数据是否存在

    Examples:
        >>> dw_panel_exists("stock_prices")
        >>> dw_panel_exists("stock_prices", field_values={'market': 'US'})
    """
    return _get_panel_storage_service().exists(
        panel_name=panel_name, field_values=field_values
    )


def dw_panel_get(panel_name: str) -> Optional[Panel]:
    """获取DataWhale本地面板对象

    通过名称获取DataWhale本地面板对象，用于高级操作。

    Args:
        panel_name: 面板数据名称

    Returns:
        Optional[Panel]: 面板对象，如果不存在则返回None

    Examples:
        >>> panel = dw_panel_get("stock_prices")
        >>> if panel:
        ...     print(f"索引列: {panel.index_col}")
        ...     print(f"实体列: {panel.entity_col_name}")
    """
    return _get_panel_storage_service().get_panel(panel_name)


def panel_read_last_line(
    panel_name: str,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
    dtypes: Dict[str, str] = None,
) -> Optional[pd.DataFrame]:
    """读取面板数据文件的最后一行

    根据字段值确定面板数据文件，并高效读取该文件的最后一行，无需加载整个文件。
    这对于大文件的智能更新模式下检查最新记录特别有用。

    ### 应用场景
    - 检查最新日期记录，确定是否需要更新数据
    - 获取最新的市场数据，进行实时分析
    - 快速查看最新的数据状态，而无需加载全部历史数据

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于定位具体文件
            如果是单层结构面板，可以为None
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供
        dtypes: 数据类型字典，指定各列的数据类型
            如果为None则使用元数据中的dtypes

    Returns:
        Optional[pd.DataFrame]: 包含最后一行数据的DataFrame
            如果文件不存在或为空则返回None

    Raises:
        ValueError: 参数无效或读取过程中出错时抛出
        FileNotFoundError: 当指定的文件不存在时抛出

    Examples:
        >>> # 读取特定面板的最后一行数据
        >>> last_row = panel_read_last_line(
        ...     panel_name="stock_prices",
        ...     field_values={"market": "US", "indicator": "price"},
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
        >>>
        >>> # 如果成功读取，打印最后一行的日期和价格信息
        >>> if last_row is not None and not last_row.empty:
        ...     print(f"最新日期: {last_row['date'].iloc[0]}")
        ...     print(f"Apple股价: {last_row['AAPL'].iloc[0]}")
    """
    # 验证路径参数
    if panel_folder is None or meta_folder is None:
        raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

    try:
        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 读取最后一行
        return panel.read_last_line(field_values, dtypes)
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"读取面板数据最后一行失败: {str(e)}")
        if isinstance(e, FileNotFoundError):
            raise e
        else:
            raise ValueError(f"读取面板数据最后一行失败: {str(e)}")


def panel_read_last_n_lines(
    panel_name: str,
    n: int,
    field_values: Dict[str, str] = None,
    panel_folder: str = None,
    meta_folder: str = None,
    dtypes: Dict[str, str] = None,
) -> Optional[pd.DataFrame]:
    """读取面板数据文件的最后n行

    根据字段值确定面板数据文件，并高效读取该文件的最后n行数据，无需加载整个文件。
    这对于大文件的数据分析和智能更新模式特别有用。

    ### 应用场景
    - 分析最近n天的市场趋势
    - 获取最新的交易记录进行回测
    - 在不加载全部历史数据的情况下进行数据预处理

    Args:
        panel_name: 面板数据名称
        n: 需要读取的行数，必须是正整数
        field_values: 字段值映射，用于定位具体文件
            如果是单层结构面板，可以为None
        panel_folder: 面板数据存储目录的绝对路径，必须提供
        meta_folder: 元数据存储目录的绝对路径，必须提供
        dtypes: 数据类型字典，指定各列的数据类型
            如果为None则使用元数据中的dtypes

    Returns:
        Optional[pd.DataFrame]: 包含最后n行数据的DataFrame
            如果文件为空返回None
            如果文件只有表头则返回一个只有表头的空DataFrame

    Raises:
        ValueError: 当n不是正整数，或读取过程中出错时抛出
        FileNotFoundError: 当指定的文件不存在时抛出

    Examples:
        >>> # 读取特定面板最后10行数据
        >>> last_rows = panel_read_last_n_lines(
        ...     panel_name="stock_prices",
        ...     n=10,
        ...     field_values={"market": "US", "indicator": "price"},
        ...     panel_folder="/path/to/panel",
        ...     meta_folder="/path/to/meta"
        ... )
        >>>
        >>> # 绘制最近10天的价格趋势图
        >>> if last_rows is not None and not last_rows.empty:
        ...     import matplotlib.pyplot as plt
        ...     last_rows.set_index('date')['AAPL'].plot(title="Apple最近10天股价")
        ...     plt.show()
    """
    try:
        # 验证n是否为正整数
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"n必须是正整数，当前值为: {n}")

        # 验证路径参数
        if panel_folder is None or meta_folder is None:
            raise ValueError("必须提供panel_folder和meta_folder的绝对路径")

        # 加载面板数据
        panel = Panel.load_panel(
            name=panel_name, folder=panel_folder, meta_folder=meta_folder
        )

        # 读取最后n行
        return panel.read_last_n_lines(n, field_values, dtypes)
    except ValueError as e:
        # 路径参数验证失败，继续抛出异常
        raise e
    except Exception as e:
        print(f"读取面板数据最后{n}行失败: {str(e)}")
        if isinstance(e, FileNotFoundError):
            raise e
        else:
            raise ValueError(f"读取面板数据最后{n}行失败: {str(e)}")


def dw_panel_read_last_line(
    panel_name: str, field_values: Dict[str, str] = None, dtypes: Dict[str, str] = None
) -> Optional[pd.DataFrame]:
    """读取本地面板数据文件的最后一行（内部API）

    根据字段值确定面板数据文件，并高效读取该文件的最后一行，无需加载整个文件。
    此函数是panel_read_last_line的封装，使用系统配置中的存储路径，供DataWhale内部使用。

    ### 应用场景
    - 检查最新日期记录，确定是否需要更新数据
    - 获取最新的市场数据，进行实时分析
    - 智能更新模式中快速检查记录状态

    Args:
        panel_name: 面板数据名称
        field_values: 字段值映射，用于定位具体文件
            如果是单层结构面板，可以为None
        dtypes: 数据类型字典，指定各列的数据类型
            如果为None则使用元数据中的dtypes

    Returns:
        Optional[pd.DataFrame]: 包含最后一行数据的DataFrame
            如果文件不存在或为空则返回None

    Raises:
        StorageError: 读取失败时抛出

    Examples:
        >>> # 读取美国市场股票价格的最后一行
        >>> last_row = dw_panel_read_last_line(
        ...     panel_name="stock_prices",
        ...     field_values={"market": "US", "indicator": "price"}
        ... )
        >>>
        >>> # 获取最新交易日的所有股票收盘价
        >>> if last_row is not None and not last_row.empty:
        ...     latest_date = last_row.iloc[0]['date']
        ...     print(f"最新交易日: {latest_date}")
        ...     for col in last_row.columns:
        ...         if col not in ['date', 'market', 'indicator']:
        ...             print(f"{col}: {last_row.iloc[0][col]}")
    """
    return _get_panel_storage_service().read_last_line(
        panel_name=panel_name, field_values=field_values, dtypes=dtypes
    )


def dw_panel_read_last_n_lines(
    panel_name: str,
    n: int,
    field_values: Dict[str, str] = None,
    dtypes: Dict[str, str] = None,
) -> Optional[pd.DataFrame]:
    """读取本地面板数据文件的最后n行（内部API）

    根据字段值确定面板数据文件，并高效读取该文件的最后n行数据，无需加载整个文件。
    此函数是panel_read_last_n_lines的封装，使用系统配置中的存储路径，供DataWhale内部使用。

    ### 数据处理特点
    - 高效读取：仅读取文件末尾数据，适合处理大文件
    - 保留结构：返回的数据保持宽格式，每行一个日期，每列一个实体
    - 类型转换：自动处理数据类型转换，确保返回类型正确的DataFrame

    Args:
        panel_name: 面板数据名称
        n: 需要读取的行数，必须是正整数
        field_values: 字段值映射，用于定位具体文件
            如果是单层结构面板，可以为None
        dtypes: 数据类型字典，指定各列的数据类型
            如果为None则使用元数据中的dtypes

    Returns:
        Optional[pd.DataFrame]: 包含最后n行数据的DataFrame
            如果文件为空返回None
            如果文件只有表头则返回一个只有表头的空DataFrame

    Raises:
        ValueError: 当n不是正整数时抛出
        StorageError: 读取过程中出错时抛出

    Examples:
        >>> # 读取美国市场股票价格的最后5个交易日数据
        >>> last_rows = dw_panel_read_last_n_lines(
        ...     panel_name="stock_prices",
        ...     n=5,
        ...     field_values={"market": "US", "indicator": "price"}
        ... )
        >>>
        >>> # 计算最近5日的平均价格
        >>> if last_rows is not None and not last_rows.empty:
        ...     # 设置日期为索引
        ...     df = last_rows.set_index('date')
        ...     # 计算每只股票的平均价格
        ...     mean_prices = df.mean()
        ...     # 移除字段值列
        ...     mean_prices = mean_prices.drop(['market', 'indicator'], errors='ignore')
        ...     print(f"最近5日平均价格:\n{mean_prices}")
    """
    return _get_panel_storage_service().read_last_n_lines(
        panel_name=panel_name, n=n, field_values=field_values, dtypes=dtypes
    )
