# DataWhale 数据分析工具包

## 项目简介
DataWhale 是一个综合性的数据分析工具包，集成了多个金融数据源的接口，提供了便捷的数据获取和分析功能。本项目旨在为数据分析师和量化交易研究者提供一站式的数据解决方案。

## 主要特性
- 多数据源支持：集成 AKShare、Tushare、JQData、BaoStock 等主流金融数据接口
- 数据处理工具：提供数据清洗、转换和分析的常用工具
- 数据存储：支持 SQL 数据库存储和管理
- 可扩展性：模块化设计，便于扩展和自定义
- 数据下载与更新：支持全市场数据批量下载和增量更新
- 断点续传：支持数据下载和更新的断点续传功能

## 安装方法

### 使用pip安装
```bash
pip install datawhale
```

### 从源码安装
```bash
git clone https://github.com/yourusername/datawhale.git
cd datawhale
pip install -e .
```

### 依赖要求
- Python >= 3.8
- akshare >= 1.16.13
- baostock >= 0.8.9
- pandas >= 2.2.3
- numpy >= 2.2.3
- tushare >= 1.4.19
- jqdatasdk >= 1.9.7
- SQLAlchemy >= 2.0.38

## 快速开始

### 基本使用
```python
from datawhale.application import get_daily_kline, get_stock_list

# 获取股票列表
stock_list = get_stock_list()

# 获取日K线数据（不复权）
df = get_daily_kline(
    stock_code="600000",
    start_date="20240101",
    end_date="20240331",
    adjust_flag="3"  # 1：后复权，2：前复权，3：不复权
)
```

### 数据下载功能
```python
from datawhale.application import download_daily_kline, download_adjust_factor
from datetime import datetime

# 下载全市场日K线数据
result = download_daily_kline(
    mode='all',              # 下载全市场数据
    start_date='1990-01-01', # 从1990年开始下载
    end_date=datetime.now().strftime('%Y-%m-%d'),  # 下载到最新日期
    adjust_flag='3',         # 不复权
    force_update=False,      # 不强制更新已存在的数据
    resume_failed=True       # 继续下载之前失败的数据
)

# 下载复权因子数据
result = download_adjust_factor(
    mode='all',              # 下载全市场数据
    start_date='1990-01-01', # 从1990年开始下载
    end_date=datetime.now().strftime('%Y-%m-%d'),  # 下载到最新日期
    force_update=False,      # 不强制更新已存在的数据
    resume_failed=True       # 继续下载之前失败的数据
)
```

### 数据更新功能
```python
from datawhale.application import update_daily_kline, update_adjust_factor, update_stock_list

# 更新股票列表
update_result = update_stock_list()

# 更新最新一天的日K线数据
result = update_daily_kline(
    resume_failed=True  # 继续更新之前失败的股票数据
)

# 更新最新的复权因子数据
result = update_adjust_factor(
    resume_failed=True  # 继续更新之前失败的股票数据
)
```

## 项目结构
```
datawhale/
├── application/       # 应用层：业务逻辑实现
├── domain/           # 领域层：核心业务模型
├── infrastructure/   # 基础设施层：数据源、存储等
└── config/           # 配置文件
```

## API文档

### 数据获取接口
- `get_daily_kline()`: 获取本地日K线数据
- `get_stock_list()`: 获取本地股票列表
- `get_adjust_factor()`: 获取本地复权因子数据

### 数据下载接口
- `download_daily_kline()`: 下载日K线数据，支持全市场或按股票代码首位数字下载
- `download_adjust_factor()`: 下载复权因子数据，支持全市场或按股票代码首位数字下载

### 数据更新接口
- `update_stock_list()`: 更新股票列表数据
- `update_daily_kline()`: 更新最新一天的日K线数据，支持断点续传
- `update_adjust_factor()`: 更新最新的复权因子数据，支持断点续传
- `update_listing_date()`: 更新股票上市日期数据

详细的API文档请参考 `docs/domain_services_usage.md`

## 贡献指南
1. Fork 本仓库
2. 创建新的分支 `git checkout -b feature/your-feature`
3. 提交更改 `git commit -am 'Add new feature'`
4. 推送到分支 `git push origin feature/your-feature`
5. 提交 Pull Request

## 开源协议
本项目采用 BSD 协议开源，详见 [LICENSE](LICENSE) 文件。

## 联系方式
- 作者：王工一念
- 邮箱：hans_wang@outlook.com

更新日志
详见 [CHANGELOG](CHANGELOG.md) 文件。
