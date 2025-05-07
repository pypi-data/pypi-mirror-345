from setuptools import setup, find_packages

setup(
    name="nipanbo-mcp-time1",           # 修改后的包名
    version="0.2.0",
    packages=find_packages(),          # 自动发现包
    install_requires=[
        "mcp",                         # 假设 FastMCP 是 PyPI 包
    ],
    entry_points={
        "console_scripts": [
            "nipanbo-mcp-time1=nipanbo_mcp_time.fastmcp",  # 修改入口点
        ],
    },
)

# python setup.py sdist bdist_wheel

# pypi-AgEIcHlwaS5vcmcCJGQ0OGFjMTJkLTA1MjctNDc4NS05ZmEyLTE2YjQ5NTQ2Yjk2NgACKlszLCIwYWZiODA1ZC05YTY1LTQ0OWYtYTBmMS0zNDU4ZTZhYjNjMGMiXQAABiBUbrfdb3yMd0v656DtYFSYbocTedignhNoXe0m9kYebg