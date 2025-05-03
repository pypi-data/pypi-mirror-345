# _*_ coding : utf-8 _*_
# @Time : 2025-05-03 11:23
# @Author : liubiao
# @File : setup.py
# @Project : mcp-weather-example

from setuptools import setup, find_packages

setup(
    name='weather-mcp-server',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # 列出所有依赖
        'requests',
        'mcp',
        'httpx'
    ],
    # 其他元数据，如作者、描述、URL等
    author='Your Name',
    author_email='external_ll@163.com',
    description='weather test',
    url='http://github.com/your_username/your_package_name',
)