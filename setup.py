"""
Project website: https://bitbucket.org/yymao/fast3tree
Copyright (c) 2015 Yao-Yuan Mao (yymao)
"""
import os
from setuptools import setup

lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fast3tree')
exec(open(os.path.join(lib_path, 'make_lib.py')).read())
make_lib(3, True, True, lib_path)

setup(
    name='fast3tree',
    version='0.2.0',
    description='A Python wrapper of Peter Behroozi\'s fast3tree code.',
    url='https://bitbucket.org/yymao/fast3tree',
    download_url = 'https://bitbucket.org/yymao/fast3tree/get/v0.2.0.tar.gz',
    author='Yao-Yuan Mao',
    author_email='yymao.astro@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    use_2to3=False,
    packages=['fast3tree'],
    package_data={
        'fast3tree': ['fast3tree.c', get_lib_name(3, True)],
    },
    install_requires = ['numpy'],
)

