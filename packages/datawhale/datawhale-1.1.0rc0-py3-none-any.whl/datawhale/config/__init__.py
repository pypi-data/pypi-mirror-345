# 配置文件包 
import os
import yaml
import pathlib

def set_data_dir(absolute_path):
    """
    设置数据存储路径
    
    Args:
        absolute_path: 数据存储的绝对路径
    """
    # 创建目录
    pathlib.Path(absolute_path).mkdir(parents=True, exist_ok=True)
    
    # 修改storage.yaml文件中的配置
    storage_file = os.path.join(os.path.dirname(__file__), 'infrastructure', 'storage.yaml')
    
    # 读取原始配置
    with open(storage_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新数据路径
    config['data_dir'] = absolute_path
    
    # 保存配置
    with open(storage_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return absolute_path

def set_runtime_dir(absolute_path):
    """
    设置运行信息存储路径
    
    Args:
        absolute_path: 运行信息存储的绝对路径
    """
    # 创建目录
    pathlib.Path(absolute_path).mkdir(parents=True, exist_ok=True)
    
    # 修改storage.yaml文件中的配置
    storage_file = os.path.join(os.path.dirname(__file__), 'infrastructure', 'storage.yaml')
    
    # 读取原始配置
    with open(storage_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新运行信息路径
    config['runtime_dir'] = absolute_path
    
    # 保存配置
    with open(storage_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return absolute_path

def get_data_dir():
    """
    获取当前配置的数据存储路径
    
    Returns:
        str: 数据存储的绝对路径
    """
    storage_file = os.path.join(os.path.dirname(__file__), 'infrastructure', 'storage.yaml')
    
    # 读取配置
    with open(storage_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config['data_dir']

def get_runtime_dir():
    """
    获取当前配置的运行信息存储路径
    
    Returns:
        str: 运行信息存储的绝对路径
    """
    storage_file = os.path.join(os.path.dirname(__file__), 'infrastructure', 'storage.yaml')
    
    # 读取配置
    with open(storage_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config['runtime_dir'] 