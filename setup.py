"""
Licensed under GPLv3

`fast3tree/fast3tree.c` is written by Peter Behroozi (http://www.peterbehroozi.com/)
 source taken from the Rockstar halo finder (https://bitbucket.org/gfcstanford/rockstar)
"""
import os
from setuptools import setup

lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fast3tree')
exec(open(os.path.join(lib_path, 'version.py')).read()) # pylint: disable=W0122
exec(open(os.path.join(lib_path, 'make_lib.py')).read()) # pylint: disable=W0122
make_lib(3, True, True, lib_path)

setup(
    name='fast3tree',
    version=__version__,
    description='A Python wrapper of Peter Behroozi\'s fast3tree code.',
    url='https://bitbucket.org/yymao/fast3tree',
    download_url = 'https://bitbucket.org/yymao/fast3tree/get/v{}.tar.gz'.format(__version__),
    author='Yao-Yuan Mao',
    author_email='yymao.astro@gmail.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
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
