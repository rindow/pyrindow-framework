from setuptools import setup, find_packages

from os.path import join, dirname
import sys
sys.path.insert(0, join(dirname(__file__), 'lib'))
sys.path.pop(0)

packages=find_packages('lib')

setup(
    name="PyRindow-Framework",
    version="0.2.0",
    description="IoC container based Application Framework",
    author="Rindow",
    url="https://github.com/rindow/pyrindow-framework",
    author_email="rindow dot io",
    license="BSD-3-Clause",    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    keywords="ioc container framework",
    packages=packages,
    namespaces=['pyrindow.container','pyrindow.stdlib','pyrindow.bridge'],
    package_dir={'': 'lib'},
)
