# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='minebot',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[
        'requests',  # GitHub API에 접근하기 위한 requests 라이브러리
    ],
    description="MineBot 패키지 - 주식 데이터와 GitHub 연동",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="KoreanSniper",
    author_email="ytkoreansniper@gmail.com",
    url="https://github.com/KoreanSniper/minebot",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
