"""
Python SDK for MetalX Lite (MXLite)[https://github.com/koitococo/mxlite]
提供与服务器交互的工具和类，用于系统部署和管理。
"""

# 导出核心类和函数
from .mxlite import (
    MXLite, MXLiteConfig, MXDRunner, ErrorReason
)

from .utils import (
    get_mxd_path,
    get_mxa_path,
)

__all__ = [
    # mxlite模块
    "MXLiteConfig", "MXLite", "MXDRunner", "ErrorReason",
    # utils模块
    "get_mxd_path", "get_mxa_path",
]
