#! /usr/bin/env python3

from setuptools import setup

setup(
    name='xmldom',
    use_scm_version={
        "local_scheme": "node-and-timestamp"
    },
    setup_requires=['setuptools_scm'],
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info at homeinfo dot de>',
    maintainer='Richard Neumann',
    maintainer_email='<r dot neumann at homeinfo period de>',
    install_requires=['pyxb'],
    py_modules=['xmldom'],
    license='GPLv3',
    description='An XML DOM library using PyXB.'
)
