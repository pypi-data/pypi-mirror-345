from enum import Enum

from pydantic import BaseModel
from typing import Dict, List, Union, Optional, Any, Literal


# 操作错误类型
class ErrorReason(str, Enum):
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_NOT_COMPLETED = "TASK_NOT_COMPLETED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# 基础响应模型
class BaseResponse(BaseModel):
    ok: bool


# 错误响应模型
class ErrorResponse(BaseResponse):
    ok: bool = False
    reason: str
    error: Optional[str] = None


# 主机列表响应
class HostListResponse(BaseModel):
    ok: bool = True
    sessions: List[str]


# 主机额外信息 - 网络接口
class NetworkInterface(BaseModel):
    mac_address: str
    mtu: int
    ip: List[Dict[str, Any]]  # 可以进一步细化为IP地址类型


# 主机额外信息 - 块设备
class BlockDevice(BaseModel):
    maj_min: str
    disk_seq: int
    name: str
    kname: str
    model: Optional[str]
    size: int
    removable: bool
    uuid: Optional[str]
    wwid: Optional[str]
    readonly: bool
    path: Optional[str]

    path_by_seq: Optional[str] = None
    subsystem: Optional[str] = None

    class Config:
        extra = "ignore"  # 忽略额外字段

# 主机额外信息 - 挂载点
class MountPoint(BaseModel):
    kind: Literal["HDD", "SSD", "Unknown"]
    device_name: str
    file_system: str
    mount_point: str
    total_space: int
    is_removeable: Optional[bool] = None
    is_read_only: bool


# 主机额外信息 - CPU
class CpuInfo(BaseModel):
    names: List[str]
    vendor_id: str
    brand: str


# 主机额外信息 - 额外信息
class UtsInfo(BaseModel):
    sysname: str
    nodename: str
    release: str
    version: str
    machine: str
    domainname: str


# 主机额外信息 - 系统信息
class SystemInfo(BaseModel):
    total_memory: int
    name: Optional[str]
    hostname: Optional[str]
    kernel_version: Optional[str]
    cpus: List[CpuInfo]
    mnts: List[MountPoint]
    nics: List[NetworkInterface]
    blks: List[BlockDevice]
    uts: UtsInfo


# 主机额外信息 - 套接字信息
class SocketInfo(BaseModel):
    local_addr: str
    remote_addr: str


# 主机额外信息
class HostExtraInfo(BaseModel):
    socket_info: SocketInfo
    controller_url: str
    system_info: SystemInfo
    envs: List[str]
    session_id: str


# 主机信息成功响应
class HostInfoSuccessResponse(BaseModel):
    ok: bool = True
    host: str
    info: HostExtraInfo


# 主机信息失败响应
class HostInfoErrorResponse(BaseModel):
    ok: bool = False
    host: str
    info: Optional[HostExtraInfo] = None


# 主机信息响应
class HostInfoResponse(BaseModel):
    @classmethod
    def model_validate(cls, obj: Any) -> Union[HostInfoSuccessResponse, HostInfoErrorResponse]:
        if obj.get("ok") is True:
            return HostInfoSuccessResponse.model_validate(obj)
        else:
            return HostInfoErrorResponse.model_validate(obj)
    
    @classmethod
    def parse_obj(cls, obj: Any) -> Union[HostInfoSuccessResponse, HostInfoErrorResponse]:
        if obj.get("ok") is True:
            return HostInfoSuccessResponse.parse_obj(obj)
        else:
            return HostInfoErrorResponse.parse_obj(obj)


# 主机信息列表的单个主机信息
class HostListInfoItem(BaseModel):
    host: str
    info: HostExtraInfo


# 主机信息列表响应
class HostListInfoResponse(BaseModel):
    ok: bool = True
    hosts: List[HostListInfoItem]


# 命令执行响应载荷
class CommandExecutionPayload(BaseModel):
    type: Literal["CommandExecutionResponse"]
    stdout: str
    stderr: str
    code: int


# 文件操作响应载荷
class FileOperationPayload(BaseModel):
    type: Literal["FileOperationResponse"]
    hash: Optional[str]
    success: bool


# 空响应载荷
class NonePayload(BaseModel):
    type: Literal["None"]


# 任务结果载荷联合类型
class TaskResultPayload(BaseModel):
    payload: Union[CommandExecutionPayload, FileOperationPayload, NonePayload]


# 任务成功响应
class TaskSuccessResponse(BaseResponse):
    ok: bool = True
    payload: TaskResultPayload


# 完整任务结果
class TaskResult(BaseModel):
    @classmethod
    def model_validate(cls, obj: Any) -> Union[TaskSuccessResponse, ErrorResponse]:
        if obj.get("ok") is True:
            return TaskSuccessResponse.model_validate(obj)
        else:
            return ErrorResponse.model_validate(obj)
    
    @classmethod
    def parse_obj(cls, obj: Any) -> Union[TaskSuccessResponse, ErrorResponse]:
        if obj.get("ok") is True:
            return TaskSuccessResponse.parse_obj(obj)
        else:
            return ErrorResponse.parse_obj(obj)


# 添加任务成功响应
class AddTaskSuccessResponse(BaseResponse):
    ok: bool = True
    task_id: int


# 添加任务结果
class AddTaskResult(BaseModel):
    @classmethod
    def model_validate(cls, obj: Any) -> Union[AddTaskSuccessResponse, ErrorResponse]:
        if obj.get("ok") is True:
            return AddTaskSuccessResponse.model_validate(obj)
        else:
            return ErrorResponse.model_validate(obj)
    
    @classmethod
    def parse_obj(cls, obj: Any) -> Union[AddTaskSuccessResponse, ErrorResponse]:
        if obj.get("ok") is True:
            return AddTaskSuccessResponse.parse_obj(obj)
        else:
            return ErrorResponse.parse_obj(obj)


# URL替换响应
class GetUrlSubResponse(BaseModel):
    ok: bool
    error: Optional[str]
    urls: List[str]


# 目录列表结果
class DirListingResult(BaseModel):
    files: List[str]
    subdirs: List[str]
    is_file: bool
    is_symlink: bool
    size: int


# 目录列表成功响应
class LsdirSuccessResponse(BaseModel):
    ok: bool = True
    error: None = None
    existed: bool = True
    result: DirListingResult


# 目录列表错误响应
class LsdirErrorResponse(BaseModel):
    ok: bool = False
    existed: bool
    error: str
    result: None = None


# 目录列表响应
class LsdirResponse(BaseModel):
    @classmethod
    def model_validate(cls, obj: Any) -> Union[LsdirSuccessResponse, LsdirErrorResponse]:
        if obj.get("ok") is True:
            return LsdirSuccessResponse.model_validate(obj)
        else:
            return LsdirErrorResponse.model_validate(obj)
    
    @classmethod
    def parse_obj(cls, obj: Any) -> Union[LsdirSuccessResponse, LsdirErrorResponse]:
        if obj.get("ok") is True:
            return LsdirSuccessResponse.parse_obj(obj)
        else:
            return LsdirErrorResponse.parse_obj(obj)


# 文件映射项
class FileMapItem(BaseModel):
    path: str
    name: str
    isdir: Optional[bool] = None


# 添加文件映射请求
class AddFileMapRequest(BaseModel):
    maps: List[FileMapItem]


# 文件映射操作结果项
class FileMapResultItem(BaseModel):
    name: str
    ok: bool
    err: Optional[str] = None


# 添加文件映射响应
class AddFileMapResponse(BaseModel):
    result: List[FileMapResultItem]


class StringResponse(BaseModel):
    data: str


class StringListResponse(BaseModel):
    data: List[str]
