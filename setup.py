#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import os
from pathlib import Path

import setuptools

HERE = Path(__file__).parent

__package_name__ = 'wikitalk_parser'
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def import_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_version(package_name):
    version = import_file('version',
                          os.path.join(__location__, package_name, 'version.py'))
    return version.__version__


__version__ = get_version(__package_name__)


def read_requirements(reqs_path):
    with open(reqs_path, encoding='utf8') as f:
        reqs = [line.strip() for line in f
                if not line.strip().startswith('#') and not line.strip().startswith('--')]
    return reqs


def get_extra_requires(path, add_all=True, ext='*.txt'):
    main_reqs = read_requirements(HERE / 'requirements.txt')

    extra_deps = {}
    for filename in path.glob(ext):
        if filename.name == 'requirements.txt':
            continue
        # convention of naming requirements files: requirements.{module}.txt
        package_suffix = filename.suffixes[-2].strip('.')
        reqs = list({*main_reqs, *read_requirements(filename)})
        extra_deps[package_suffix] = reqs

    if add_all:
        extra_deps['all'] = set(vv for v in extra_deps.values() for vv in v)
    return extra_deps


if __name__ == '__main__':

    setuptools.setup(name=__package_name__,
                     version=__version__,
                     author='Vladimir Gurevich',
                     description='A library for parsing Wikipedia talk pages',
                     long_description=(HERE / 'README.md').read_text(),
                     long_description_content_type='text/markdown',
                     url='https://github.com/imvladikon/wikitalk_parser',
                     # noqa
                     packages=setuptools.find_packages(exclude=(
                         'tests',
                         'tests.*',
                     )),
                     classifiers=[
                         'Programming Language :: Python :: 3',
                         'Topic :: Scientific/Engineering'
                     ],
                     python_requires='>=3.8',
                     package_dir={__package_name__: __package_name__},
                     install_requires=read_requirements(HERE / 'requirements.txt'),
                     extras_require=get_extra_requires(HERE))
