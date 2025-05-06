#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""证券代码标准化装饰器模块

提供用于标准化证券代码的装饰器。
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast, TypeVar

from .interface import standardize_code, to_source_code

# 尝试导入pandas，但不强制要求
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

F = TypeVar("F", bound=Callable[..., Any])


def standardize_stock_codes(
    source: Optional[str] = None,
    target_source: Optional[str] = None,
    target_params: Optional[Union[str, List[str]]] = None,
    result_key: Optional[str] = None,
    df_columns: Optional[Union[str, List[str]]] = None,
    df_param: Optional[str] = None,
    df_result: bool = False,
) -> Callable[[F], F]:
    """证券代码标准化装饰器

    将函数参数值或返回值中的证券代码标准化。

    参数配合关系说明:

    1. source和target_source参数:
       - source=None: 表示输入的证券代码已是标准格式（如'600000.SH'），无需转换为标准格式
       - target_source=None: 表示输出保持标准格式，不转换为特定数据源格式
       - 若同时设置source和target_source: 将从source格式先转为标准格式，再转为target_source格式
       - 数据源名称需为有效值，如: 'tushare', 'baostock', 'akshare', 'joinquant', 'rqdata'等

    2. 处理位置参数说明（至少设置以下四组参数中的一组，否则装饰器无效）:
       - target_params: 标准化函数参数的值，target_params=None时不处理任何参数
       - result_key: 标准化返回值字典或对象中的指定字段，result_key=None时不处理返回值的字段
       - df_param: 处理DataFrame参数，df_param=None时不处理DataFrame参数
       - df_result: 处理返回的DataFrame，df_result=False时不处理返回的DataFrame

    3. df_columns参数:
       - df_columns=None: 处理所有列（可能会降低效率）
       - df_columns设为特定列: 只处理DataFrame中的指定列（推荐设置以提高效率）
       - 只有当df_param不为None或df_result为True时，df_columns参数才有效

    用法示例:

    1. 标准化指定参数的值:
    @standardize_stock_codes(source="akshare", target_params=["stock_code", "index_code"])
    def get_data(stock_code="600000", index_code="000001", ...):
        # stock_code和index_code的值会被自动从akshare格式标准化为XXXX.XX格式
        # 例如，如果传入stock_code="600000"，会被标准化为"600000.SH"
        pass

    2. 标准化函数返回值的特定字段值:
    @standardize_stock_codes(target_source="joinquant", result_key="code")
    def get_stock():
        # 返回结果中的code字段值会被转换为聚宽格式
        # 例如 {"code": "600000.SH"} 将被转换为 {"code": "600000.XSHG"}
        return {"code": "600000.SH", ...}

    3. 标准化DataFrame参数的股票代码列:
    @standardize_stock_codes(source="akshare", df_param="data", df_columns=["code", "symbol"])
    def process_data(data: pd.DataFrame):
        # 传入的DataFrame中指定的列将被标准化为统一的证券代码格式
        # 例如，列"code"中的值"600000"会被标准化为"600000.SH"
        pass

    4. 标准化返回的DataFrame中的股票代码列:
    @standardize_stock_codes(target_source="joinquant", df_result=True, df_columns=["code"])
    def get_data() -> pd.DataFrame:
        # 返回的DataFrame中的"code"列的值会被转换为聚宽格式
        # 例如"600000.SH"将被转换为"600000.XSHG"
        return df

    5. 组合使用多个功能:
    @standardize_stock_codes(
        source="akshare",
        target_source="tushare",
        target_params=["stock_code"],
        result_key="result_code",
        df_param="input_df",
        df_result=True,
        df_columns=["code"]
    )
    def complex_func(stock_code, input_df):
        # 同时标准化单个参数、DataFrame参数和返回值
        return {"result_code": stock_code, "dataframe": input_df}

    Args:
        source: 源数据格式，可选值: tushare, baostock, akshare, joinquant, rqdata
               如果为None，将假设输入已是标准格式（如'600000.SH'）
        target_source: 目标数据格式，如果为None，将保持标准格式不转换
                      如果提供，将把标准化后的代码转换为该格式
        target_params: 要标准化值的参数名称，可以是单个字符串或字符串列表
                      如果为None，不处理任何参数
        result_key: 要标准化值的返回值字段，如果返回值是字典或对象
                   如果为None，不处理返回值中的任何字段
        df_columns: 要处理的DataFrame列名，可以是单个字符串或字符串列表
                   如果为None则处理所有列（可能降低效率）
                   只有当df_param不为None或df_result为True时有效
        df_param: 包含DataFrame的参数名称
                 如果为None，不处理任何DataFrame参数
        df_result: 是否处理返回的DataFrame
                  默认为False，设为True时会处理返回的DataFrame

    Returns:
        装饰后的函数

    注意事项:
    1. target_params, result_key, df_param, df_result至少要提供一个，否则装饰器不会有任何作用
    2. 转换过程是两步的: 先将输入转换为标准格式，再从标准格式转换为目标格式(如果指定target_source)
    3. 处理DataFrame时需要安装pandas库，否则会抛出ImportError
    4. DataFrame中只有指定列才会被处理，未指定的列保持不变
    5. 如果代码无法识别或无法转换，将保持原样不变
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
                            # 添加调试信息
                            try:
                                # 先标准化参数值，再转换为目标格式（如果需要）
                                # 不捕获异常，确保ValueError被正确传递给调用者
                                std_value = standardize_code(param_value, source)
                                if target_source:
                                    std_value = to_source_code(std_value, target_source)
                                bound_args.arguments[param_name] = std_value
                            except Exception as e:
                                raise  # 重新抛出异常

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

                        # 标准化每一列中的股票代码
                        for col in cols_to_process:
                            if col in df.columns:
                                # 逐行处理股票代码
                                df[col] = df[col].apply(
                                    lambda x: (
                                        to_source_code(
                                            standardize_code(x, source), target_source
                                        )
                                        if pd.notna(x)
                                        else x
                                    )
                                )

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
                        std_value = standardize_code(result[result_key], source)
                        if target_source:
                            std_value = to_source_code(std_value, target_source)
                        result[result_key] = std_value
                elif hasattr(result, result_key):
                    # 如果返回的是对象且有该属性
                    attr_value = getattr(result, result_key)
                    if attr_value is not None:
                        # 先标准化字段值，再转换为目标格式（如果需要）
                        std_value = standardize_code(attr_value, source)
                        if target_source:
                            std_value = to_source_code(std_value, target_source)
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

                # 标准化每一列中的股票代码
                for col in cols_to_process:
                    if col in result.columns:
                        # 逐行处理股票代码
                        result[col] = result[col].apply(
                            lambda x: (
                                to_source_code(
                                    standardize_code(x, source), target_source
                                )
                                if pd.notna(x)
                                else x
                            )
                        )

            return result

        return cast(F, wrapper)

    return decorator


def standardize_param_stock_code(
    param_name: str, source: Optional[str] = None, target_source: Optional[str] = None
) -> Callable[[F], F]:
    """标准化参数证券代码装饰器

    将函数中指定参数的证券代码值标准化。这是standardize_stock_codes的简化版本，
    专门用于处理单个参数的场景。

    参数配合关系说明:
    - param_name: 必需参数，指定要处理的参数名
    - source=None: 表示输入的证券代码已是标准格式，无需转换为标准格式
    - target_source=None: 表示输出保持标准格式，不转换为特定数据源格式

    Args:
        param_name: 参数名称，其值将被标准化
        source: 输入代码值的数据源格式，None表示输入已是标准格式
        target_source: 输出代码值的数据源格式，None表示保持标准格式

    Returns:
        装饰后的函数

    Example:
        @standardize_param_stock_code("code", source="akshare", target_source="tushare")
        def process_stock(code="600000"):
            # 如果code="600000"，它将被从akshare格式转换为tushare格式的对应代码
            # 例如从"600000"转换为"600000.SH"
            pass

        @standardize_param_stock_code("code", source="akshare")
        def get_standard_code(code="600000"):
            # 从akshare格式转换为标准格式，但不转换为其他格式
            # code="600000" 将变为 "600000.SH"
            pass

        @standardize_param_stock_code("code", target_source="joinquant")
        def convert_code(code="600000.SH"):
            # 输入假定已是标准格式，转换为joinquant格式
            # code="600000.SH" 将变为 "600000.XSHG"
            pass
    """
    return standardize_stock_codes(
        source=source, target_source=target_source, target_params=param_name
    )


def standardize_param_stock_codes(
    param_name: str, source: Optional[str] = None, target_source: Optional[str] = None
) -> Callable[[F], F]:
    """标准化参数证券代码列表装饰器

    将函数中指定的证券代码列表参数中的每个代码值标准化。适用于参数值是
    证券代码列表的场景，会对列表中的每个元素进行标准化处理。

    参数配合关系说明:
    - param_name: 必需参数，指定包含代码列表的参数名
    - source=None: 表示列表中的证券代码已是标准格式，无需转换为标准格式
    - target_source=None: 表示输出保持标准格式，不转换为特定数据源格式

    Args:
        param_name: 包含代码列表的参数名称
        source: 输入代码值的数据源格式，None表示输入已是标准格式
        target_source: 输出代码值的数据源格式，None表示保持标准格式

    Returns:
        装饰后的函数

    Example:
        @standardize_param_stock_codes("codes", source="akshare", target_source="joinquant")
        def process_stocks(codes=["600000", "000001"]):
            # codes中的每个代码值会从akshare格式转换为joinquant格式
            # 例如 ["600000", "000001"] 将被转换为 ["600000.XSHG", "000001.XSHE"]
            pass

        @standardize_param_stock_codes("codes", source="akshare")
        def get_standard_codes(codes=["600000", "000001"]):
            # 只转换为标准格式，不转换为其他格式
            # ["600000", "000001"] 将变为 ["600000.SH", "000001.SZ"]
            pass

    注意事项:
    1. 列表中的None值会被保留，不会进行标准化处理
    2. 如果列表中某个代码无法识别或无法转换，将保持原样不变
    3. 输入列表将得到标准化后的新列表，列表结构保持不变
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数签名
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)

            # 处理代码列表参数
            if param_name in bound_args.arguments:
                codes_list = bound_args.arguments[param_name]
                if codes_list is not None:
                    # 标准化列表中的每个代码值
                    if isinstance(codes_list, list):
                        std_codes = []
                        for code in codes_list:
                            if code is not None:
                                # 先标准化代码值，再转换为目标格式（如果需要）
                                std_code = standardize_code(code, source)
                                if target_source:
                                    std_code = to_source_code(std_code, target_source)
                                std_codes.append(std_code)
                            else:
                                std_codes.append(None)

                        # 更新参数值
                        bound_args.arguments[param_name] = std_codes

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


def standardize_result_stock_code(
    result_key: str, source: Optional[str] = None, target_source: Optional[str] = None
) -> Callable[[F], F]:
    """标准化返回结果证券代码装饰器

    将函数返回值中特定字段的证券代码值标准化。适用于返回字典或对象的函数，
    会对返回结果中特定键的值进行标准化处理。

    参数配合关系说明:
    - result_key: 必需参数，指定返回结果中要处理的键名
    - source=None: 表示返回值中的证券代码已是标准格式，无需转换为标准格式
    - target_source=None: 表示输出保持标准格式，不转换为特定数据源格式

    Args:
        result_key: 返回结果中要标准化值的键名
        source: 返回代码值的原始数据源格式，None表示返回值已是标准格式
        target_source: 返回代码值的目标数据源格式，None表示保持标准格式

    Returns:
        装饰后的函数

    Example:
        @standardize_result_stock_code("stock_code", target_source="baostock")
        def get_stock():
            # 返回结果中的stock_code字段值将被转换为baostock格式
            # 例如 {"stock_code": "600000.SH"} 将被转换为 {"stock_code": "sh.600000"}
            return {"stock_code": "600000.SH", ...}

        @standardize_result_stock_code("stock_code", source="akshare")
        def get_standard_stock():
            # 从akshare格式转换为标准格式
            # {"stock_code": "600000"} 将变为 {"stock_code": "600000.SH"}
            return {"stock_code": "600000", ...}

    注意事项:
    1. 此装饰器只适用于返回字典或带属性的对象的函数
    2. 如果返回值不是字典或对象，或者指定的键不存在，函数将不做任何处理直接返回原结果
    3. 只有指定键的值会被处理，其他键的值保持不变
    """
    return standardize_stock_codes(
        source=source, target_source=target_source, result_key=result_key
    )


def standardize_param_dataframe_stock_codes(
    param_name: str,
    columns: Optional[Union[str, List[str]]] = None,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化DataFrame股票代码装饰器

    将函数中DataFrame参数中的股票代码列标准化。适用于参数是pandas DataFrame的函数，
    会对DataFrame中的特定列进行标准化处理。

    参数配合关系说明:
    - param_name: 必需参数，指定包含DataFrame的参数名
    - columns=None: 处理DataFrame中的所有列（可能降低效率）
    - columns指定特定列: 只处理DataFrame中的指定列（推荐以提高效率）
    - source=None: 表示DataFrame中的证券代码已是标准格式，无需转换为标准格式
    - target_source=None: 表示输出保持标准格式，不转换为特定数据源格式

    Args:
        param_name: 包含DataFrame的参数名称
        columns: 包含股票代码的列名，可以是单个字符串或字符串列表
                如果为None则处理所有列（可能降低效率）
        source: 输入代码的数据源格式，None表示输入已是标准格式
        target_source: 输出代码的数据源格式，None表示保持标准格式

    Returns:
        装饰后的函数

    Example:
        @standardize_param_dataframe_stock_codes("df", columns=["code", "symbol"], source="akshare", target_source="tushare")
        def process_data(df: pd.DataFrame):
            # df中"code"和"symbol"列的所有股票代码会从akshare格式转换为tushare格式
            # 例如"600000"将变为"600000.SH"
            pass

        @standardize_param_dataframe_stock_codes("df", columns=["code"], source="akshare")
        def process_data(df: pd.DataFrame):
            # 只处理"code"列，只转换为标准格式
            # "600000"将变为"600000.SH"
            pass

    注意事项:
    1. 此装饰器需要安装pandas库，否则会抛出ImportError
    2. 只有指定列会被处理，DataFrame中的其他列保持不变
    3. 如果指定列不存在于DataFrame中，该列会被忽略
    4. DataFrame中的NaN值会被保留，不进行标准化处理
    """
    return standardize_stock_codes(
        source=source,
        target_source=target_source,
        df_param=param_name,
        df_columns=columns,
    )


def standardize_result_dataframe_stock_codes(
    columns: Optional[Union[str, List[str]]] = None,
    source: Optional[str] = None,
    target_source: Optional[str] = None,
) -> Callable[[F], F]:
    """标准化返回的DataFrame股票代码装饰器

    将函数返回的DataFrame中的股票代码列标准化。适用于返回pandas DataFrame的函数，
    会对返回的DataFrame中的特定列进行标准化处理。

    参数配合关系说明:
    - columns=None: 处理DataFrame中的所有列（可能降低效率）
    - columns指定特定列: 只处理DataFrame中的指定列（推荐以提高效率）
    - source=None: 表示DataFrame中的证券代码已是标准格式，无需转换为标准格式
    - target_source=None: 表示输出保持标准格式，不转换为特定数据源格式

    Args:
        columns: 包含股票代码的列名，可以是单个字符串或字符串列表
                如果为None则处理所有列（可能降低效率）
        source: 返回代码的原始数据源格式，None表示返回值已是标准格式
        target_source: 返回代码的目标数据源格式，None表示保持标准格式

    Returns:
        装饰后的函数

    Example:
        @standardize_result_dataframe_stock_codes(columns=["code"], target_source="joinquant")
        def get_stocks() -> pd.DataFrame:
            # 返回的DataFrame中"code"列的股票代码将被转换为聚宽格式
            # 例如"600000.SH"将变为"600000.XSHG"
            return df

        @standardize_result_dataframe_stock_codes(columns=["code", "index_code"], source="akshare")
        def get_akshare_data() -> pd.DataFrame:
            # 将"code"和"index_code"列从akshare格式转换为标准格式
            # 例如"600000"将变为"600000.SH"
            return df

    注意事项:
    1. 此装饰器需要安装pandas库，否则会抛出ImportError
    2. 只有指定列会被处理，DataFrame中的其他列保持不变
    3. 如果函数返回值不是DataFrame，将不做任何处理直接返回原结果
    4. 如果指定列不存在于DataFrame中，该列会被忽略
    5. DataFrame中的NaN值会被保留，不进行标准化处理
    """
    return standardize_stock_codes(
        source=source, target_source=target_source, df_result=True, df_columns=columns
    )


def direct_standardize_check(code: str, source: Optional[str] = None) -> str:
    """
    直接检查证券代码格式，用于测试无效代码时确保异常被抛出

    与standardize_code的区别是此函数不会捕获异常

    Args:
        code: 原始证券代码
        source: 数据源名称

    Returns:
        str: 标准化后的证券代码

    Raises:
        ValueError: 当代码格式无效时抛出
    """
    from .interface import standardize_code

    # 直接将参数传递给standardize_code并让异常向上传播
    return standardize_code(code, source)
