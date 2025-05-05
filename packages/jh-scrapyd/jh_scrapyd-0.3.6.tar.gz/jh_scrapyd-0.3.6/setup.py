from setuptools import setup, find_packages

# 定义项目的依赖
install_requires = [
    'Twisted>=20.3.0',  # scrapyd 依赖 Twisted
    'scrapy>=2.0.0',    # scrapyd 依赖 scrapy
    'redis>=5.2.1',    # scrapyd 依赖 redis
    'pytz>=2024.2',    # scrapyd 依赖 pytz
    'psutil>=6.1.1',    # scrapyd 依赖 psutil
    'pywin32; platform_system == "Windows"',  # Windows 环境下需要 pywin32
]

# 定义可选的依赖
extras_require = {
    'dev': [
        'pytest>=6.0.0',  # 测试依赖
        'pytest-cov',     # 测试覆盖率
        'flake8',         # 代码风格检查
    ],
    'docs': [
        'sphinx>=4.0.0',  # 文档生成工具
        'sphinx_rtd_theme',  # 文档主题
    ],
}

setup(
    name="jh_scrapyd",
    version="0.3.6",
    license='MIT',
    description='Preemptive scraping cluster',
    long_description=open('jh_scrapyd/README.md').read(),
    long_description_content_type='text/markdown',
    author='Mr Ye',
    author_email='mrye5869@gmail.com',
    url='https://github.com/mrye5869/jh_scrapyd',
    packages=find_packages(),
    include_package_data=True,  # 包含包数据文件（如非 Python 文件）
    install_requires=install_requires,
    extras_require=extras_require,  # 可选依赖
    python_requires='>=3.7',  # Python 版本要求
    entry_points={
        "console_scripts": [
            "jh_scrapyd=jh_scrapyd.__main__:main",  # 定义命令行入口
        ],
    },
    package_data={
        'jh_scrapyd': ['default_scrapyd.conf', 'VERSION', 'jh/*', 'jh/queue/*', 'jh/utils/*'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',  # 开发状态
        'Intended Audience :: Developers',  # 目标用户
        'License :: OSI Approved :: MIT License',  # 许可证
        'Programming Language :: Python :: 3',  # Python 版本
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',  # 操作系统支持
    ],
)