##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup
"""
from __future__ import absolute_import
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='m01.fake',
    version='3.0.5',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description="Fake MongoDB implementation",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license="ZPL 2.1",
    keywords="mongoDB mongo fake",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Database',
    ],
    url='http://pypi.python.org/pypi/m01.fake',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    extras_require=dict(
        test=[
            'zope.testing',
        ],
        stub=[
            'm01.stub',
            ],
        ),
    install_requires=[
        'setuptools',
        'six',
        'future',
        'sentinels',
        'pymongo',
        ],
    tests_require = [
        'zope.testing',
        ],
    test_suite = 'm01.fake.tests.test_suite',
    include_package_data=True,
    zip_safe=False,
    )
