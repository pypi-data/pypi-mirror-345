#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Dict, Optional, Union, Iterator, Any
import pandas as pd
import os
import itertools
from .layer import Layer


class Layers:
    """多层文件结构管理类

    负责创建、存储和调整多层文件夹结构。
    可以根据提供的字段列表创建多个层级，并管理它们之间的关联关系。

    属性:
        layers: 按层级顺序存储的Layer对象列表
        root: 根层级对象
    """

    def __init__(self, fields: List[str] = None):
        """初始化多层结构

        Args:
            fields: 用于创建层级的字段列表，如果为None则创建一个仅有根层级的结构
        """
        self.layers: List[Layer] = []
        self.root: Optional[Layer] = None

        # 如果提供了字段列表，创建相应的层级结构
        if fields is not None:
            self.create_layers(fields)

    def create_layers(self, fields: List[str]) -> None:
        """根据字段列表创建层级结构

        第一层使用默认field="root"，后续层级使用提供的fields列表中的值

        Args:
            fields: 用于创建层级的字段列表
        """
        # 清空现有层级
        self.layers = []

        # 创建第一层（根层级），默认field为"root"
        root_layer = Layer(level=0, field="root")
        self.layers.append(root_layer)
        self.root = root_layer

        # 创建后续层级
        prev_layer = root_layer
        for i, field in enumerate(fields, 1):
            new_layer = Layer(level=i, field=field)
            # 链接到前一层
            prev_layer.link_next(new_layer)
            self.layers.append(new_layer)
            prev_layer = new_layer

    def add_layer(self, field: str) -> Layer:
        """在结构末尾添加新层级

        Args:
            field: 新层级的字段名

        Returns:
            新创建的Layer对象

        Raises:
            ValueError: 如果层级结构还未初始化
        """
        if not self.layers:
            raise ValueError("层级结构未初始化，请先调用create_layers方法")

        # 获取当前最后一层
        last_layer = self.layers[-1]
        # 创建新层级
        new_layer = Layer(level=last_layer.level + 1, field=field)
        # 链接到前一层
        last_layer.link_next(new_layer)
        # 添加到层级列表
        self.layers.append(new_layer)

        return new_layer

    def insert_layer(self, position: int, field: str) -> Layer:
        """在指定位置插入新层级

        Args:
            position: 插入位置（0表示在根层级之后）
            field: 新层级的字段名

        Returns:
            新创建的Layer对象

        Raises:
            ValueError: 如果position无效或层级结构未初始化
        """
        if not self.layers:
            raise ValueError("层级结构未初始化，请先调用create_layers方法")

        if position < 0 or position >= len(self.layers):
            raise ValueError(f"无效的插入位置: {position}")

        # 创建新层级
        new_layer = Layer(level=position + 1, field=field)

        # 处理前后层级的链接
        prev_layer = self.layers[position]
        next_layer = prev_layer.next_layer

        # 链接新层级
        prev_layer.link_next(new_layer)
        if next_layer:
            new_layer.link_next(next_layer)

        # 更新后续层级的level值
        for i, layer in enumerate(self.layers[position + 1 :], position + 2):
            layer.level = i

        # 在正确位置插入新层级
        self.layers.insert(position + 1, new_layer)

        return new_layer

    def remove_layer(self, position: int) -> None:
        """移除指定位置的层级

        Args:
            position: 要移除的层级位置

        Raises:
            ValueError: 如果position无效、层级结构未初始化或尝试移除根层级
        """
        if not self.layers:
            raise ValueError("层级结构未初始化，请先调用create_layers方法")

        if position <= 0 or position >= len(self.layers):
            raise ValueError(f"无效的层级位置: {position}")

        # 获取要移除的层级
        layer_to_remove = self.layers[position]
        prev_layer = layer_to_remove.prev_layer
        next_layer = layer_to_remove.next_layer

        # 重新链接前后层级
        if prev_layer and next_layer:
            prev_layer.link_next(next_layer)
        elif prev_layer:
            prev_layer.next_layer = None

        # 从列表中移除
        self.layers.pop(position)

        # 更新后续层级的level值
        for i, layer in enumerate(self.layers[position:], position):
            layer.level = i

    def _generate_value_combinations(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> List[List[str]]:
        """生成所有可能的字段值组合

        Args:
            field_values: 部分字段名到字段值的映射，必须包含root键。
                         root键的值必须是字符串，其他字段值可以是单个值或值列表。

        Returns:
            所有可能的字段值组合列表，每个组合是一个列表，包含root值和其他层级的值

        Raises:
            ValueError: 如果field_values不包含root键或root值不是字符串
        """
        if field_values is None:
            raise ValueError("field_values不能为None，必须包含'root'键")

        # 检查是否包含root键
        if "root" not in field_values:
            raise ValueError("field_values必须包含'root'键")

        # 获取root值
        root_value = field_values["root"]

        # 确保root值是字符串
        if isinstance(root_value, list):
            raise ValueError("root值必须是字符串，不能是列表")

        root_value = str(root_value)

        # 获取非root层的层级
        non_root_layers = list(self.layers)[1:]

        # 如果没有非root层，返回只包含root值的组合
        if not non_root_layers:
            return [[root_value]]

        # 为每个层级准备值列表
        layer_values = []
        for layer in non_root_layers:
            field = layer.field

            # 如果提供了字段值
            if field in field_values:
                field_value = field_values[field]

                # 如果值是列表
                if isinstance(field_value, list):
                    # 转换所有值为字符串
                    layer_values.append([str(v) for v in field_value])
                else:
                    # 单个值转为列表
                    layer_values.append([str(field_value)])
            else:
                # 使用通配符
                layer_values.append(["*"])

        # 生成非root层的所有可能组合
        non_root_combinations = list(itertools.product(*layer_values))

        # 将root值与非root组合结合
        all_combinations = []
        for non_root_combo in non_root_combinations:
            all_combinations.append([root_value] + list(non_root_combo))

        return all_combinations

    def _create_pattern(self, value_combination: List[str]) -> str:
        """从字段值组合创建匹配模式

        Args:
            value_combination: 字段值的组合列表，包含root值和其他层级的值

        Returns:
            生成的模式字符串，包含root值作为前缀
        """

        return os.path.join(*value_combination)

    def get_match_pattern(
        self, field_values: Dict[str, Union[str, List[str], Any]] = None
    ) -> List[str]:
        """根据部分字段值生成用于glob匹配的模式

        对于未提供值的字段，使用通配符*代替。
        支持字段值为单个值或值列表，始终返回模式列表。
        必须包含root字段的值，且root值必须是字符串。

        例如，对于三层结构root->code->date:
        - 当提供root='dataset', code=1时，将生成["dataset/1/*"]
        - 当提供root='dataset', code=[1,2]时，将生成["dataset/1/*", "dataset/2/*"]
        - 当提供root='dataset', code=[1,2], date=["20230101","20230102"]时，
          将生成["dataset/1/20230101", "dataset/1/20230102", "dataset/2/20230101", "dataset/2/20230102"]

        Args:
            field_values: 部分字段名到字段值的映射，必须包含root键

        Returns:
            用于glob匹配的模式字符串列表
        """
        # 获取所有可能的值组合
        value_combinations = self._generate_value_combinations(field_values)

        # 创建匹配模式
        patterns = []
        for combination in value_combinations:
            pattern = self._create_pattern(combination)
            patterns.append(pattern)

        # 始终返回列表
        return patterns

    def __iter__(self) -> Iterator[Layer]:
        """返回层级迭代器

        Returns:
            层级对象迭代器
        """
        return iter(self.layers)

    def __len__(self) -> int:
        """返回层级数量

        Returns:
            层级数量
        """
        return len(self.layers)

    def __getitem__(self, key: int) -> Layer:
        """通过索引获取层级

        Args:
            key: 层级索引

        Returns:
            对应的Layer对象
        """
        return self.layers[key]

    def validate_field_values(self, field_values: Dict[str, str]) -> None:
        """验证字段值是否完整有效

        检查提供的字段值是否包含所有必需的非root字段。

        Args:
            field_values: 字段名到字段值的映射

        Raises:
            ValueError: 当缺少必需字段时抛出
        """
        # 获取所有非root层的字段名
        non_root_fields = [layer.field for layer in self.layers[1:]]

        # 如果没有非root层，不需要验证
        if not non_root_fields:
            return

        # 检查所有必需的字段是否都提供了
        missing_fields = set(non_root_fields) - set(field_values.keys())
        if missing_fields:
            raise ValueError(f"缺少必需的字段值: {missing_fields}")

    def build_file_path(
        self, base_path: str, root_value: str, field_values: Dict[str, str]
    ) -> str:
        """构建文件的完整路径

        根据字段值构建文件路径，最后一层将字段值作为文件名而不是目录。

        Args:
            base_path: 基础路径
            root_value: 根层的值（数据集名称）
            field_values: 字段名到字段值的映射

        Returns:
            构建的文件完整路径
        """
        # 验证字段值
        self.validate_field_values(field_values)

        # 构建路径组件
        path_components = [base_path, root_value]

        # 获取所有非root层的字段
        non_root_layers = list(self.layers)[1:]

        # 如果没有非root层，使用默认文件名
        if not non_root_layers:
            dir_path = os.path.join(*path_components)
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, "data")
            return file_path

        # 添加除最后一层外的所有层作为目录
        for i, layer in enumerate(non_root_layers[:-1]):
            field = layer.field
            path_components.append(field_values[field])

        # 创建直到倒数第二层的目录
        dir_path = os.path.join(*path_components)
        os.makedirs(dir_path, exist_ok=True)

        # 最后一层作为文件名
        last_field = non_root_layers[-1].field
        file_name = field_values[last_field]
        file_path = os.path.join(dir_path, file_name)

        return file_path

    def extract_field_values(
        self, file_path: str, base_path: str, root_value: str
    ) -> Dict[str, str]:
        """从文件路径中提取字段值

        Args:
            file_path: 文件的绝对路径
            base_path: 基础路径
            root_value: 根层的值（数据集名称）

        Returns:
            字段名到字段值的映射字典
        """
        # 计算相对路径（相对于base_path）
        try:
            rel_path = os.path.relpath(file_path, base_path)
        except ValueError:
            # 如果路径无法计算相对路径（例如在不同驱动器上）
            raise ValueError(f"无法计算相对路径: {file_path} 相对于 {base_path}")

        # 分割路径组件
        components = rel_path.split(os.sep)

        # 第一个组件应该是root_value
        if not components or components[0] != root_value:
            raise ValueError(f"文件路径 {file_path} 不在数据集 {root_value} 中")

        # 获取所有非root层的字段名
        non_root_layers = list(self.layers)[1:]

        # 如果只有root层，返回空字典
        if not non_root_layers:
            return {}

        field_names = [layer.field for layer in non_root_layers]

        # 创建字段值映射
        field_values = {}

        # 从路径组件中提取字段值
        for i, field in enumerate(field_names):
            # 确保索引在范围内（考虑到根目录和可能的文件扩展名）
            if i + 1 < len(components):
                # 如果是最后一个字段，处理可能带有扩展名的文件名
                if i == len(field_names) - 1:
                    # 提取不带扩展名的文件名作为字段值
                    file_name = components[i + 1]
                    field_values[field] = os.path.splitext(file_name)[0]
                else:
                    field_values[field] = components[i + 1]

        return field_values
