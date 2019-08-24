# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages
import io
import os

PACKAGE = "ultron"
NAME = "ultron"
VERSION = "0.1.5"
DESCRIPTION = "Ultron " + VERSION
AUTHOR = "kerry"
AUTHOR_EMAIL = "flaght@gmail.com"
URL = 'https://github.com/flaght'


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license="Apache License",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy==1.16.2',
        'pandas==0.24.1',
        'mysql-connector-python==8.0.15',
        'protobuf==3.7.0',
        'pymssql==2.1.4',
        'PyMySQL==0.9.3',
        'python-dateutil==2.8.0',
        'scikit-learn==0.20.2',
        'scipy==1.2.1',
        'SQLAlchemy==1.3.1',
        'uqer==1.3.3',
        'redis==3.2.0',
        'celery==4.3.0',
        'gevent==1.4.0',
        'Twisted==18.9.0',
        'protobuf==3.7.0',
        'vine==1.3.0'
    ]
)
