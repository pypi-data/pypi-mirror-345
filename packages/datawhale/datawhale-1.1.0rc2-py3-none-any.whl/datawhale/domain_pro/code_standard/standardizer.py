#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from typing import Optional, Dict, List, Pattern, Tuple


class StockCodeStandardizer:
    """证券代码标准化工具类

    将不同数据源的证券代码转换为标准格式 (600000.SH)
    支持的数据源:
    - tushare: 600000.SH, 000001.SZ
    - baostock: sh.600000, sz.000001
    - akshare: 600000, 000001
    - 聚宽(joinquant): 600000.XSHG, 000001.XSHE
    - 米筐(RQData): 600000.XSHG, 000001.XSHE
    """

    # 交易所映射
    EXCHANGES = {
        # 上交所
        "SH": ["XSHG", "SSE", "SHSE", "SH"],
        # 深交所
        "SZ": ["XSHE", "SZSE", "SZ"],
        # 北交所
        "BJ": ["BSE", "BJ"],
        # 港交所
        "HK": ["XHKG", "HK"],
        # 开放式基金
        "OF": ["OF", "F"],
    }

    # 反向交易所映射
    EXCHANGE_REVERSE_MAP = {}
    for std_exchange, aliases in EXCHANGES.items():
        for alias in aliases:
            EXCHANGE_REVERSE_MAP[alias.upper()] = std_exchange

    # 各数据源的代码格式
    SOURCE_FORMATS = {
        "tushare": r"^(\d{6})\.([A-Z]{2})$",  # 600000.SH
        "baostock": r"^([a-z]{2})\.(\d{6})$",  # sh.600000
        "akshare": r"^(\d{6})$",  # 600000
        "joinquant": r"^(\d{6})\.([A-Z]{4})$",  # 600000.XSHG
        "rqdata": r"^(\d{6})\.([A-Z]{4})$",  # 600000.XSHG
    }

    # 股票代码前缀到交易所的映射
    CODE_PREFIX_EXCHANGES = {
        # 上交所
        "60": "SH",  # 主板
        "688": "SH",  # 科创板
        "689": "SH",  # 科创板存托凭证
        "900": "SH",  # B股
        # 深交所
        "00": "SZ",  # 主板
        "002": "SZ",  # 中小板
        "003": "SZ",  # 主板
        "004": "SZ",  # 主板
        "300": "SZ",  # 创业板
        "301": "SZ",  # 创业板
        "200": "SZ",  # B股
        # 北交所
        "83": "BJ",  # 北交所
        "87": "BJ",  # 北交所
        "88": "BJ",  # 北交所
        "430": "BJ",  # 北交所
        "82": "BJ",  # 北交所
        "889": "BJ",  # 北交所
    }

    # 指数代码映射
    INDEX_CODE_MAP = {
        # 上证指数
        "000001": "SH",
        # 深证成指
        "399001": "SZ",
        # 沪深300
        "000300": "SH",
        "399300": "SZ",
        # 上证50
        "000016": "SH",
        # 中证500
        "000905": "SH",
        # 创业板指
        "399006": "SZ",
        # 科创50
        "000688": "SH",
        # 北证50
        "899050": "BJ",
    }

    # 特殊产品代码映射
    SPECIAL_PRODUCTS = {
        # ETF基金
        "51": "SH",
        "159": "SZ",
        "56": "SH",
        "58": "SH",
        "501": "SH",  # 场内基金
        "502": "SH",  # 分级基金
        "150": "SZ",  # 分级基金
        "16": "SZ",  # LOF基金
        # 债券
        "11": "SH",  # 可转债
        "12": "SZ",  # 可转债
        "113": "SH",  # 可转债
        "123": "SZ",  # 可转债
        "127": "SZ",  # 可转债
        "128": "SZ",  # 可转债
        "110": "SH",  # 可转债
        # 期权
        "10": "SH",
        # 国债
        "01": "SH",
        "02": "SH",
        "019": "SH",  # 国债
        "10": "SH",  # 国债
        # 开放式基金
        "00": "OF",  # 开放式基金
        "16": "OF",  # 开放式基金
        # 期货
        "IF": "CFE",  # 股指期货
        "IC": "CFE",  # 股指期货
        "IH": "CFE",  # 股指期货
        "T": "CFE",  # 国债期货
        "TF": "CFE",  # 国债期货
        "TS": "CFE",  # 国债期货
    }

    # 不同数据源对于000开头代码的默认交易所映射
    SOURCE_000_DEFAULT = {
        "akshare": "SZ",  # akshare默认000开头为深交所股票
        "joinquant": "SZ",  # 聚宽默认000开头为深交所股票
        "rqdata": "SZ",  # 米筐默认000开头为深交所股票
        "baostock": "SZ",  # baostock默认000开头为深交所股票
        "of": "OF",  # of默认为开放式基金
    }

    # 正则表达式缓存
    _PATTERN_CACHE: Dict[str, Pattern] = {}

    @classmethod
    def _get_pattern(cls, pattern: str) -> Pattern:
        """获取或创建正则表达式模式

        Args:
            pattern: 正则表达式字符串

        Returns:
            Pattern: 编译后的正则表达式模式
        """
        if pattern not in cls._PATTERN_CACHE:
            cls._PATTERN_CACHE[pattern] = re.compile(pattern)
        return cls._PATTERN_CACHE[pattern]

    @classmethod
    def standardize(cls, code: str, source: Optional[str] = None) -> str:
        """将不同格式的证券代码标准化为统一格式

        Args:
            code: 原始证券代码
            source: 数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata
                   如不提供，则自动检测

        Returns:
            str: 标准化后的证券代码，格式为[数字代码].[交易所代码]，如600000.SH

        Raises:
            ValueError: 当代码格式无效或无法判断交易所时抛出
        """
        if not code:
            raise ValueError("证券代码不能为空")

        # 判断输入类型
        if not isinstance(code, str):
            raise ValueError(f"证券代码必须是字符串类型，实际类型为: {type(code)}")

        # 移除空白字符并转为大写
        code = code.strip().upper()

        # 快速检查：有效证券代码应至少包含数字部分
        if not re.search(r"\d+", code):
            raise ValueError(f"无效的证券代码格式: {code}，证券代码应至少包含数字部分")

        # 特殊处理：如果是纯数字000开头的代码且指定了数据源
        if (
            code.isdigit()
            and code.startswith("000")
            and source
            and source.lower() in cls.SOURCE_000_DEFAULT
        ):
            numeric_code = code
            exchange = cls.SOURCE_000_DEFAULT[source.lower()]
            return f"{numeric_code}.{exchange}"

        try:
            # 尝试提取数字代码和交易所信息
            numeric_code, exchange = cls._parse_code(code, source)

            # 验证结果的有效性
            if not (numeric_code and exchange):
                raise ValueError(f"无法从证券代码提取有效的数字部分和交易所: {code}")

            # 验证数字部分格式
            if not re.match(r"^\d{6}$", numeric_code):
                raise ValueError(f"无效的证券代码数字部分: {numeric_code}，应为6位数字")

            # 验证交易所格式
            valid_exchanges = set()
            for exchanges in cls.EXCHANGES.values():
                valid_exchanges.update(exchanges)
            valid_exchanges.update(cls.EXCHANGES.keys())

            if exchange not in valid_exchanges and exchange not in ["CFE", "OF"]:
                raise ValueError(f"无效的交易所代码: {exchange}")

            # 返回标准格式
            return f"{numeric_code}.{exchange}"

        except ValueError as e:
            # 重新抛出异常，确保错误信息包含原始代码
            raise ValueError(f"无法标准化证券代码 '{code}': {str(e)}")

    @classmethod
    def _parse_code(cls, code: str, source: Optional[str] = None) -> Tuple[str, str]:
        """解析证券代码，提取数字代码和交易所信息

        Args:
            code: 原始证券代码
            source: 数据源名称

        Returns:
            Tuple[str, str]: (数字代码, 交易所代码)

        Raises:
            ValueError: 当代码格式无效或无法判断交易所时抛出
        """
        # 快速检查：明显无效的代码
        if not code or len(code) < 2:
            raise ValueError(f"证券代码太短: {code}")

        # 检查是否包含无效字符
        if re.search(r"[^A-Z0-9\.]", code):
            raise ValueError(f"证券代码包含无效字符: {code}")

        # 如果已经是标准格式，直接返回
        std_pattern = cls._get_pattern(r"^(\d{6})\.([A-Z]{2,4})$")
        std_match = std_pattern.match(code)
        if std_match:
            numeric_code, exchange = std_match.groups()
            if exchange in cls.EXCHANGE_REVERSE_MAP:
                exchange = cls.EXCHANGE_REVERSE_MAP[exchange]
            return numeric_code, exchange

        # 特殊处理: akshare和joinquant的000开头代码默认为深交所
        if code.isdigit() and code.startswith("000") and source:
            if source.lower() in cls.SOURCE_000_DEFAULT:
                return code, cls.SOURCE_000_DEFAULT[source.lower()]

        # 如果知道数据源，使用特定格式解析
        if source and source.lower() in cls.SOURCE_FORMATS:
            source_pattern = cls._get_pattern(cls.SOURCE_FORMATS[source.lower()])
            source_match = source_pattern.match(code)

            if source_match:
                if source.lower() == "baostock":
                    exchange_code, numeric_code = source_match.groups()
                    exchange = exchange_code.upper()
                    if exchange in cls.EXCHANGE_REVERSE_MAP:
                        exchange = cls.EXCHANGE_REVERSE_MAP[exchange]
                elif source.lower() == "akshare":
                    numeric_code = source_match.group(1)
                    # 特殊处理：akshare的000开头代码默认为深交所股票
                    if numeric_code.startswith("000"):
                        exchange = "SZ"
                    else:
                        exchange = cls._infer_exchange_by_code(
                            numeric_code, source=source.lower()
                        )
                else:
                    numeric_code, exchange_code = source_match.groups()
                    if exchange_code in cls.EXCHANGE_REVERSE_MAP:
                        exchange = cls.EXCHANGE_REVERSE_MAP[exchange_code]
                    else:
                        exchange = exchange_code
                return numeric_code, exchange

        # 尝试自动检测格式
        for fmt_name, fmt_pattern in cls.SOURCE_FORMATS.items():
            pattern = cls._get_pattern(fmt_pattern)
            match = pattern.match(code)
            if match:
                if fmt_name == "baostock":
                    exchange_code, numeric_code = match.groups()
                    if exchange_code.upper() in cls.EXCHANGE_REVERSE_MAP:
                        exchange = cls.EXCHANGE_REVERSE_MAP[exchange_code.upper()]
                    else:
                        exchange = exchange_code.upper()
                elif fmt_name == "akshare":
                    numeric_code = match.group(1)
                    # 特殊处理：akshare的000开头代码默认为深交所股票
                    if numeric_code.startswith("000"):
                        exchange = "SZ"
                    else:
                        exchange = cls._infer_exchange_by_code(
                            numeric_code, source=fmt_name
                        )
                else:
                    numeric_code, exchange_code = match.groups()
                    if exchange_code in cls.EXCHANGE_REVERSE_MAP:
                        exchange = cls.EXCHANGE_REVERSE_MAP[exchange_code]
                    else:
                        exchange = exchange_code
                return numeric_code, exchange

        # 处理纯数字代码
        if code.isdigit() and len(code) == 6:
            numeric_code = code
            try:
                exchange = cls._infer_exchange_by_code(numeric_code, source=source)
            except ValueError:
                # 如果指定了数据源且是000开头的代码，使用数据源默认映射
                if (
                    source
                    and source.lower() in cls.SOURCE_000_DEFAULT
                    and numeric_code.startswith("000")
                ):
                    exchange = cls.SOURCE_000_DEFAULT[source.lower()]
                else:
                    raise
            return numeric_code, exchange

        # 处理其他格式 - 更严格：必须包含有效的6位数字代码
        numeric_pattern = re.compile(r"\d{6}")
        numeric_match = numeric_pattern.search(code)
        if numeric_match:
            numeric_code = numeric_match.group()
            non_numeric_parts = code.replace(numeric_code, "").replace(".", "").strip()

            if non_numeric_parts:
                if non_numeric_parts.upper() in cls.EXCHANGE_REVERSE_MAP:
                    exchange = cls.EXCHANGE_REVERSE_MAP[non_numeric_parts.upper()]
                else:
                    exchange = non_numeric_parts.upper()
            else:
                try:
                    exchange = cls._infer_exchange_by_code(numeric_code, source=source)
                except ValueError:
                    # 如果指定了数据源且是000开头的代码，使用数据源默认映射
                    if (
                        source
                        and source.lower() in cls.SOURCE_000_DEFAULT
                        and numeric_code.startswith("000")
                    ):
                        exchange = cls.SOURCE_000_DEFAULT[source.lower()]
                    else:
                        raise

            return numeric_code, exchange

        # 处理开放式基金特殊格式
        of_pattern = re.compile(r"([a-zA-Z0-9]{6})(OF|of|F|f)?")
        of_match = of_pattern.match(code)
        if of_match and (of_match.group(2) or source == "of"):
            fund_code = of_match.group(1)
            return fund_code, "OF"

        # 如果所有匹配规则都失败，抛出错误
        raise ValueError(f"无法解析证券代码: {code}")

    @classmethod
    def _infer_exchange_by_code(cls, code: str, source: Optional[str] = None) -> str:
        """根据证券代码的数字部分推断交易所

        Args:
            code: 证券代码的数字部分
            source: 数据源名称

        Returns:
            str: 交易所代码

        Raises:
            ValueError: 当无法确定交易所时抛出
        """
        # 检查特定指数
        if code in cls.INDEX_CODE_MAP:
            return cls.INDEX_CODE_MAP[code]

        # 检查股票代码前缀
        for prefix, exchange in sorted(
            cls.CODE_PREFIX_EXCHANGES.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if code.startswith(prefix):
                return exchange

        # 检查特殊产品代码
        for prefix, exchange in cls.SPECIAL_PRODUCTS.items():
            if code.startswith(prefix):
                return exchange

        # 处理000开头的特殊情况 (可能是上交所指数或深交所股票)
        if code.startswith("000"):
            # 如果有指定数据源，使用数据源默认处理
            if source and source.lower() in cls.SOURCE_000_DEFAULT:
                return cls.SOURCE_000_DEFAULT[source.lower()]
            # 否则需要明确指定交易所
            raise ValueError(
                f"000开头的证券代码 {code} 需要提供交易所标识(SH或SZ)以区分上交所指数和深交所股票"
            )

        raise ValueError(f"无法确定证券代码 {code} 的交易所")

    @classmethod
    def to_source_format(cls, code: str, target_source: str) -> str:
        """将标准格式代码转换为指定数据源的格式

        Args:
            code: 标准格式或其他格式的证券代码
            target_source: 目标数据源名称，可选值: tushare, baostock, akshare, joinquant, rqdata

        Returns:
            str: 目标数据源格式的证券代码

        Raises:
            ValueError: 当代码格式无效或数据源名称无效时抛出
        """
        if not target_source or target_source.lower() not in cls.SOURCE_FORMATS:
            raise ValueError(f"不支持的数据源: {target_source}")

        # 先将代码标准化
        std_code = cls.standardize(code)
        numeric_code, exchange = std_code.split(".")

        # 转换为目标数据源格式
        target_source = target_source.lower()

        if target_source == "tushare":
            # tushare格式: 600000.SH
            return std_code

        elif target_source == "baostock":
            # baostock格式: sh.600000
            if exchange == "OF":
                return numeric_code  # 开放式基金通常不带交易所后缀
            exchange_alias = exchange.lower()
            return f"{exchange_alias}.{numeric_code}"

        elif target_source == "akshare":
            # akshare格式: 600000
            return numeric_code

        elif target_source in ["joinquant", "rqdata"]:
            # 聚宽/米筐格式: 600000.XSHG
            if exchange == "SH":
                return f"{numeric_code}.XSHG"
            elif exchange == "SZ":
                return f"{numeric_code}.XSHE"
            elif exchange == "BJ":
                return f"{numeric_code}.BSE"
            elif exchange == "HK":
                return f"{numeric_code}.XHKG"
            elif exchange == "OF":
                return f"{numeric_code}"  # 开放式基金通常不带交易所后缀

        return std_code
