# setup.py
from setuptools import setup, find_packages

setup(
    name='ORCIdentify',
    version='0.1.0',
    description='A ocr api client to identify graphical captcha.',
    author='HeJinQing',
    author_email='q.w.e.a.s@icloud.com',
    packages=find_packages(),
    install_requires=[
        "requests"
        # 列出你的库依赖的其他库
    ],
)