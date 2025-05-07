from setuptools import setup, find_packages

setup(
    name="nipanbo-mcp-time",           # 修改后的包名
    version="0.1.0",
    packages=find_packages(),          # 自动发现包
    install_requires=[
        "mcp",                         # 假设 FastMCP 是 PyPI 包
    ],
    entry_points={
        "console_scripts": [
            "nipanbo-mcp-time=nipanbo_mcp_time.fastmcp:main",  # 修改入口点
        ],
    },
)