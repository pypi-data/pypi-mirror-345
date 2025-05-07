# setup.py
import setuptools
from pathlib import Path

# 1. 读取 requirements.txt，过滤掉空行和注释
here = Path(__file__).parent
req_txt = here / "requirements.txt"
install_requires = []
if req_txt.exists():
    for line in req_txt.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            install_requires.append(line)

# 2. 调用 setuptools.setup
setuptools.setup(
    name="multicloud-storage",              # pip install 时的包名
    version="0.1.0",
    description="统一操作 MinIO/OSS/S3 兼容存储的工具包",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/your_username/multicloud-storage",
    packages=setuptools.find_packages(),     # 会找到 multicloud_storage/core, clients
    install_requires=install_requires,       # 动态从 requirements.txt 加载
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
