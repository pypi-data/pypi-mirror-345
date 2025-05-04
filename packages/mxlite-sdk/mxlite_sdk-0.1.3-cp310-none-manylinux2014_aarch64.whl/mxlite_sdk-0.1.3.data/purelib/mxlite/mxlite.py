import asyncio
import json
import logging
import os
import random
import re
import socket
import subprocess
import threading
import urllib.parse
from pathlib import Path
from typing import Dict, Tuple, Union, Optional, Literal, TypeVar, cast, Type

import aiohttp
from pydantic import BaseModel

from .types import (
    ErrorResponse, ErrorReason, HostListResponse, HostInfoSuccessResponse, HostInfoErrorResponse, HostListInfoResponse,
    TaskResult, AddTaskResult, AddFileMapResponse, GetUrlSubResponse, LsdirResponse, StringResponse, StringListResponse
)
from .utils import get_mxd_path, get_bin_dir

# 创建日志记录器
logger = logging.getLogger("mxlite")

# 类型变量
T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')

# 类型别名
ApiResult = Tuple[T, int]  # API返回结果和HTTP状态码的元组


class MXLiteConfig:
    """
    MXLite 配置类，管理 SDK 的配置参数
    """

    def __init__(
            self,
            root_dir: Optional[str] = None,
            http_port: Optional[int] = None,
            https_port: Optional[int] = None,
            token: Optional[str] = None,
            certificates_dir: Optional[str] = None,
            env_dict: Optional[Dict[str, str]] = None,
            verbose: bool = False,
            host: str = "127.0.0.1"  # 默认主机地址
    ):
        """
        初始化 MXLite 配置

        Args:
            root_dir: 资源文件所在的目录
            http_port: HTTP端口
            https_port: HTTPS端口
            token: 认证令牌
            certificates_dir: 证书目录
            env_dict: 可选的环境变量字典，用于从环境变量获取配置
            verbose: 是否输出详细日志
            host: 主机地址，默认为127.0.0.1
        """
        self.env = env_dict or os.environ
        self._executable = None
        self._root_dir = root_dir
        self.http_port = http_port or self._get_random_port(40000, 50000)
        self.https_port = https_port or self._get_random_port(50001, 60000)
        self._token = token or ""
        self._certificates_dir = certificates_dir
        self.verbose = verbose
        self.host = host  # 保存主机地址

    def _get_random_port(self, min_port: int, max_port: int, attempt: int = 0) -> int:
        """获取随机端口"""
        if attempt > 10:
            raise socket.error("无法获取随机端口")
        port = random.randint(min_port, max_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(0.2)
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except socket.error:
            sock.close()
            return self._get_random_port(min_port, max_port, attempt + 1)

    @property
    def executable(self) -> Optional[str]:
        """获取MXD可执行文件名"""
        if self._executable is not None:
            return self._executable

        # 从环境变量获取
        env_exec = self.env.get("MXD_EXECUTABLE")
        if env_exec:
            return env_exec

        # 尝试自动查找适用于当前平台的mxd可执行文件
        platform_exec = get_mxd_path()
        if platform_exec:
            # 返回文件名，而不是完整路径
            self._executable = os.path.basename(platform_exec)
            return self._executable
        return None

    @property
    def root_dir(self) -> str:
        """获取根目录，默认为当前目录"""
        if self._root_dir is not None:
            return self._root_dir
        self._root_dir = self.env.get("MXD_ROOT_DIR", os.getcwd())
        return self._root_dir

    @property
    def bin_dir(self) -> str:
        """获取二进制文件目录"""
        return get_bin_dir()

    @property
    def token(self) -> Optional[str]:
        """获取认证令牌"""
        if self._token is not None:
            return self._token
        return self.env.get("MXD_TOKEN")

    @property
    def certificates_dir(self) -> str:
        """获取证书目录，默认为根目录下的certs目录"""
        if self._certificates_dir is not None:
            return self._certificates_dir
        return self.env.get("MXD_CERTS_DIR", os.path.join(self.root_dir, "certs"))

    def get_mxd_executable_path(self) -> Optional[str]:
        """
        获取MXD可执行文件的完整路径

        Returns:
            str: 可执行文件的完整路径或None
        """
        exec_name = self.executable
        if not exec_name:
            return None

        # 先检查bin_dir目录
        bin_path = os.path.join(get_bin_dir(), exec_name)
        if os.path.exists(bin_path):
            if not os.access(bin_path, os.X_OK):
                logger.error(f"MXD 可执行文件没有执行权限: {bin_path}")
                os.chmod(bin_path, 0o755)
            if os.access(bin_path, os.X_OK):
                return bin_path
        return None


class MXDRunner:
    """
    MXD 运行器类，负责管理 MXD 进程的生命周期
    """

    def __init__(self, config: MXLiteConfig):
        """
        初始化 MXD 运行器

        Args:
            config: MXLite 配置对象
        """
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.abort_controller_active = False

    def start_mxd(
            self,
            resource_path: Optional[str] = None,
            with_https: Optional[bool] = False,
            generate_cert: Optional[bool] = True
    ) -> bool:
        """
        启动MXD服务

        Args:
            resource_path: 可选，资源文件路径
            with_https: 是否启用HTTPS
            generate_cert: 是否生成证书(仅在启用HTTPS时有效)

        Returns:
            bool: 启动是否成功
        """
        if not with_https and generate_cert:
            generate_cert = False
        mxd_path = self.config.get_mxd_executable_path()
        if mxd_path and not self.process:
            logger.info(f"使用mxd可执行文件: {mxd_path}")
            self.process = self._run_mxd(mxd_path, resource_path, with_https, generate_cert)
            return self.process is not None
        else:
            if not mxd_path:
                logger.error("未找到有效的MXD可执行文件")
            elif self.process:
                logger.warning("MXD服务已经在运行中")
            return False

    def _run_mxd(
            self,
            mxd_path: str,
            resource_path: Optional[str] = None,
            with_https: Optional[bool] = False,
            generate_cert: Optional[bool] = True
    ) -> Optional[subprocess.Popen]:
        """
        运行MXD可执行程序

        Args:
            mxd_path: MXD可执行文件的完整路径
            resource_path: 可选，静态文件路径
            with_https: 是否启用HTTPS
            generate_cert: 是否生成证书(仅在启用HTTPS时有效)

        Returns:
            subprocess.Popen: MXD进程对象，如果启动失败则返回None
        """
        if not os.path.exists(mxd_path) or not os.access(mxd_path, os.X_OK):
            logger.error(f"MXD 可执行文件不存在或没有执行权限: {mxd_path}")
            return None

        if self.abort_controller_active:
            self.kill_mxd()

        self.abort_controller_active = True

        # 确保证书目录存在
        certs_dir = Path(self.config.certificates_dir)
        if not certs_dir.exists():
            certs_dir.mkdir(parents=True, exist_ok=True)

        # 构建命令行参数
        cmd = [mxd_path]

        # 添加令牌参数
        if self.config.token:
            cmd.extend(["-k", self.config.token])

        # 添加静态路径参数
        if resource_path:
            cmd.extend(["-s", resource_path])

        # 修复：将端口值转换为字符串
        cmd.extend(["-p", str(self.config.http_port or 15080), "--http"])

        # HTTPS相关配置
        if with_https:
            cmd.extend(["-P", str(self.config.https_port or 15443), "--https"])

            # 检查证书文件是否存在
            cert_exists = os.path.exists(os.path.join(self.config.certificates_dir, "tls.crt"))
            key_exists = os.path.exists(os.path.join(self.config.certificates_dir, "tls.key"))

            # 如果用户要求生成证书或证书文件不存在，则添加生成证书参数
            if generate_cert or not (cert_exists and key_exists):
                cmd.extend(["--generate-cert"])
                logger.info("将生成新的HTTPS证书")

            # 添加证书路径
            cmd.extend(["--tls-cert", os.path.join(self.config.certificates_dir, "tls.crt")])
            cmd.extend(["--tls-key", os.path.join(self.config.certificates_dir, "tls.key")])
            cmd.extend(["--ca-cert", os.path.join(self.config.certificates_dir, "ca.crt")])
            cmd.extend(["--ca-key", os.path.join(self.config.certificates_dir, "ca.key")])

        try:
            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # 设置处理输出的线程
            self._setup_output_threads(process)

            logger.info(
                f"启动 mxd{f' 资源文件路径 {resource_path}' if resource_path else ''}, "
                f"http端口 {self.config.http_port or 15080}, https端口 {self.config.https_port or 15443}"
            )
            return process
        except Exception as e:
            logger.error(f"执行mxd时出错: {e}")
            return None

    def _setup_output_threads(self, process: subprocess.Popen) -> None:
        """
        设置处理进程输出的线程

        Args:
            process: 进程对象
        """

        def read_stdout():
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if line:
                        self.handle_log(line)

        def read_stderr():
            if process.stderr:
                for line in iter(process.stderr.readline, ""):
                    if line:
                        logger.error(line.strip())

        # 创建并启动线程
        stdout_thread = threading.Thread(target=read_stdout)
        stderr_thread = threading.Thread(target=read_stderr)

        stdout_thread.daemon = True
        stderr_thread.daemon = True

        stdout_thread.start()
        stderr_thread.start()

    @staticmethod
    def handle_log(data: str) -> None:
        """
        处理MXD日志输出

        Args:
            data: 日志行
        """
        rfc3339_pattern = r"^((\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?)(Z|[+-]\d{2}:\d{2})?)"

        for line in data.strip().split("\n"):
            if not line:
                continue

            # 移除时间戳
            text = re.sub(rfc3339_pattern, "", line).strip()

            # 提取日志级别和消息
            level = text[:6].strip() if len(text) > 6 else ""
            message = text[6:].strip() if len(text) > 6 else text

            # 根据日志级别输出日志
            if level == "INFO":
                logger.info(message)
            elif level == "ERROR":
                logger.error(message)
            elif level == "WARN":
                logger.warning(message)
            elif level == "DEBUG":
                logger.debug(message)
            elif level == "TRACE":
                logger.debug(message)  # Python logging没有TRACE级别，使用DEBUG代替
            else:
                logger.info(text)  # 默认为INFO级别

    def kill_mxd(self) -> None:
        """关闭MXD进程"""
        if self.abort_controller_active and self.process:
            logger.info("停止mxd...")
            try:
                self.process.terminate()
                # 给进程一些时间来优雅退出
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果进程未在超时时间内退出，则强制终止
                self.process.kill()
            except Exception as e:
                logger.error(f"停止mxd时出错: {e}")

            self.process = None
            self.abort_controller_active = False

    def is_running(self) -> bool:
        """
        检查MXD进程是否在运行

        Returns:
            bool: 进程是否在运行
        """
        return self.process is not None and self.process.poll() is None


class MXLite:
    """
    MXLite 集成客户端类，整合了MXD服务管理和MXC API客户端功能
    所有网络请求都支持异步操作
    支持内部管理MXD进程或连接外部MXD服务
    """

    def __init__(
            self,
            config: Optional[MXLiteConfig] = None,
            host: Optional[str] = None,
            http_port: Optional[int] = None,
            token: Optional[str] = None,
            auto_connect: bool = True,
            **kwargs
    ):
        """
        初始化 MXLite 客户端

        Args:
            config: MXLiteConfig 配置对象
            host: 可选，MXD服务主机地址，用于外部连接模式
            http_port: 可选，MXD服务HTTP端口
            token: 可选，MXD服务认证令牌，用于外部连接模式
            auto_connect: 是否自动连接到外部MXD服务（仅在外部模式下有效）
            **kwargs: 如果没有提供config，可以直接传入配置参数
        """
        # 确定当前的运行模式：内部运行或外部连接
        self.external_mode = host is not None

        if self.external_mode:
            # 外部连接模式，使用提供的连接参数
            self.config = MXLiteConfig(
                http_port=http_port,
                token=token,
                host=host or "127.0.0.1",
                **kwargs
            )
            self.runner = None
        else:
            # 内部运行模式，创建并管理MXD进程
            self.config = config or MXLiteConfig(**kwargs)
            self.runner = MXDRunner(self.config)

        self._session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()  # 用于确保Session的线程安全
        self._connected = False
        self._connection_check_task = None  # 连接健康检查任务
        self._reconnect_attempts = 0  # 重连尝试计数
        self.MAX_RECONNECT_ATTEMPTS = 3  # 最大重连次数
        self.RECONNECT_DELAY = 5  # 重连延迟（秒）

        # 如果是外部模式且设置了自动连接，则创建连接
        if self.external_mode and auto_connect:
            asyncio.create_task(self._ensure_connected())

    async def _ensure_connected(self) -> bool:
        """
        确保已连接到MXD服务，如果未连接则尝试连接

        Returns:
            bool: 是否已连接
        """
        if not self._connected:
            return await self.connect_mxd()
        return True

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        获取或创建一个aiohttp会话

        Returns:
            aiohttp.ClientSession: 会话对象
        """
        async with self._lock:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
            return self._session

    async def _check_connection_health(self) -> None:
        """
        定期检查与MXD服务的连接状态
        """
        while True:
            try:
                # 每30秒检查一次连接
                await asyncio.sleep(30)
                if not self._connected:
                    continue

                # 简单的健康检查
                await self._ensure_connected()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"连接健康检查异常: {e}")

    async def connect_mxd(self) -> bool:
        """
        连接到MXD服务

        Returns:
            bool: 连接是否成功
        """
        if self._connected:
            logger.warning("已经连接到MXD服务")
            return True

        try:
            # 尝试发送一个简单的请求来测试连接
            result, status = await self.get_host_list()
            if status == 200:
                self._connected = True
                logger.info(f"成功连接到MXD服务: {self.config.host}:{self.config.http_port}")

                # 启动连接健康检查任务
                if self.external_mode and self._connection_check_task is None:
                    self._connection_check_task = asyncio.create_task(self._check_connection_health())

                self._reconnect_attempts = 0  # 重置重连计数
                return True
            else:
                logger.error(f"连接MXD服务失败: {self.config.host}:{self.config.http_port}, 状态码: {status}")
                return False
        except Exception as e:
            logger.error(f"连接MXD服务时出错: {e}")
            return False

    async def reconnect_mxd(self) -> bool:
        """
        尝试重新连接MXD服务

        Returns:
            bool: 重连是否成功
        """
        if self._reconnect_attempts >= self.MAX_RECONNECT_ATTEMPTS:
            logger.error(f"达到最大重连尝试次数({self.MAX_RECONNECT_ATTEMPTS})，放弃重连")
            return False

        self._reconnect_attempts += 1
        logger.info(f"尝试重连MXD服务 (尝试 {self._reconnect_attempts}/{self.MAX_RECONNECT_ATTEMPTS})")

        # 等待一段时间后尝试重连
        await asyncio.sleep(self.RECONNECT_DELAY)
        return await self.connect_mxd()

    async def disconnect_mxd(self) -> None:
        """
        断开与MXD服务的连接
        """
        self._connected = False

        # 取消连接健康检查任务
        if self._connection_check_task:
            self._connection_check_task.cancel()
            try:
                await self._connection_check_task
            except asyncio.CancelledError:
                pass
            self._connection_check_task = None

        async with self._lock:
            if self._session and not self._session.closed:
                await self._session.close()
                self._session = None
        logger.info("已断开与MXD服务的连接")

    async def close(self):
        """关闭客户端和相关资源"""
        if self.runner:
            self.runner.kill_mxd()
        await self.disconnect_mxd()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self.external_mode:
            await self._ensure_connected()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    def start_mxd(
            self,
            resource_path: Optional[str] = None,
            with_https: Optional[bool] = False,
            generate_cert: Optional[bool] = True
    ) -> bool:
        """
        启动MXD服务

        Args:
            resource_path: 可选，资源文件路径
            with_https: 是否启用HTTPS
            generate_cert: 是否生成证书(仅在启用HTTPS时有效)

        Returns:
            bool: 启动是否成功
        """
        if self.external_mode:
            logger.warning("使用外部MXD连接模式，忽略start_mxd调用")
            return False

        if not self.runner:
            logger.error("MXDRunner未初始化")
            return False

        return self.runner.start_mxd(resource_path, with_https, generate_cert)

    def kill_mxd(self) -> None:
        """关闭MXD进程"""
        if self.external_mode:
            logger.warning("使用外部MXD连接模式，忽略kill_mxd调用")
            return

        if self.runner:
            self.runner.kill_mxd()

    def is_mxd_running(self) -> bool:
        """
        检查MXD进程是否在运行

        Returns:
            bool: 进程是否在运行
        """
        if self.external_mode:
            return self._connected

        return self.runner and self.runner.is_running()

    async def _async_request(
            self,
            url: str,
            method: str,
            response_model: Type[T],
            body: Optional[Dict] = None
    ) -> Tuple[T, int]:
        """
        发送异步HTTP请求，并将响应解析为指定的Pydantic模型

        Args:
            url: 请求URL
            method: HTTP方法
            response_model: 响应数据模型类型
            body: 可选的请求体

        Returns:
            Tuple[响应模型实例, HTTP状态码]
        """
        # 如果是外部模式，确保已连接
        if self.external_mode and not await self._ensure_connected():
            error_data = {
                "ok": False,
                "reason": ErrorReason.INTERNAL_ERROR,
                "error": "未连接到MXD服务"
            }
            # 尝试将错误数据转换为请求的响应模型，如果不兼容，则返回通用ErrorResponse
            try:
                return response_model(**error_data), 503
            except Exception as exception:
                logger.error(f"无法转换错误数据为响应模型: {error_data}，错误信息: {exception}")
                return cast(T, ErrorResponse(**error_data)), 503

        headers = {"Content-Type": "application/json"}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"

        if url.startswith("/"):
            url = f"http://{self.config.host}:{self.config.http_port}{url}"

        try:
            session = await self._get_session()
            async with session.request(method=method, url=url, headers=headers, json=body) as response:
                resp_text = await response.text()
                if response.status >= 400 and self.config.verbose:
                    logger.error(
                        f"请求失败: URL={url}, Method={method}, Body={body}, "
                        f"Status={response.status}, Response={resp_text}"
                    )

                try:
                    # 处理字符串响应的特殊情况
                    if response_model == StringResponse:
                        return StringResponse(data=resp_text.strip()), response.status
                    # 处理字符串列表响应的特殊情况
                    elif response_model == StringListResponse:
                        # 尝试解析为JSON列表，如果失败则返回空列表
                        try:
                            data = json.loads(resp_text)
                            if isinstance(data, list):
                                return StringListResponse(data=data), response.status
                            else:
                                return StringListResponse(data=[]), response.status
                        except json.JSONDecodeError:
                            return StringListResponse(data=[]), response.status

                    # 正常情况：解析JSON数据
                    json_data = json.loads(resp_text)

                    # 使用Pydantic模型验证和转换数据
                    validated_data = response_model.model_validate(json_data)
                    return validated_data, response.status
                except json.JSONDecodeError as e:
                    # 如果是特殊响应模型但JSON解析失败，返回空值
                    if response_model == StringResponse:
                        return StringResponse(data=""), response.status
                    if response_model == StringListResponse:
                        return StringListResponse(data=[]), response.status

                    logger.error(
                        f"无法解析JSON响应: URL={url}, Method={method}, Body={body}, "
                        f"Status={response.status}, Response={resp_text}, Error={e}"
                    )
                    # 创建错误响应
                    error_data = {
                        "ok": False,
                        "reason": ErrorReason.INTERNAL_ERROR,
                        "error": str(e)
                    }
                    # 尝试将错误数据转换为请求的响应模型
                    try:
                        return response_model.model_validate(error_data), response.status
                    except Exception as exception:
                        logger.error(f"无法转换错误数据为响应模型: {error_data}，错误信息: {exception}")
                        return cast(T, ErrorResponse.model_validate(error_data)), response.status

                except Exception as e:
                    logger.error(
                        f"响应数据验证失败: URL={url}, Method={method}, "
                        f"Status={response.status}, Error={e}"
                    )
                    error_data = {
                        "ok": False,
                        "reason": ErrorReason.INTERNAL_ERROR,
                        "error": f"响应数据验证失败: {str(e)}"
                    }
                    try:
                        return response_model.model_validate(error_data), response.status
                    except Exception as exception:
                        logger.error(f"无法转换错误数据为响应模型: {error_data}，错误信息: {exception}")
                        return cast(T, ErrorResponse.model_validate(error_data)), response.status

        except aiohttp.ClientError as e:
            logger.error(f"HTTP请求失败: URL={url}, Method={method}, Error={e}")

            # 如果是外部模式，尝试重连
            if self.external_mode:
                self._connected = False
                if await self.reconnect_mxd():
                    # 重连成功，重试请求
                    logger.info("重连成功，重试请求")
                    return await self._async_request(url, method, response_model, body)

            error_data = {"ok": False, "reason": ErrorReason.INTERNAL_ERROR, "error": str(e)}
            try:
                return response_model.model_validate(error_data), 503
            except Exception as exception:
                logger.error(f"无法转换错误数据为响应模型: {error_data}，错误信息: {exception}")
                return cast(T, ErrorResponse.model_validate(error_data)), 503

        except Exception as e:
            logger.error(f"请求失败: URL={url}, Method={method}, Body={body}, Error={e}")
            error_data = {"ok": False, "reason": ErrorReason.INTERNAL_ERROR, "error": str(e)}
            try:
                return response_model.model_validate(error_data), 500
            except Exception as exception:
                logger.error(f"无法转换错误数据为响应模型: {error_data}，错误信息: {exception}")
                return cast(T, ErrorResponse.model_validate(error_data)), 500

    async def _get(self, url: str, response_model: Type[T]) -> Tuple[T, int]:
        """
        发送异步GET请求

        Args:
            url: 请求URL
            response_model: 响应数据模型类型

        Returns:
            Tuple[响应模型实例, HTTP状态码]
        """
        return await self._async_request(url, "GET", response_model)

    async def _post(self, url: str, body: dict, response_model: Type[T]) -> Tuple[T, int]:
        """
        发送异步POST请求

        Args:
            url: 请求URL
            body: 请求体
            response_model: 响应数据模型类型

        Returns:
            Tuple[响应模型实例, HTTP状态码]
        """
        return await self._async_request(url, "POST", response_model, body)

    async def get_host_list(self) -> ApiResult[HostListResponse]:
        """
        获取主机列表

        Returns:
            包含主机ID列表的响应
        """
        return await self._get(f"/api/list", HostListResponse)

    async def get_host_info(self, host_id: str) -> ApiResult[Union[HostInfoSuccessResponse, HostInfoErrorResponse]]:
        """
        获取主机信息

        Args:
            host_id: 主机ID

        Returns:
            主机信息响应
        """
        # 对主机ID进行URL编码
        return await self._get(f"/api/info?host={host_id}", Union[HostInfoSuccessResponse, HostInfoErrorResponse])

    async def get_host_list_info(self) -> ApiResult[HostListInfoResponse]:
        """
        获取所有主机信息列表

        Returns:
            所有主机的信息列表
        """
        return await self._get(f"/api/list-info", HostListInfoResponse)

    async def get_task_result(self, host_id: str, task_id: int) -> ApiResult[TaskResult]:
        """
        获取任务执行结果

        Args:
            host_id: 主机ID
            task_id: 任务ID

        Returns:
            任务执行结果
        """
        # 对主机ID进行URL编码
        encoded_host_id = urllib.parse.quote(host_id)
        return await self._get(f"/api/result?host={encoded_host_id}&task_id={task_id}", TaskResult)

    async def until_task_complete(self, host_id: str, task_id: int, interval: int = 1, timeout: int = -1) -> TaskResult:
        """
        异步阻塞等待任务完成

        Args:
            host_id: 主机ID
            task_id: 任务ID
            interval: 轮询间隔（秒）
            timeout: 超时时间（秒），-1表示无限等待

        Returns:
            任务执行结果
        """
        timeout_remaining = timeout

        while True:
            result, _ = await self.get_task_result(host_id, task_id)

            if result.get("ok"):
                return result

            if result.get("reason") != ErrorReason.TASK_NOT_COMPLETED:
                return result

            if timeout != -1:
                timeout_remaining -= interval
                if timeout_remaining <= 0:
                    return result

            # 修复：使用interval作为休眠时间，而不是timeout
            await asyncio.sleep(interval)

    async def command_exec(self, host_id: str, command: str) -> ApiResult[AddTaskResult]:
        """
        在远程主机上执行命令

        Args:
            host_id: 主机ID
            command: 要执行的命令

        Returns:
            添加任务的结果
        """
        return await self._post(f"/api/exec", {"host": host_id, "cmd": command}, AddTaskResult)

    async def upload_file(self, host_id: str, src_path: str, target_url: str) -> ApiResult[AddTaskResult]:
        """
        将文件从远程主机上传到指定URL

        Args:
            host_id: 主机ID
            src_path: 主机上的源文件路径
            target_url: 上传目标URL

        Returns:
            添加任务的结果
        """
        return await self._post(f"/api/file", {
            "url": target_url, "host": host_id, "path": src_path, "op": "upload"
        }, AddTaskResult)

    async def download_file(self, host_id: str, src_url: str, target_path: str) -> ApiResult[AddTaskResult]:
        """
        从指定URL下载文件到远程主机

        Args:
            host_id: 主机ID
            src_url: 源文件URL
            target_path: 主机上的目标文件路径

        Returns:
            添加任务的结果
        """
        return await self._post(f"/api/file", {
            "url": src_url,
            "host": host_id,
            "path": target_path,
            "op": "download"
        }, AddTaskResult)

    async def add_file_map(self, file: str, publish_name: str) -> ApiResult[AddFileMapResponse]:
        """
        添加文件映射（将文件路径映射为发布名称）

        Args:
            file: 文件路径
            publish_name: 发布名称

        Returns:
            文件映射添加结果
        """
        logger.debug(f"添加文件映射: {file} 作为 {publish_name}")

        return await self._post(f"/api/file-map", {
            "maps": [
                {"name": publish_name, "path": file, "isdir": False}
            ]
        }, AddFileMapResponse)

    async def add_dir_map(self, dirname: str, publish_name: str) -> ApiResult[AddFileMapResponse]:
        """
        添加目录映射（将目录路径映射为发布名称）

        Args:
            dirname: 目录路径
            publish_name: 发布名称

        Returns:
            目录映射添加结果
        """
        logger.debug(f"添加目录映射: {dirname} 作为 {publish_name}")

        return await self._post(f"/api/file-map", {
            "maps": [
                {"name": publish_name, "path": dirname, "isdir": True}
            ]
        }, AddFileMapResponse)

    async def remove_file_map(self, file: str) -> ApiResult[str]:
        """
        移除文件映射

        Args:
            file: 发布名称

        Returns:
            移除结果
        """
        return await self._async_request(f"/api/file-map", "DELETE", StringResponse, {"publish_name": file})

    async def get_file_map(self) -> ApiResult[StringListResponse]:
        """
        获取所有文件映射

        Returns:
            文件映射列表
        """
        return await self._get(f"/api/file-map", StringListResponse)

    async def get_url_sub_by_ip(self, path: str, ip: str, https: bool = False) -> ApiResult[GetUrlSubResponse]:
        """
        获取指定 IP 主机的下载指定文件的 URL

        Args:
            path: 路径
            ip: IP地址
            https: 是否使用HTTPS

        Returns:
            URL替换结果
        """
        # 对参数进行URL编码
        encoded_path = urllib.parse.quote(path)
        encoded_ip = urllib.parse.quote(ip)
        return await self._get(f"/srv/url-sub/by-ip?ip={encoded_ip}&path={encoded_path}&https={https}",
                               GetUrlSubResponse)

    async def get_url_sub_by_host(self, path: str, host_id: str, https: bool = False) -> ApiResult[GetUrlSubResponse]:
        """
        获取指定 ID 主机的下载指定文件的 URL

        Args:
            path: 路径
            host_id: 主机ID
            https: 是否使用HTTPS

        Returns:
            URL替换结果
        """
        # 对参数进行URL编码
        encoded_path = urllib.parse.quote(path)
        encoded_host_id = urllib.parse.quote(host_id)
        return await self._get(f"/srv/url-sub/by-host?host={encoded_host_id}&path={encoded_path}&https={https}",
                               GetUrlSubResponse)

    async def get_remote_ip_by_host_ip(self, host_id: str) -> ApiResult[GetUrlSubResponse]:
        """
        获取获取指定 IP 服务器所在的子网下的部署服务器的 IP 地址

        Args:
            host_id: 主机ID

        Returns:
            远程IP查询结果
        """
        return await self._get(f"/srv/url-sub/remote-ip-by-host-ip?host={host_id}", GetUrlSubResponse)

    async def lsdir(self, path: str) -> ApiResult[LsdirResponse]:
        """
        列出目录内容

        Args:
            path: 目录路径

        Returns:
            目录内容列表
        """
        # 对路径进行URL编码
        encoded_path = urllib.parse.quote(path)
        return await self._get(f"/srv/fs/lsdir?path={encoded_path}", LsdirResponse)

    async def read_file(self, path: str, max_size: int) -> ApiResult[Optional[str]]:
        """
        读取文件内容

        Args:
            path: 文件路径
            max_size: 最大读取大小

        Returns:
            文件内容或None（如果读取失败）
        """
        headers = {}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"

        # 对路径进行URL编码
        encoded_path = urllib.parse.quote(path)

        try:
            session = await self._get_session()
            async with session.get(
                    f"http://{self.config.host}:{self.config.http_port}/srv/fs/read?path={encoded_path}&max_size={max_size}",
                    headers=headers
            ) as response:
                if response.status >= 400 and self.config.verbose:
                    logger.error(
                        f"读取文件失败: 路径={path}, 状态码={response.status}"
                    )

                if response.status >= 400:
                    return None, response.status

                text = await response.text()
                return text, response.status
        except Exception as e:
            logger.error(f"读取文件请求失败: 路径={path}, 错误={e}")
            return None, 500

    async def get_file_hash(
            self,
            file: str,
            algorithm: Literal["sha1", "sha256", "sha512", "md5", "xxh3"]
    ) -> Optional[str]:
        """
        获取文件哈希值

        Args:
            file: 文件路径
            algorithm: 哈希算法

        Returns:
            文件哈希值或None（如果获取失败）
        """
        # 对文件路径进行URL编码
        encoded_file = urllib.parse.quote(file)

        try:
            session = await self._get_session()
            async with session.head(
                    f"http://{self.config.host}:{self.config.http_port}/srv/file/{encoded_file}?{algorithm}=true"
            ) as response:
                if not response.ok:
                    logger.error(
                        f"获取文件哈希失败: 文件={file}, 算法={algorithm}, 状态码={response.status}"
                    )
                    return None

                return response.headers.get(f"x-hash-{algorithm}")
        except Exception as e:
            logger.error(f"获取文件哈希请求失败: 文件={file}, 算法={algorithm}, 错误={e}")
            raise
