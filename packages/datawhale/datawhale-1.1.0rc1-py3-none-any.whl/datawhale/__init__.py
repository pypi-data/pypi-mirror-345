#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DataWhale基础设施模块接口

提供任务图、任务阶段、存储服务和任务系统的统一接口
"""

__version__ = "1.1.0rc1"

# 导入日志和异常模块（这些是基础模块，其他模块可能依赖它们）
import datawhale.logging as logging
import datawhale.exceptions as exceptions

# 导入配置模块
import datawhale.config as config

# 导入基础设施模块
import datawhale.storage as storage
import datawhale.local as local
import datawhale.standard as standard

# 导入应用层模块
import datawhale.app as app

# 导入核心功能模块
import datawhale.graph as graph
import datawhale.tasks as tasks

# 导入初始化模块
import datawhale.init as init


# 导入存储服务接口
from datawhale.storage import *

# 导入本地存储接口
from datawhale.local import *

# 导入标准化接口
from datawhale.standard import *

# 导入应用层接口
from datawhale.app import *

# 导入任务系统接口
from datawhale.tasks import *

# 导入任务图接口
from datawhale.graph import *

# 导入初始化配置接口
from datawhale.init import *

# 导入日志接口
from datawhale.logging import *

# 导入配置系统接口
from datawhale.config import *

# 导入异常接口
from datawhale.exceptions import *

# 重新导出所有接口
__all__ = []

# 扩展__all__列表
for module in [
    storage,
    local,
    standard,
    app,
    tasks,
    graph,
    init,
    logging,
    config,
    exceptions,
]:
    if hasattr(module, "__all__"):
        __all__.extend(module.__all__)
