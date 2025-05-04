import os
import platform
import logging
from typing import Optional

# 创建日志记录器
logger = logging.getLogger("mxlite.utils")


def get_bin_dir() -> str:
    """
    获取二进制文件目录路径

    Returns:
        str: 二进制文件目录的绝对路径
    """
    bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir, exist_ok=True)
    return bin_dir


def get_arch(arch_str: str) -> str:
    """
    获取指定系统的架构
    Args:
        arch_str: 系统架构字符串，可通过 platform.machine() 或 uname -m 获取

    Returns:
        str: 系统架构，如 'x86_64' 或 'arm64'
    """
    return {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
    }.get(arch_str.lower(), arch_str.lower())


def get_system(system_str: str) -> str:
    """
    获取指定系统的名称
    Args:
        system_str: 系统名称字符串，可通过 platform.system() 获取

    Returns:
        str: 系统名称，如 'linux' 或 'windows'
    """
    return {
        "linux": "linux",
        "windows": "windows",
        "darwin": "darwin",
    }.get(system_str.lower(), system_str.lower())


def get_mxd_path() -> Optional[str]:
    """
    获取MXD可执行文件路径，基于当前平台

    Returns:
        Optional[str]: MXD可执行文件的绝对路径，如果文件不存在则返回None
    """
    system = get_system(platform.system().lower())
    arch = get_arch(platform.machine().lower())
    bin_dir = get_bin_dir()

    # 确定可执行文件名
    executable = f"mxd-{system}-{arch}"
    if system == "windows":
        executable += ".exe"

    file_path = os.path.join(bin_dir, executable)
    if os.path.exists(file_path):
        # 确保文件有执行权限
        if system != "windows":
            os.chmod(file_path, 0o755)
        return file_path

    logger.warning(f"未找到MXD可执行文件: {file_path}")
    return None


def get_mxa_path(arch: str = "arm64") -> Optional[str]:
    """
    获取MXA可执行文件路径

    Args:
        arch: 指定架构，如 'x86_64' 或 'arm64'

    Returns:
        Optional[str]: MXA可执行文件的绝对路径，如果文件不存在则返回None
    """
    bin_dir = get_bin_dir()
    executable = f"mxa-linux-{arch.lower()}"
    file_path = os.path.join(bin_dir, executable)
    if os.path.exists(file_path):
        os.chmod(file_path, 0o755)
        return file_path

    logger.warning(f"未找到MXA可执行文件: {file_path}")
    return None
