from setuptools import setup
from codecs import open
from os import path
__author__ = 'sroche'


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='apperian',
    version='0.1.0',
    description='Python module for interacting with the EASE APIs',
    long_description=long_description,
    url='https://github.com/sroche0/apperian-pyapi/',
    author='Shawn Roche',
    author_email='sroche@apperian.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],

    keywords=['apperian', 'ease'],
    packages=['modules'],
    install_requires=['requests'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    }
)
