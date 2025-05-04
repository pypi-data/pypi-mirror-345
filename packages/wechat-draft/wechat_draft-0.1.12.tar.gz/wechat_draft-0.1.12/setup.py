# 开发人员： Xiaoqiang
# 微信公众号:  XiaoqiangClub
# 开发时间： 2025-04-19
# 文件名称： setup.py
# 项目描述： 项目安装配置文件
# 开发工具： PyCharm
from setuptools import setup, find_packages
from wechat_draft import (VERSION, AUTHOR, DESCRIPTION, EMAIL)

setup(
    name='wechat_draft',
    version=VERSION,  # 示例版本号
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description="https://blog.csdn.net/xiaoqiangclub/article/details/147403554",  # 项目详细描述
    long_description_content_type='text/markdown',
    url='https://gitee.com/xiaoqiangclub/wechat_draft',
    install_requires=[  # 依赖包
        'requests',
        'pillow',
    ],
    extras_require={  # 可选的额外依赖
        # Windows 平台特定依赖
        'windows': [
            'DrissionPage',
            'pypiwin32'
        ],
        # Linux 平台特定依赖
        'linux': []
    },
    packages=find_packages(),  # 自动发现所有包
    classifiers=[  # 项目分类
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',  # 指明使用的许可证
    python_requires='>=3.8',  # 指定最低 Python 版本
    zip_safe=False,  # 是否可以放心地进行 zip 安装
    entry_points={  # 命令行入口
        'console_scripts': [
            # 'xiaoqiangclub = xiaoqiangclub.cmd.xiaoqiangclub_cli:main',
        ],
    },
)
