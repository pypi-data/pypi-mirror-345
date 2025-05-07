from setuptools import setup, find_packages

setup(
    name="nipanbo-mcp-time",           # PyPI 包名（连字符）
    version="0.3.0",
    packages=find_packages(),          # 自动发现包
    install_requires=[
        "mcp",                         # 假设 FastMCP 是 PyPI 包
    ],
    entry_points={
        "console_scripts": [
            "nipanbo-mcp-time=nipanbo_mcp_time.fastmcp",  # 直接运行脚本
        ],
    },
)

# rm -rf dist/*
# python setup.py sdist bdist_wheel
# twine upload dist/*


# pypi-AgEIcHlwaS5vcmcCJGQ0OGFjMTJkLTA1MjctNDc4NS05ZmEyLTE2YjQ5NTQ2Yjk2NgACKlszLCIwYWZiODA1ZC05YTY1LTQ0OWYtYTBmMS0zNDU4ZTZhYjNjMGMiXQAABiBUbrfdb3yMd0v656DtYFSYbocTedignhNoXe0m9kYebg