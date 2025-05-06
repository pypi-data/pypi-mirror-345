#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""字段标准化装饰器模块

提供用于标准化字段的装饰器。
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast, TypeVar, Set

# 需要导入相关的字段标准化函数
from .interface import standardize_field, convert_field

# 尝试导入pandas，但不强制要求
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

F = TypeVar("F", bound=Callable[..., Any])


def standardize_field_values(
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
    target_params: Optional[Union[str, List[str]]] = None,
    result_key: Optional[str] = None,
    df_columns: Optional[Union[str, List[str]]] = None,
    df_param: Optional[str] = None,
    df_result: bool = False,
) -> Callable[[F], F]:
    """字段值标准化装饰器

    这是字段标准化系统的核心装饰器，可以对函数的参数值、返回值、DataFrame参数或DataFrame返回值中的字段名称进行标准化处理。
    该装饰器支持多种标准化场景，并可以根据需要组合使用不同的参数。

    核心功能:
    1. 参数值标准化：将函数参数中的字段名标准化
    2. 返回值字段标准化：将函数返回值中的特定字段标准化
    3. DataFrame列名标准化：将DataFrame参数或返回值的列名标准化

    Args:
        source (Optional[str]):
            源数据字段格式，如"akshare"、"tushare"等。
            - 当不提供时（None），假定输入已经是标准格式
            - 当处理非标准格式的字段名时必须提供
            - 常见值：None, "akshare", "tushare", "baostock", "joinquant", "rqdata"

        target_source (Optional[str]):
            目标数据字段格式。
            - 当不提供时（None），输出将保持标准格式
            - 当需要将标准格式转换为特定格式时提供
            - 常见值同source参数

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 当处理可能有歧义的字段名时尤为重要
            - 例如："price"（价格类）, "volume"（交易量类）, "ratio"（比率类）
            - 也可以指定更具体的类型，如："close_price", "open_price", "trading_volume"等

        target_params (Optional[Union[str, List[str]]]):
            要标准化的参数名称，字符串或字符串列表。
            - 当需要标准化函数参数中的字段名称时必须提供
            - 可以指定多个参数名，如["price_field", "volume_field"]
            - 与result_key, df_param, df_result至少要提供一个，否则装饰器无效
            - 注意：参数默认值通常不会被转换，只有显式传入的参数值会被标准化

        result_key (Optional[str]):
            要标准化的返回值字段名称。
            - 当需要标准化函数返回的字典或对象中的特定字段时提供
            - 例如，返回值为{"field": "close"}，则result_key="field"
            - 与target_params, df_param, df_result至少要提供一个，否则装饰器无效

        df_columns (Optional[Union[str, List[str]]]):
            要处理的DataFrame列名，字符串或字符串列表。
            - 当只需处理DataFrame中的特定列时提供
            - 不提供时将处理所有列（可能会降低效率）
            - 只有当df_param或df_result为True时有效

        df_param (Optional[str]):
            包含DataFrame的参数名称。
            - 当需要处理函数参数中的DataFrame列名时提供
            - 与target_params, result_key, df_result至少要提供一个，否则装饰器无效

        df_result (bool):
            是否处理返回的DataFrame。
            - 设为True时，将处理函数返回的DataFrame的列名
            - 默认为False
            - 与target_params, result_key, df_param至少要提供一个，否则装饰器无效

    Returns:
        装饰后的函数，其参数或返回值将根据设置被标准化

    参数组合和使用场景:

    1. 参数值标准化场景:
       必填参数: target_params
       可选参数: source, target_source, field_type

       @standardize_field_values(source="akshare", target_params="price_field")
       def func(price_field="close"):
           # price_field 将从 akshare 格式转换为标准格式
           # 注意：默认参数值"close"通常不会被转换，只有显式传入的参数会被标准化
           return price_field

    2. 返回值标准化场景:
       必填参数: result_key
       可选参数: source, target_source, field_type

       @standardize_field_values(target_source="tushare", result_key="field")
       def func():
           # 返回值中的 field 字段将从标准格式转换为 tushare 格式
           return {"field": "price"}

    3. DataFrame参数列名标准化场景:
       必填参数: df_param
       可选参数: source, target_source, field_type, df_columns

       @standardize_field_values(source="akshare", df_param="data", df_columns=["close"])
       def func(data):
           # data DataFrame 中的 close 列名将从 akshare 格式转换为标准格式
           # DataFrame保持DataFrame类型，只有列名被修改
           return data

    4. DataFrame返回值列名标准化场景:
       必填参数: df_result=True
       可选参数: source, target_source, field_type, df_columns

       @standardize_field_values(target_source="joinquant", df_result=True)
       def func():
           # 返回的 DataFrame 所有列名将从标准格式转换为 joinquant 格式
           # DataFrame保持DataFrame类型，只有列名被修改
           return pd.DataFrame({"price": [100, 101]})

    5. 混合场景 - 同时处理参数和返回值:
       @standardize_field_values(
           source="akshare",
           target_source="tushare",
           target_params=["field1"],
           result_key="field2"
       )
       def func(field1):
           # field1 参数和返回值中的 field2 都会被标准化
           return {"field2": field1}

    6. 完整场景 - 同时处理所有类型的输入和输出:
       @standardize_field_values(
           source="akshare",
           target_source="tushare",
           field_type="price",
           target_params=["price_field"],
           result_key="result_field",
           df_param="df_input",
           df_result=True,
           df_columns=["open", "close"]
       )
       def complex_func(price_field, df_input):
           # 多种数据同时被标准化
           return {"result_field": price_field, "dataframe": df_input}

    注意事项:
    1. target_params, result_key, df_param, df_result 至少要提供一个，否则装饰器不会有任何作用
    2. 当提供 field_type 时，会显著提高字段匹配的准确性，特别是处理同名但不同类型的字段时
    3. 当处理 DataFrame 时，如果指定了 df_columns，只会处理这些列，提高效率
    4. 标准化过程是两步的：先将输入转换为标准格式，再从标准格式转换为目标格式（如果指定）
    5. 如果字段在预定义的映射表中找不到对应关系，将保持原样不变
    6. 当处理 DataFrame 时，需要安装 pandas 库，否则会抛出 ImportError
    7. 注意：函数的默认参数值通常不会被自动转换，只有函数调用时显式传入的参数值会被标准化
    """

    # 将单个参数名或列名转换为列表
    if isinstance(target_params, str):
        target_params = [target_params]
    if isinstance(df_columns, str):
        df_columns = [df_columns]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查pandas是否可用
            if (df_param or df_result) and not PANDAS_AVAILABLE:
                raise ImportError("处理DataFrame需要安装pandas库")

            # 处理被标准化的参数值
            if target_params:
                # 获取函数签名
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)

                # 标准化传入的目标参数值
                for param_name in target_params:
                    if param_name in bound_args.arguments:
                        param_value = bound_args.arguments[param_name]
                        # 忽略None值
                        if param_value is not None:
                            # 先标准化参数值，再转换为目标格式（如果需要）
                            std_value = standardize_field(
                                param_value, source, field_type
                            )
                            if target_source:
                                std_value = convert_field(
                                    std_value, target_source, field_type
                                )
                            bound_args.arguments[param_name] = std_value

                # 更新位置参数和关键字参数
                new_args = []
                for p_name in sig.parameters:
                    if p_name in bound_args.arguments:
                        if len(new_args) < len(args) and list(
                            sig.parameters.keys()
                        ).index(p_name) < len(args):
                            new_args.append(bound_args.arguments[p_name])
                        else:
                            kwargs[p_name] = bound_args.arguments[p_name]

                # 如果有位置参数，使用更新后的位置参数
                if new_args:
                    args = tuple(new_args)

            # 处理DataFrame参数
            if df_param and PANDAS_AVAILABLE:
                # 获取函数签名
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)

                if df_param in bound_args.arguments:
                    df = bound_args.arguments[df_param]
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # 确定要处理的列
                        cols_to_process = (
                            df_columns if df_columns else df.columns.tolist()
                        )
                        # 只处理DataFrame中实际存在的列
                        cols_to_process = [
                            col for col in cols_to_process if col in df.columns
                        ]

                        # 创建新的列名映射
                        rename_map = {}
                        for col in cols_to_process:
                            # 标准化列名，再转换为目标格式（如果需要）
                            std_col = standardize_field(col, source, field_type)
                            if target_source:
                                std_col = convert_field(
                                    std_col, target_source, field_type
                                )
                            rename_map[col] = std_col

                        # 重命名DataFrame列
                        if rename_map:
                            df = df.rename(columns=rename_map)
                            bound_args.arguments[df_param] = df

                        # 更新位置参数和关键字参数
                        new_args = []
                        for p_name in sig.parameters:
                            if p_name in bound_args.arguments:
                                if len(new_args) < len(args) and list(
                                    sig.parameters.keys()
                                ).index(p_name) < len(args):
                                    new_args.append(bound_args.arguments[p_name])
                                else:
                                    kwargs[p_name] = bound_args.arguments[p_name]

                        # 如果有位置参数，使用更新后的位置参数
                        if new_args:
                            args = tuple(new_args)

            # 执行原函数
            result = func(*args, **kwargs)

            # 处理返回值字段
            if result_key and result is not None:
                if isinstance(result, dict):
                    if result_key in result and result[result_key] is not None:
                        # 先标准化字段值，再转换为目标格式（如果需要）
                        std_value = standardize_field(
                            result[result_key], source, field_type
                        )
                        if target_source:
                            std_value = convert_field(
                                std_value, target_source, field_type
                            )
                        result[result_key] = std_value
                elif hasattr(result, result_key):
                    # 如果返回的是对象且有该属性
                    attr_value = getattr(result, result_key)
                    if attr_value is not None:
                        # 先标准化字段值，再转换为目标格式（如果需要）
                        std_value = standardize_field(attr_value, source, field_type)
                        if target_source:
                            std_value = convert_field(
                                std_value, target_source, field_type
                            )
                        setattr(result, result_key, std_value)

            # 处理返回的DataFrame
            if (
                df_result
                and PANDAS_AVAILABLE
                and isinstance(result, pd.DataFrame)
                and not result.empty
            ):
                # 确定要处理的列
                cols_to_process = df_columns if df_columns else result.columns.tolist()
                # 只处理DataFrame中实际存在的列
                cols_to_process = [
                    col for col in cols_to_process if col in result.columns
                ]

                # 创建新的列名映射
                rename_map = {}
                for col in cols_to_process:
                    # 标准化列名，再转换为目标格式（如果需要）
                    std_col = standardize_field(col, source, field_type)
                    if target_source:
                        std_col = convert_field(std_col, target_source, field_type)
                    rename_map[col] = std_col

                # 重命名DataFrame列
                if rename_map:
                    result = result.rename(columns=rename_map)

            return result

        return cast(F, wrapper)

    return decorator


def standardize_param_field(
    param_name: str,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化参数字段值装饰器

    将函数中指定参数的字段值标准化。这是一个便捷装饰器，是standardize_field_values的简化版本，
    专门用于处理单个参数的场景。

    Args:
        param_name (str):
            参数名称，其值将被标准化。这是必填参数，指定哪个参数的值需要被标准化。
            例如："price_field", "column_name", "field_type"等。

        source (Optional[str]):
            输入字段值的数据源格式。
            - 当不提供时（None），假定输入已经是标准格式
            - 常见值："akshare", "tushare", "baostock", "joinquant", "rqdata"
            - 如果参数值不是标准格式，则必须提供此参数

        target_source (Optional[str]):
            输出字段值的目标数据源格式。
            - 当不提供时（None），输出将保持标准格式
            - 常见值同source参数
            - 当需要将标准字段名转换为特定数据源格式时使用

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 例如："price", "volume", "return", "close_price"等
            - 当字段名称可能有歧义时，强烈建议提供此参数
            - 不提供时，将根据名称相似度进行匹配，可能不够准确

    Returns:
        装饰后的函数，其指定参数的值将被标准化

    使用场景:

    1. 基本用法 - 将参数从特定格式转换为标准格式:
       @standardize_param_field("price_field", source="akshare")
       def get_data(price_field="收盘"):
           # 注意：默认参数值"收盘"通常不会自动转换
           # 但显式传入的price_field参数值会从akshare格式转换为标准格式
           # 例如显式传入"收盘"会变成"close"
           return price_field

    2. 将参数从标准格式转换为特定格式:
       @standardize_param_field("field_name", target_source="tushare")
       def process_data(field_name="close"):
           # 显式传入的field_name参数值将从标准格式转换为tushare格式
           # 例如传入"close"可能变成"close"
           return field_name

    3. 指定字段类型提高准确性:
       @standardize_param_field("field", source="akshare", field_type="price")
       def analyze(field="收盘"):
           # 指定field是价格类型，确保正确匹配为"close"
           # 但注意，默认参数值"收盘"通常不会被自动转换
           return field

    4. 完整转换链:
       @standardize_param_field("field", source="akshare", target_source="baostock", field_type="price")
       def convert_field(field="收盘"):
           # 显式传入的field参数值从akshare格式转换为标准格式(close)，然后再转换为baostock格式(close)
           return field

    注意事项:
    1. 此装饰器仅处理单个参数，如果需要处理多个参数，请使用standardize_field_values或standardize_param_fields
    2. 如果提供的字段在预定义的映射表中找不到对应关系，将保持原样不变
    3. 当字段名称模糊时，field_type参数可以显著提高匹配准确性
    4. field_mapping.json中定义了标准字段名，是字段标准化的基础，标准格式就是name字段的值
    5. 函数的默认参数值通常不会被自动转换，只有函数调用时显式传入的参数值会被标准化
    """
    return standardize_field_values(
        source=source,
        target_source=target_source,
        field_type=field_type,
        target_params=param_name,
    )


def standardize_param_fields(
    param_name: str,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化参数字段列表装饰器

    将函数中指定的字段列表参数中的每个字段值标准化。这个装饰器专门用于处理包含多个字段名称的列表参数，
    会对列表中的每个元素进行标准化处理。

    Args:
        param_name (str):
            包含字段列表的参数名称。这是必填参数，指定哪个列表参数需要被标准化。
            例如："fields", "columns", "metrics"等。

        source (Optional[str]):
            输入字段值的数据源格式。
            - 当不提供时（None），假定输入已经是标准格式
            - 常见值："akshare", "tushare", "baostock", "joinquant", "rqdata"
            - 如果列表中的字段不是标准格式，则必须提供此参数

        target_source (Optional[str]):
            输出字段值的目标数据源格式。
            - 当不提供时（None），输出将保持标准格式
            - 常见值同source参数
            - 当需要将标准字段名转换为特定数据源格式时使用

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 例如："price", "volume", "return"等
            - 当列表中的字段名可能有歧义时，建议提供此参数
            - 所有列表元素将使用相同的field_type进行匹配

    Returns:
        装饰后的函数，其指定参数中的字段列表将被逐一标准化

    使用场景:

    1. 基本用法 - 标准化字段列表:
       @standardize_param_fields("field_list", source="akshare")
       def get_data(field_list=["开盘", "收盘", "最高", "最低"]):
           # field_list中的每个元素都会从akshare格式转换为标准格式
           # 例如 ["开盘", "收盘", "最高", "最低"] 会变成 ["open", "close", "high", "low"]
           return pd.DataFrame(columns=field_list)

    2. 将标准字段列表转换为特定格式:
       @standardize_param_fields("columns", target_source="tushare")
       def process_data(columns=["open", "close"]):
           # columns列表中的每个元素从标准格式转换为tushare格式
           # 例如 ["open", "close"] 可能变成 ["open", "close"]
           return columns

    3. 指定字段类型处理特定领域数据:
       @standardize_param_fields("metrics", source="akshare", field_type="price")
       def analyze(metrics=["开盘", "收盘"]):
           # 指定metrics中的字段都是价格类型，确保正确匹配为 ["open", "close"]
           return metrics

    注意事项:
    1. 此装饰器专门处理包含多个字段名的列表参数，列表中的每个元素都会被单独标准化
    2. 列表中的None值会被保留，不会进行标准化处理
    3. 如果列表中某个字段在预定义的映射表中找不到对应关系，该字段将保持原样不变
    4. 所有字段会使用相同的field_type进行匹配，如果列表中包含不同类型的字段，可能需要分别处理
    5. 此装饰器不会改变参数的类型，输入列表将得到标准化后的列表
    6. field_mapping.json中定义了标准字段名，是字段标准化的基础，标准格式就是name字段的值
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数签名
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)

            # 处理字段列表参数
            if param_name in bound_args.arguments:
                fields_list = bound_args.arguments[param_name]
                if fields_list is not None:
                    # 标准化列表中的每个字段值
                    if isinstance(fields_list, list):
                        std_fields = []
                        for field in fields_list:
                            if field is not None:
                                # 先标准化字段值，再转换为目标格式（如果需要）
                                std_field = standardize_field(field, source, field_type)
                                if target_source:
                                    std_field = convert_field(
                                        std_field, target_source, field_type
                                    )
                                std_fields.append(std_field)
                            else:
                                std_fields.append(None)

                        # 更新参数值
                        bound_args.arguments[param_name] = std_fields

                        # 更新位置参数和关键字参数
                        new_args = []
                        for p_name in sig.parameters:
                            if p_name in bound_args.arguments:
                                if len(new_args) < len(args) and list(
                                    sig.parameters.keys()
                                ).index(p_name) < len(args):
                                    new_args.append(bound_args.arguments[p_name])
                                else:
                                    kwargs[p_name] = bound_args.arguments[p_name]

                        # 如果有位置参数，使用更新后的位置参数
                        if new_args:
                            args = tuple(new_args)

            # 执行原函数
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def standardize_result_field(
    result_key: str,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化函数返回值中特定字段的装饰器

    将函数返回值（字典）中指定键的字段值标准化。适用于返回字典格式的函数，
    会对字典中特定键的值进行标准化处理。

    Args:
        result_key (str):
            返回值字典中需要标准化的键名。这是必填参数，指定返回字典中哪个键的值需要被标准化。
            例如："field_name", "column", "price_field"等。

        source (Optional[str]):
            输入字段值的数据源格式。
            - 当不提供时（None），假定输入已经是标准格式
            - 常见值："akshare", "tushare", "baostock", "joinquant", "rqdata"
            - 如果返回值中的字段不是标准格式，则必须提供此参数

        target_source (Optional[str]):
            输出字段值的目标数据源格式。
            - 当不提供时（None），输出将保持标准格式
            - 常见值同source参数
            - 当需要将标准字段名转换为特定数据源格式时使用

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 例如："price", "volume", "return", "close_price"等
            - 当字段名称可能有歧义时，强烈建议提供此参数
            - 不提供时，将根据名称相似度进行匹配，可能不够准确

    Returns:
        装饰后的函数，其返回值中指定键的值将被标准化

    使用场景:

    1. 基本用法 - 标准化返回字典中的字段:
       @standardize_result_field("field_name", source="akshare")
       def get_field_info():
           # 返回一个包含field_name键的字典
           return {"field_name": "收盘", "value": 100}
           # 结果会变为：{"field_name": "close", "value": 100}

    2. 将返回值中的标准字段转换为特定格式:
       @standardize_result_field("column", target_source="tushare")
       def get_column():
           # 函数返回的字典中column键值将从标准格式转换为tushare格式
           return {"column": "close", "description": "当日收盘价"}
           # 结果会变为：{"column": "close", "description": "当日收盘价"}

    3. 指定字段类型提高匹配准确性:
       @standardize_result_field("field", source="akshare", field_type="price")
       def get_price_field():
           return {"field": "收盘", "data": [100, 101, 102]}
           # 指定field是价格类型，确保正确匹配为 "close"

    4. 完整转换链:
       @standardize_result_field("metric", source="akshare", target_source="baostock", field_type="price")
       def convert_metric():
           # 返回值中的metric键从akshare格式转换为标准格式，然后再转换为baostock格式
           return {"metric": "收盘"}
           # 结果会变为：{"metric": "close"}

    注意事项:
    1. 此装饰器仅适用于返回字典的函数
    2. 只会处理字典中指定键的值，其他键不受影响
    3. 如果返回值不是字典，或者指定的键不存在，函数将不做任何处理直接返回原结果
    4. 如果提供的字段在预定义的映射表中找不到对应关系，该字段将保持原样不变
    5. field_mapping.json中定义了标准字段名，是字段标准化的基础，标准格式就是name字段的值
    """
    return standardize_field_values(
        source=source,
        target_source=target_source,
        field_type=field_type,
        result_key=result_key,
    )


def standardize_return_value(
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化函数返回值装饰器

    将函数的整个返回值作为字段名进行标准化。适用于函数直接返回单个字段名（字符串）的情况。

    Args:
        source (Optional[str]):
            输入字段值的数据源格式。
            - 当不提供时（None），假定输入已经是标准格式
            - 常见值："akshare", "tushare", "baostock", "joinquant", "rqdata"
            - 如果函数返回的字段不是标准格式，则必须提供此参数

        target_source (Optional[str]):
            输出字段值的目标数据源格式。
            - 当不提供时（None），输出将保持标准格式
            - 常见值同source参数
            - 当需要将标准字段名转换为特定数据源格式时使用

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 例如："price", "volume", "return", "close_price"等
            - 当字段名称可能有歧义时，强烈建议提供此参数
            - 不提供时，将根据名称相似度进行匹配，可能不够准确

    Returns:
        装饰后的函数，其字符串返回值将被标准化

    使用场景:

    1. 基本用法 - 标准化函数返回的字段名:
       @standardize_return_value(source="akshare")
       def get_default_price_field():
           return "收盘"  # 返回值将被标准化为 "close"

    2. 将返回的标准字段名转换为特定格式:
       @standardize_return_value(target_source="tushare")
       def get_price_column():
           return "close"  # 返回值将被转换为tushare格式 "close"

    3. 指定字段类型提高匹配准确性:
       @standardize_return_value(source="akshare", field_type="price")
       def default_price_indicator():
           return "收盘"  # 明确指定是价格类型字段，提高匹配准确性

    4. 完整转换链 - 跨平台字段转换:
       @standardize_return_value(source="akshare", target_source="baostock", field_type="price")
       def convert_price_field():
           return "收盘"  # 从akshare格式转换为标准格式(close)，再转换为baostock格式(close)

    注意事项:
    1. 此装饰器只适用于直接返回字符串(字段名)的函数
    2. 如果函数返回值不是字符串，将不做任何处理直接返回
    3. 如果字段在预定义的映射表中找不到对应关系，返回值将保持原样不变
    4. 当字段名称模糊时，强烈建议提供field_type参数，以提高匹配准确性
    5. field_mapping.json中定义了标准字段名，是字段标准化的基础，标准格式就是name字段的值
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取原始返回值
            result = func(*args, **kwargs)

            # 如果返回值是字符串，进行标准化处理
            if isinstance(result, str):
                # 先标准化字段值，再转换为目标格式（如果需要）
                std_result = standardize_field(result, source, field_type)
                if target_source:
                    std_result = convert_field(std_result, target_source, field_type)

                return std_result

            # 如果返回值不是字符串，直接返回
            return result

        return cast(F, wrapper)

    return decorator


def standardize_param_dataframe_columns(
    param_ind: int = 0,
    param_name: Optional[str] = None,
    columns: Optional[Union[str, List[str]]] = None,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化输入参数中DataFrame列名的装饰器

    将函数输入参数中的DataFrame列名进行标准化处理。此装饰器适用于接收pandas DataFrame作为参数的函数，
    可以自动对输入DataFrame的列名进行格式转换和标准化，使函数内部可以使用统一的列名格式。
    DataFrame会保持DataFrame类型不变，只有列名会被修改。

    Args:
        param_ind (int):
            DataFrame参数在函数参数列表中的位置索引。
            - 默认值为0，表示第一个参数
            - 当函数有多个参数且DataFrame不是第一个参数时需要调整此值
            - 与param_name互斥，两者只需提供一个

        param_name (Optional[str]):
            DataFrame参数的名称。
            - 当函数使用关键字参数时更适合使用此参数
            - 与param_ind互斥，两者只需提供一个
            - 例如函数def process(df=None)中，param_name应为"df"

        columns (Optional[Union[str, List[str]]]):
            要标准化的列名，可以是单个字符串或字符串列表。
            - 当不提供时（None），将处理DataFrame中的所有列
            - 只有指定的列会被处理，其他列保持不变
            - 当只需要标准化特定列时使用，可提高处理效率

        source (Optional[str]):
            输入列名的数据源格式。
            - 当不提供时（None），假定输入已经是标准格式
            - 常见值："akshare", "tushare", "baostock", "joinquant", "rqdata"
            - 如果输入的DataFrame列名不是标准格式，则必须提供此参数

        target_source (Optional[str]):
            输出列名的目标数据源格式。
            - 当不提供时（None），输出将保持标准格式
            - 常见值同source参数
            - 当需要将标准列名转换为特定数据源格式时使用

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 例如："price", "volume", "return", "close_price"等
            - 当列名可能有歧义时，强烈建议提供此参数
            - 不提供时，将根据名称相似度进行匹配，可能不够准确
            - 所有列将使用相同的field_type进行匹配（如果列包含不同类型，请考虑单独处理）

    Returns:
        装饰后的函数，其接收的DataFrame参数的列名将被标准化

    使用场景:

    1. 基本用法 - 标准化输入DataFrame的所有列名:
       @standardize_param_dataframe_columns(source="akshare")
       def process_data(df):
           # 输入的df所有列名从akshare格式转换为标准格式
           # 例如："收盘" -> "close"
           # df仍然是DataFrame类型，只有列名被修改
           print(df.columns)  # 在函数内部可以直接使用标准化后的列名
           return df

    2. 指定参数位置 - 当DataFrame不是第一个参数:
       @standardize_param_dataframe_columns(param_ind=1, source="tushare")
       def calculate_returns(dates, price_df, benchmark=None):
           # price_df的列名从tushare格式转换为标准格式
           # price_df仍然是DataFrame类型，只有列名被修改
           return price_df["close"].pct_change()  # 可直接使用标准列名

    3. 使用参数名称 - 适用于关键字参数:
       @standardize_param_dataframe_columns(param_name="price_data", source="joinquant")
       def calculate_volatility(window=20, price_data=None):
           # 通过参数名定位DataFrame，列名从joinquant格式转换为标准格式
           # price_data仍然是DataFrame类型，只有列名被修改
           return price_data["close"].rolling(window).std()

    4. 只处理特定列 - 提高效率:
       @standardize_param_dataframe_columns(columns=["close", "open"], source="akshare")
       def calculate_gap(df):
           # 只处理close和open两列，其他列保持原样
           # df仍然是DataFrame类型，只有指定的列名被修改
           return df["open"] - df["close"].shift(1)  # 使用标准化后的列名

    5. 格式转换 - 将标准格式转换为特定格式:
       @standardize_param_dataframe_columns(target_source="joinquant")
       def prepare_for_backtest(df):
           # 输入的DataFrame列名假定已是标准格式，转换为joinquant格式
           # 例如："close" -> "close"
           # df仍然是DataFrame类型，只有列名被修改
           return df

    6. 完整转换链 - 在不同数据源格式之间转换:
       @standardize_param_dataframe_columns(source="tushare", target_source="joinquant")
       def convert_data_format(df):
           # DataFrame列名从tushare格式先转换为标准格式，再转换为joinquant格式
           # df仍然是DataFrame类型，只有列名被修改
           return df

    7. 组合使用多个参数:
       @standardize_param_dataframe_columns(
           param_name="price_df",
           columns=["close"],
           source="tushare",
           field_type="price"
       )
       def get_latest_close(price_df=None, date=None):
           # 只处理price_df中的close列，指定为价格类型，从tushare格式转换为标准格式
           # price_df仍然是DataFrame类型，只有指定的列名被修改
           return price_df["close"].iloc[-1]

    注意事项:
    1. param_ind和param_name是互斥的，不要同时提供两者
    2. 确保param_ind或param_name能正确定位到DataFrame参数，否则装饰器无法正常工作
    3. 当未指定columns参数时，会处理所有列，可能影响性能
    4. 所有列会使用相同的field_type和source/target_source参数进行处理
    5. 如果数据包含不同类型的列，考虑使用多个处理步骤或更通用的field_type
    6. 函数内部应使用处理后的列名，而不是原始列名
    7. DataFrame的数据内容不会被修改，只有列名会被标准化，DataFrame类型保持不变
    8. field_mapping.json中定义了标准字段名，是字段标准化的基础，标准格式就是name字段的值
    9. 必须安装pandas库才能使用此装饰器
    """
    # 处理单个列名或列名列表
    if isinstance(columns, str):
        columns = [columns]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not PANDAS_AVAILABLE:
                raise ImportError("处理DataFrame需要安装pandas库")

            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)
            param_key = None

            # 根据参数名确定DataFrame参数
            if param_name is not None and param_name in bound_args.arguments:
                param_key = param_name
            # 或者根据位置索引确定DataFrame参数
            elif param_ind < len(args):
                param_keys = list(sig.parameters.keys())
                if param_ind < len(param_keys):
                    param_key = param_keys[param_ind]

            # 如果找到DataFrame参数并且是DataFrame类型
            if param_key and param_key in bound_args.arguments:
                df = bound_args.arguments[param_key]
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # 确定要处理的列
                    cols_to_process = columns if columns else df.columns.tolist()
                    # 只处理DataFrame中实际存在的列
                    cols_to_process = [
                        col for col in cols_to_process if col in df.columns
                    ]

                    # 创建新的列名映射
                    rename_map = {}
                    for col in cols_to_process:
                        # 标准化列名，再转换为目标格式（如果需要）
                        std_col = standardize_field(col, source, field_type)
                        if target_source:
                            std_col = convert_field(std_col, target_source, field_type)
                        rename_map[col] = std_col

                    # 重命名DataFrame列
                    if rename_map:
                        df = df.rename(columns=rename_map)
                        bound_args.arguments[param_key] = df

                        # 更新位置参数和关键字参数
                        new_args = []
                        for p_name in sig.parameters:
                            if p_name in bound_args.arguments:
                                if len(new_args) < len(args) and list(
                                    sig.parameters.keys()
                                ).index(p_name) < len(args):
                                    new_args.append(bound_args.arguments[p_name])
                                else:
                                    kwargs[p_name] = bound_args.arguments[p_name]

                        # 如果有位置参数，使用更新后的位置参数
                        if new_args:
                            args = tuple(new_args)

            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def standardize_result_dataframe_columns(
    columns: Optional[Union[str, List[str]]] = None,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    field_type: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化返回的DataFrame列名装饰器

    将函数返回的DataFrame的列名进行标准化处理。此装饰器适用于返回pandas DataFrame的函数，
    可以自动对返回DataFrame的列名进行格式转换和标准化。装饰后的函数仍返回DataFrame，只是列名被标准化。

    Args:
        columns (Optional[Union[str, List[str]]]):
            要标准化的列名，可以是单个字符串或字符串列表。
            - 当不提供时（None），将处理DataFrame中的所有列
            - 只有指定的列会被处理，其他列保持不变
            - 当只需要标准化特定列时使用，可提高处理效率

        source (Optional[str]):
            输入列名的数据源格式。
            - 当不提供时（None），假定输入已经是标准格式
            - 常见值："akshare", "tushare", "baostock", "joinquant", "rqdata"
            - 如果返回的DataFrame列名不是标准格式，则必须提供此参数

        target_source (Optional[str]):
            输出列名的目标数据源格式。
            - 当不提供时（None），输出将保持标准格式
            - 常见值同source参数
            - 当需要将标准列名转换为特定数据源格式时使用

        field_type (Optional[str]):
            字段类型，用于提高字段匹配的准确性。
            - 例如："price", "volume", "return", "close_price"等
            - 当列名可能有歧义时，强烈建议提供此参数
            - 不提供时，将根据名称相似度进行匹配，可能不够准确
            - 所有列将使用相同的field_type进行匹配（如果列包含不同类型，请考虑单独处理）

    Returns:
        装饰后的函数，其返回的DataFrame列名将被标准化，返回类型仍是DataFrame

    使用场景:

    1. 基本用法 - 标准化返回DataFrame的所有列名:
       @standardize_result_dataframe_columns(source="akshare")
       def get_price_data():
           # 返回的DataFrame所有列名从akshare格式转换为标准格式
           df = pd.DataFrame({"收盘": [100, 101], "开盘": [99, 100]})
           return df
           # 返回值仍为DataFrame类型，但列名会变为:
           # df.columns = ["close", "open"]

    2. 只处理特定列 - 提高效率:
       @standardize_result_dataframe_columns(columns=["收盘", "开盘"], source="akshare")
       def get_market_data():
           # 只处理收盘和开盘两列，其他列保持原样
           df = pd.DataFrame({
               "收盘": [100, 101],
               "开盘": [99, 100],
               "code": ["000001", "000002"]  # 这列不会被处理
           })
           return df
           # 返回值仍为DataFrame类型，但列名会变为:
           # df.columns = ["close", "open", "code"]

    3. 将标准格式转换为特定数据源格式:
       @standardize_result_dataframe_columns(target_source="tushare")
       def get_standardized_data():
           # 假设函数返回的DataFrame列名已经是标准格式，将被转换为tushare格式
           df = pd.DataFrame({"close": [100, 101], "open": [99, 100]})
           return df
           # 返回值仍为DataFrame类型，列名根据tushare格式映射而变化

    4. 完整转换链 - 跨平台数据转换:
       @standardize_result_dataframe_columns(source="akshare", target_source="baostock")
       def convert_data_format():
           # DataFrame列名从akshare格式先转换为标准格式，再转换为baostock格式
           df = pd.DataFrame({"收盘": [100, 101], "开盘": [99, 100]})
           return df
           # 返回值仍为DataFrame类型，列名经过两次转换

    5. 指定字段类型提高匹配准确性:
       @standardize_result_dataframe_columns(source="akshare", field_type="price")
       def get_price_data():
           # 明确指定所有列都是价格类型字段，提高匹配准确性
           df = pd.DataFrame({"close": [100, 101], "open": [99, 100]})
           return df
           # 返回值仍为DataFrame类型，列名匹配会更准确

    6. 组合使用多个参数:
       @standardize_result_dataframe_columns(
           columns=["收盘"],
           source="akshare",
           target_source="baostock",
           field_type="price"
       )
       def get_closing_prices():
           # 只处理收盘列，指定为价格类型，从akshare格式转换为baostock格式
           df = pd.DataFrame({"收盘": [100, 101], "成交量": [10000, 12000]})
           return df
           # 返回值仍为DataFrame类型，只有"收盘"列名被修改

    注意事项:
    1. 此装饰器只适用于返回pandas DataFrame的函数，并且不会改变返回类型，仍然是DataFrame
    2. 如果函数返回值不是DataFrame，将直接返回原结果不做任何处理
    3. 当未指定columns参数时，会处理所有列，可能影响性能
    4. 所有列会使用相同的field_type和source/target_source参数进行处理
    5. 如果数据包含不同类型的列，考虑使用多个处理步骤或更通用的field_type
    6. DataFrame的数据内容不会被修改，只有列名会被标准化
    7. field_mapping.json中定义了标准字段名，是字段标准化的基础，标准格式就是name字段的值
    8. 必须安装pandas库才能使用此装饰器
    """
    return standardize_field_values(
        source=source,
        target_source=target_source,
        field_type=field_type,
        df_result=True,
        df_columns=columns,
    )
