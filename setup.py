#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='cloudseeder',
    version='0.1.0',
    description='Custom resources for CloudFormation and Troposphere',
    author='Chaz Schlarp',
    license='MIT',
    author_email='schlarpc@gmail.com',
    url='https://github.com/schlarpc/cloudseeder',
    keywords=['aws', 'amazon', 'amazon web services', 'cloudformation', 'cfn', 'troposphere'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(where='src', exclude=('test',)),
    package_dir={'': 'src'},
    install_requires=[
        'attrs',
        'awscli',
        'backports.functools_lru_cache; python_version < "3.3"',
        'boto3',
        'requests',
        'troposphere',
    ],
    setup_requires=[
        'pytest-runner>=3.0,<4',
    ],
    tests_require=[
        'mock',
        'pytest',
        'pytest-cov',
    ],
    extras_require={
        'docs': ['Markdown', 'Jinja2', 'pygments'],
    },
)
