# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import find_packages
from distutils.cmd import Command
from distutils.extension import Extension
import os
import sys
import io
import subprocess
import platform
import numpy as np
from Cython.Build import cythonize
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

if "--line_trace" in sys.argv:
    line_trace = True
    print("Build with line trace enabled ...")
    sys.argv.remove("--line_trace")
else:
    line_trace = False

PACKAGE = "ultron"
NAME = "ultron"
VERSION = "0.1.8"
DESCRIPTION = "Ultron " + VERSION
AUTHOR = "kerry"
AUTHOR_EMAIL = "flaght@gmail.com"
URL = 'https://github.com/flaght'


ext_modules = [
    "ultron/sentry/Utilities/Asserts.pyx",
    "ultron/sentry/Utilities/Tools.pyx",
    "ultron/sentry/Math/MathConstants.pyx",
    "ultron/sentry/Math/ErrorFunction.pyx",
    "ultron/sentry/Math/udfs.pyx",
    "ultron/sentry/Math/Distributions/NormalDistribution.pyx",
    "ultron/sentry/Math/Distributions/norm.pyx",
    "ultron/sentry/Math/Accumulators/impl.pyx",
    "ultron/sentry/Math/Accumulators/IAccumulators.pyx",
    "ultron/sentry/Math/Accumulators/StatelessAccumulators.pyx",
    "ultron/sentry/Math/Accumulators/StatefulAccumulators.pyx",
    "ultron/sentry/Analysis/SecurityValueHolders.pyx",
    "ultron/sentry/Analysis/SeriesValues.pyx",
    "ultron/sentry/Analysis/transformer.pyx",
    "ultron/sentry/Analysis/CrossSectionValueHolders.pyx",
    "ultron/sentry/Analysis/TechnicalAnalysis/StatefulTechnicalAnalysers.pyx",
    "ultron/sentry/Analysis/TechnicalAnalysis/StatelessTechnicalAnalysers.pyx",
]

if platform.system() != "Windows":
    import multiprocessing
    n_cpu = multiprocessing.cpu_count()
else:
    n_cpu = 0
 
class version_build(Command):

    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        git_ver = git_version()[:10]
        configFile = 'ultron/sentry/__init__.py'

        file_handle = open(configFile, 'r')
        lines = file_handle.readlines()
        newFiles = []
        for line in lines:
            if line.startswith('__version__'):
                line = line.split('+')[0].rstrip()
                line = line + " + \"-" + git_ver + "\"\n"
            newFiles.append(line)
        file_handle.close()
        os.remove(configFile)
        file_handle = open(configFile, 'w')
        file_handle.writelines(newFiles)
        file_handle.close()
        
def generate_extensions(ext_modules, line_trace=False):

    extensions = []

    if line_trace:
        print("define cython trace to True ...")
        define_macros = [('CYTHON_TRACE', 1), ('CYTHON_TRACE_NOGIL', 1)]
    else:
        define_macros = []

    for pyxfile in ext_modules:
        ext = Extension(name='.'.join(pyxfile.split('/'))[:-4],
                        sources=[pyxfile],
                        define_macros=define_macros)
        extensions.append(ext)
    return extensions

ext_modules_settings = cythonize(generate_extensions(ext_modules, line_trace), 
                                 compiler_directives={'embedsignature': True, 'linetrace': line_trace}, 
                                 nthreads=n_cpu)

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
        'cython>=0.26.0',
        'numpy>=1.10.1',
        'pandas>=0.18.0',
        'scipy>=0.18.0',
        'simpleutils>=0.1.0',
        'six>=1.10.0',
        'seaborn>=0.9.0',
        'mysql-connector-python==8.0.15',
        'protobuf==3.7.0',
        'pymssql==2.1.4',
        'PyMySQL==0.9.3',
        'python-dateutil==2.8.0',
        'scikit-learn==0.20.2',
        'SQLAlchemy==1.3.1',
        'uqer==1.3.3',
        'redis==3.2.0',
        'celery==4.3.0',
        'gevent==1.4.0',
        'Twisted==18.9.0',
        'protobuf==3.7.0',
        'vine==1.3.0',
        'cvxopt>=1.2.3',
        'statsmodels>=0.10.1'
    ],
    classifiers=[],
    cmdclass={"version_build": version_build},
    ext_modules=ext_modules_settings,
    include_dirs=[np.get_include()],
)
