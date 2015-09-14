"""
Project website: https://bitbucket.org/yymao/fast3tree
Copyright (c) 2015 Yao-Yuan Mao (yymao)
"""
import os
from setuptools import setup

lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fast3tree')
execfile(os.path.join(lib_path, 'make_lib.py'))
make_lib(3, True, True, lib_path)

setup(
    name='fast3tree',
    version='0.1.1',
    description='A Python wrapper of Peter Behroozi\'s fast3tree code.',
    url='https://bitbucket.org/yymao/fast3tree',
    author='Yao-Yuan Mao, Peter Behroozi',
    author_email='Yao-Yuan Mao <yymao@alumni.stanford.edu>',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    use_2to3=True,
    packages=['fast3tree'],
    package_data={
        'fast3tree': ['fast3tree.c'],
    },
    install_requires = ['numpy'],
)

