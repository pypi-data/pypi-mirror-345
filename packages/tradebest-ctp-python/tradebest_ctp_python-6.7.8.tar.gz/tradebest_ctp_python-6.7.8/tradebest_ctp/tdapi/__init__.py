"""
Trading API module for CTP
"""

import os
import platform
import sys
import ctypes

system = platform.system()
machine = platform.machine()
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

if system == "Windows":
    if machine == "AMD64":
        platform_dir = "win64"
    else:
        platform_dir = "win32"
elif system == "Linux":
    platform_dir = "linux64"
elif system == "Darwin":
    platform_dir = "macosx"
else:
    raise Exception(f"Unsupported platform: {system}")

version = "6.7.7_20240607"

package_dir = os.path.dirname(os.path.dirname(__file__))
module_path = os.path.join(package_dir, version, platform_dir)

if not os.path.exists(module_path):
    module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              version, platform_dir)

sys.path.insert(0, module_path)

if system == "Windows":
    py_version_dir = f"py3{python_version.split('.')[1]}"
    py_module_path = os.path.join(module_path, py_version_dir)
    if os.path.exists(py_module_path):
        sys.path.insert(0, py_module_path)

if system == "Linux":
    try:
        lib_path = os.path.join(module_path, "libthosttraderapi_se.so")
        if os.path.exists(lib_path):
            ctypes.CDLL(lib_path)
    except Exception as e:
        print(f"Warning: Failed to load library: {e}")

try:
    from thosttraderapi import *
    __all__ = [name for name in dir() if not name.startswith('_')]
except ImportError as e:
    print(f"Error importing thosttraderapi: {e}")
    print(f"Module path: {module_path}")
    print(f"System path: {sys.path}")
    __all__ = []
