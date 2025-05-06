from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 明确列出所有包
packages = find_packages(include=['datawhale', 'datawhale.*'])

setup(
    name="datawhale",
    version="1.1.0rc0",
    author="王工一念",
    author_email="hans_wang@outlook.com",
    description="金融数据平台，数据统一标准层。统一多数据源接口，可维护本地数据存储、更新",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    package_data={
        'datawhale.config': ['*.yaml', 'infrastructure/*.yaml'],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "baostock>=0.8.9",
        "pandas>=2.2.3",
        "numpy>=1.26.0",
        "tushare>=1.4.19",
        "beautifulsoup4>=4.13.3",
        "requests>=2.32.3",
        "SQLAlchemy>=2.0.38",
        "PyMySQL>=1.1.1",
        "PyYAML>=6.0",
        "graphviz>=0.20.0"
    ],
)