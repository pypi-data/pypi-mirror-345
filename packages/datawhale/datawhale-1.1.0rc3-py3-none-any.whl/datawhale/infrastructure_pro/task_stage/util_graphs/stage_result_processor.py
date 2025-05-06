#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from typing import Dict, List, Any, Union, Optional, Callable

# 模块内的使用相对导入
from ..stage import Stage

# 模块外的从顶层模块导入
from datawhale.logging import get_user_logger

# 创建用户日志记录器
user_logger = get_user_logger(__name__)

"""Stage执行结果处理器"""


class StageResultFlattener:
    """处理Stage执行结果的类，将不定长列表展开到一层

    用于处理已执行完成的Stage对象，收集所有具有params和data的结果项，
    并将嵌套的多级列表结果展平为单一层次的列表。

    属性:
        stage: 已执行完成的Stage对象
        node_name: 要处理的节点名称，默认为"save_df_to_cache"
        _cached_results: 缓存的处理结果
    """

    def __init__(self, stage: Stage, node_name: str = "save_df_to_cache"):
        """初始化Stage结果展平器

        Args:
            stage: 已执行完成的Stage对象
            node_name: 要处理的节点名称，默认为"save_df_to_cache"
        """
        self.stage = stage
        self.node_name = node_name
        self._cached_results = None  # 缓存处理结果
        user_logger.debug(
            f"创建Stage结果展平器, stage_id={stage.stage_id}, node_name={node_name}"
        )

    def process(self) -> List[Dict[str, Any]]:
        """处理Stage的执行结果，将嵌套列表展平为单层

        从Stage的所有registries中收集和提取结果项，每个结果项是包含params和data的字典。
        结果格式通常为[{"params": params, "data": df}, ...]
        对于嵌套的列表结果，会将其展平为单一层次的列表。

        Returns:
            所有有效结果项的列表，每个元素是一个字典，包含params和data两个键
        """
        # 如果已有缓存结果，直接返回
        if self._cached_results is not None:
            return self._cached_results

        # 验证registries是否存在
        if not self.stage.registries:
            user_logger.warning(f"Stage {self.stage.stage_id} 没有注册表，无法处理结果")
            return []

        # 收集所有registry中的结果
        all_results = []
        for i, registry in enumerate(self.stage.registries):
            # 获取当前registry中指定节点的值
            result_list = registry.get_value(self.node_name)

            # 如果找到结果（结果是一个列表）
            if result_list:
                # 记录找到的结果项数量
                user_logger.debug(f"从registry #{i} 提取到 {len(result_list)} 个结果项")

                # 将当前registry的所有结果项添加到总列表中
                all_results.extend(result_list)

                # 记录每个项的格式，用于调试
                if result_list and user_logger.isEnabledFor(10):  # DEBUG level
                    sample = result_list[0]
                    user_logger.debug(
                        f"结果项示例: {sample.keys() if isinstance(sample, dict) else type(sample)}"
                    )
            else:
                user_logger.warning(
                    f"Registry #{i} 中没有找到节点 {self.node_name} 的结果"
                )

        # 如果没有找到任何结果
        if not all_results:
            user_logger.warning(f"没有找到任何结果")
            return []

        # 过滤出有效的结果项（包含params和data的字典）
        valid_results = []
        for item in all_results:
            if isinstance(item, dict) and "params" in item and "data" in item:
                valid_results.append(item)
            else:
                user_logger.warning(f"跳过无效的结果项: {item}")

        # 缓存处理结果
        self._cached_results = valid_results

        user_logger.info(
            f"从 {len(self.stage.registries)} 个registry中总共收集到 {len(valid_results)} 个有效结果项"
        )
        return valid_results


class StageResultHashMerger:
    """处理Stage执行结果的类，根据hash值合并相同参数的数据

    用于处理已执行完成的Stage对象中extract_df_params节点的结果项，
    根据hash值识别具有相同参数的结果项，将它们的data合并为一个列表。

    属性:
        stage: 已执行完成的Stage对象
        node_name: 要处理的节点名称，默认为"extract_df_params"
        _cached_results: 缓存的处理结果
    """

    def __init__(self, stage: Stage, node_name: str = "extract_df_params"):
        """初始化Stage结果Hash合并器

        Args:
            stage: 已执行完成的Stage对象
            node_name: 要处理的节点名称，默认为"extract_df_params"
        """
        self.stage = stage
        self.node_name = node_name
        self._cached_results = None  # 缓存处理结果
        user_logger.debug(
            f"创建Stage结果Hash合并器, stage_id={stage.stage_id}, node_name={node_name}"
        )

    def process(self) -> List[Dict[str, Any]]:
        """处理Stage的执行结果，将具有相同hash的结果项的data合并

        从Stage的所有registries中收集extract_df_params节点的结果项，
        根据hash值识别具有相同参数的结果项，将它们的data合并为一个列表。
        注意：extract_df_params返回单个字典{"params": params, "data": df, "hash": params_hash}，
        而不是列表。

        Returns:
            处理后的结果项列表，具有相同hash的结果项被合并
        """
        # 如果已有缓存结果，直接返回
        if self._cached_results is not None:
            return self._cached_results

        # 验证registries是否存在
        if not self.stage.registries:
            user_logger.warning(f"Stage {self.stage.stage_id} 没有注册表，无法处理结果")
            return []

        # 使用hash值作为key，直接合并具有相同hash的结果项
        hash_dict = {}  # 类型: Dict[int, Dict[str, Any]]
        total_processed = 0

        # 遍历每个registry
        for i, registry in enumerate(self.stage.registries):
            # 获取当前registry中指定节点的值
            result = registry.get_value(self.node_name)

            # 跳过无结果的registry
            if result is None:
                user_logger.warning(
                    f"Registry #{i} 中没有找到节点 {self.node_name} 的结果"
                )
                continue

            # 检查结果项是否有效 - extract_df_params返回单个字典，不是列表
            if (
                not isinstance(result, dict)
                or "params" not in result
                or "data" not in result
                or "hash" not in result
            ):
                user_logger.warning(f"Registry #{i} 中的结果无效: 缺少必要的键")
                continue

            total_processed += 1

            # 获取hash值
            item_hash = result["hash"]

            # 如果hash已存在，合并data
            if item_hash in hash_dict:
                existing_item = hash_dict[item_hash]
                # 直接添加到已有的data列表中，因为我们确保data始终是列表
                existing_item["data"].append(result["data"])
                user_logger.debug(
                    f"合并了hash值为 {item_hash} 的结果项，data列表长度现为 {len(existing_item['data'])}"
                )
            else:
                # 新的hash，直接加入字典但将data转换为列表
                new_item = result.copy()  # 使用副本避免修改原始数据
                new_item["data"] = [new_item["data"]]  # 将data转换为单元素列表
                hash_dict[item_hash] = new_item
                user_logger.debug(f"添加了新的hash值 {item_hash}，data为单元素列表")

        # 如果没有处理任何结果
        if total_processed == 0:
            user_logger.warning(f"没有找到任何有效结果项")
            return []

        # 将合并后的结果转换为列表
        merged_results = list(hash_dict.values())

        # 缓存处理结果
        self._cached_results = merged_results

        user_logger.info(
            f"处理了 {total_processed} 个原始结果项，合并后得到 {len(merged_results)} 个结果项"
        )
        return merged_results
