
import os
import platform
import sys
from setuptools import setup, find_packages

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

ctp_versions = [
    "6.3.15_20190220",
    "6.3.19_P1_20200106",
    "6.5.1_20200908",
    "6.6.1_P1_20210406",
    "6.6.7_20220613",
    "6.6.9_20220920",
    "6.7.0_20230209",
    "6.7.1_20230613",
    "6.7.2_20230913",
    "6.7.7_20240607",
]

default_version = ctp_versions[-1]

with open(os.path.join(default_version, "version.txt"), "r") as f:
    version = f.read().strip()

packages = find_packages()

import shutil
import glob

ctp_version = default_version
src_dir = os.path.join(os.path.dirname(__file__), ctp_version)
dst_dir = os.path.join(os.path.dirname(__file__), 'tradebest_ctp', ctp_version)

os.makedirs(dst_dir, exist_ok=True)

for plat in ['linux64', 'win32', 'win64', 'macosx']:
    src_plat_dir = os.path.join(src_dir, plat)
    dst_plat_dir = os.path.join(dst_dir, plat)
    
    if os.path.exists(src_plat_dir):
        os.makedirs(dst_plat_dir, exist_ok=True)
        
        for file in glob.glob(os.path.join(src_plat_dir, '*')):
            if os.path.isfile(file):
                shutil.copy2(file, dst_plat_dir)

if os.path.exists(os.path.join(src_dir, 'version.txt')):
    shutil.copy2(os.path.join(src_dir, 'version.txt'), dst_dir)

package_data = {
    'tradebest_ctp': [f'{ctp_version}/**/*'],
}

setup(
    name="tradebest-ctp-python",
    version=version,
    description="Python wrapper for CTP API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="TradeBest Team",
    author_email="tradebest@example.com",
    url="https://github.com/tradebest/tradebest-ctp-python",
    packages=packages,
    package_data=package_data,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.7",
    install_requires=[],
    keywords=["ctp", "futures", "trading", "api", "finance"],
)
