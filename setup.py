"""
Project website: https://github.com/yymao/fast3tree
Copyright (c) 2015-2020 Yao-Yuan Mao (yymao)
Licensed under GPLv3

`fast3tree/fast3tree.c` is written by Peter Behroozi (http://www.peterbehroozi.com/)
 source taken from the Rockstar halo finder (https://bitbucket.org/gfcstanford/rockstar)
"""
import os
from setuptools import setup

# pylint: disable=undefined-variable

lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fast3tree')
exec(open(os.path.join(lib_path, 'version.py')).read())

setup(
    name='fast3tree',
    version=__version__,  # noqa: F821
    description='A Python wrapper of Peter Behroozi\'s fast3tree code.',
    url='https://github.com/yymao/fast3tree',
    download_url='https://github.com/yymao/fast3tree/archive/v{}.tar.gz'.format(__version__),  # noqa: F821
    author='Yao-Yuan Mao',
    author_email='yymao.astro@gmail.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    use_2to3=False,
    packages=['fast3tree'],
    install_requires=['numpy>=1.0'],
    include_package_data=True,
)
