#!/usr/bin/env python

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ootbat2',
    py_modules=['ootbat2'],
    version='0.1.4',
    description='linux low battery alerting tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='UNLICENSE',
    url='https://github.com/vesche/ootbat2',
    author='Austin Jackson',
    author_email='vesche@protonmail.com',
    install_requires=['playsound'],
    entry_points={
        'console_scripts': [
            'ootbat2=ootbat2:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Public Domain',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
    ],
)
