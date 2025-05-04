import os
import platform
import sys
from setuptools import setup, find_packages, Command
from setuptools.command.build_py import build_py
import shutil

# 版本信息
VERSION = "0.1.5"

# 确定当前平台 (支持通过环境变量强制指定平台)
current_system = os.environ.get("FORCE_PLATFORM_SYSTEM") or platform.system().lower()
current_machine = os.environ.get("FORCE_PLATFORM_MACHINE") or platform.machine().lower()

if current_machine == "x86_64":
    current_machine = "x86_64"
elif current_machine == "amd64":
    current_machine = "x86_64"
elif current_machine in ["arm64", "aarch64"]:
    current_machine = "arm64"
else:
    print(f"警告: 不支持的处理器架构: {current_machine}")

# 根据系统和架构确定平台标识
if current_system == "linux":
    platform_id = f"linux-{current_machine}"
elif current_system == "darwin":
    platform_id = f"darwin-{current_machine}"
elif current_system == "windows":
    platform_id = f"windows-{current_machine}"
else:
    print(f"警告: 不支持的操作系统: {current_system}")
    platform_id = "unknown"


# 自定义build_py命令来控制要包含的二进制文件
class CustomBuildPy(build_py):
    def run(self):
        # 运行标准的build_py
        build_py.run(self)
        
        # 确定构建目录中的bin路径
        bin_target_dir = os.path.join(self.build_lib, "mxlite", "bin")
        os.makedirs(bin_target_dir, exist_ok=True)
        
        # 保留占位符文件
        placeholder_path = os.path.join("mxlite", "bin", ".placeholder")
        if os.path.exists(placeholder_path):
            shutil.copy2(placeholder_path, os.path.join(bin_target_dir, ".placeholder"))
        
        # 清理构建目录中的所有mxd文件（我们只想保留平台特定的一个）
        for file in os.listdir(bin_target_dir):
            if file.startswith("mxd-"):
                os.remove(os.path.join(bin_target_dir, file))
        
        # 复制当前平台对应的mxd二进制文件
        if platform_id != "unknown":
            mxd_filename = f"mxd-{platform_id}"
            if current_system == "windows":
                mxd_filename += ".exe"
            
            src_path = os.path.join("mxlite", "bin", mxd_filename)
            if os.path.exists(src_path):
                dst_path = os.path.join(bin_target_dir, mxd_filename)
                shutil.copy2(src_path, dst_path)
                print(f"为平台 {platform_id} 添加MXD二进制文件: {mxd_filename}")
            else:
                print(f"警告: 未找到对应平台的MXD二进制文件: {src_path}")
        
        # 复制所有mxa文件
        for file in os.listdir(os.path.join("mxlite", "bin")):
            if file.startswith("mxa-"):
                src_path = os.path.join("mxlite", "bin", file)
                dst_path = os.path.join(bin_target_dir, file)
                shutil.copy2(src_path, dst_path)
                print(f"添加MXA二进制文件: {file}")
        
        # 列出最终打包的文件
        print(f"构建目录中的文件: {os.listdir(bin_target_dir)}")


# 平台特定的wheel标签
if "bdist_wheel" in sys.argv and platform_id != "unknown":
    # 强制wheel使用平台标签
    from setuptools.command.bdist_wheel import bdist_wheel
    
    class BdistWheelPlatform(bdist_wheel):
        def finalize_options(self):
            super().finalize_options()
            
            # 设置特定平台
            if current_system == "linux":
                self.root_is_pure = False
                self.plat_name = f"manylinux2014_{current_machine}"
            elif current_system == "darwin":
                self.root_is_pure = False
                # 设置 macOS 最低兼容版本为 OSX12 (macOS Monterey)
                self.plat_name = f"macosx_12_0_{current_machine}"
                print(f"设置macOS平台标签为: {self.plat_name}")
            elif current_system == "windows":
                self.root_is_pure = False
                self.plat_name = f"win_{current_machine}"
        
        def get_tag(self):
            # 获取原始标签
            python_tag, abi_tag, platform_tag = super().get_tag()
            
            # 修改 Python 标签为通用版本
            if not self.root_is_pure:
                # 使用 'cp310' 标签支持 Python 3.10 及以上版本
                python_tag = 'cp310'
                # 使用通用 ABI 标签 (none) 替代特定版本的 ABI 标签 (cp310)
                abi_tag = 'none'
                
                # 显式强制平台标签
                if current_system == "darwin":
                    platform_tag = f"macosx_12_0_{current_machine}"
                    print(f"强制设置platform_tag为: {platform_tag}")
                elif current_system == "linux":
                    if current_machine == "arm64":
                        platform_tag = f"manylinux2014_aarch64"
                        print(f"强制设置platform_tag为: {platform_tag}")
                    else:
                        platform_tag = f"manylinux2014_{current_machine}"
                    print(f"强制设置platform_tag为: {platform_tag}")
                elif current_system == "windows":
                    if current_machine == "x86_64":
                        platform_tag = f"win_amd64"
                    else:
                        platform_tag = f"win_{current_machine}"
                    print(f"强制设置platform_tag为: {platform_tag}")
            
            return python_tag, abi_tag, platform_tag
    
    # 注册自定义命令
    command_overrides = {
        "bdist_wheel": BdistWheelPlatform,
        "build_py": CustomBuildPy
    }
else:
    command_overrides = {
        "build_py": CustomBuildPy
    }

# 设置包含的包和数据文件
packages = find_packages()
package_data = {
    "mxlite": ["bin/*"],  # 使用通配符包含所有bin文件，但实际文件会由CustomBuildPy控制
}

# 准备setup参数
setup_args = {
    "name": "mxlite-sdk",
    "version": VERSION,
    "author": "PEScn",
    "author_email": "pescn@115lab.club",
    "description": "Python SDK for mxlite",
    "long_description": open("README.md", "r", encoding="utf-8").read() if os.path.exists("README.md") else "",
    "long_description_content_type": "text/markdown",
    "url": "https://github.com/EM-GeekLab/mxlite-python-sdk",
    "packages": packages,
    "package_data": package_data,
    "include_package_data": True,
    "python_requires": ">=3.10",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    "cmdclass": command_overrides,
}

# 执行setup
setup(**setup_args)