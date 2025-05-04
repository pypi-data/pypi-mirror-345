#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import find_packages, setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calcpy'))
from version import __version__ as version  # noqa: E402

setup(
    name='calcpy',
    version=version,
    description='Calculation Engine in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zhiqing Xiao',
    author_email='xzq.xiaozhiqing@gmail.com',
    url='http://github.com/zhiqingxiao/calcpy',
    packages=find_packages(),
    python_requires='>=3.8',
    include_package_data=True,
    install_requires=["numpy", "pandas"],
    classifiers=[
        'Programming Language :: Python',
    ],
)
