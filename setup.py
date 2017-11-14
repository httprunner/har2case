#encoding: utf-8
import io

from har2case import __version__
from setuptools import find_packages, setup

with io.open("README.rst", encoding='utf-8') as f:
    long_description = f.read()

install_requires = open("requirements.txt").readlines()

setup(
    name='har2case',
    version=__version__,
    description='Convert HAR(HTTP Archive) to YAML/JSON testcases for HttpRunner.',
    long_description=long_description,
    author='Leo Lee',
    author_email='mail@debugtalk.com',
    url='https://github.com/HttpRunner/har2case',
    license='MIT',
    packages=find_packages(exclude=['test.*', 'test']),
    package_data={},
    keywords='har converter yaml json',
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    entry_points={
        'console_scripts': [
            'har2case=har2case.cli:main'
        ]
    }
)
