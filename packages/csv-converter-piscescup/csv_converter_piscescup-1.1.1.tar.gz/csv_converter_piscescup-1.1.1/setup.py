from setuptools import setup, find_packages
from INFO import DESCRIPTION

setup(
    name="csv_converter-piscescup",
    version="1.1.1",
    description=DESCRIPTION,
    author="REN YuanTong",
    author_email="renyt1621@mails.jlu.edu.cn",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "csv_converter=cli:main",  # 注册命令行工具
        ]
    },
    install_requires=[
        "pandas"
    ],
)
