# @Coding: UTF-8
# @Time: 2025/3/26 21:16
# @Author: xieyang_ls
# @Filename: setup.py

from setuptools import setup, find_packages

setup(
    name="pyutils_spirit",  # 包名（PyPI唯一标识）
    version="1.5.2.0",  # 版本号（每次上传需更新）
    author="Spirit",
    author_email="2969643689@qq.com",
    description="A Small Python package",
    packages=find_packages(),  # 自动发现所有包
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Python版本要求
    keywords=['python', 'pyutils', 'IOC', 'DI', 'WebSocket', 'Container']
)
