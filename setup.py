#!/usr/bin/env python

# Copyright 2015 Jeff Trawick, http://emptyhammock.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

import os
import sys

from setuptools import setup

with open('stacktraces/__init__.py') as f:
    line_1 = f.readline()
    _, _, VERSION = line_1.replace("'", "").strip().split(' ')

if sys.argv[-1] == 'version':
    print('Version: %s' % VERSION)
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

setup(
    author='Jeff Trawick',
    author_email='trawick@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python 2.7',
        'Programming Language :: Python 3',
        'Topic :: Software Development :: Debuggers',
    ],
    description='Stack trace representation in Python',
    install_requires=['pytz', 'six'],
    license="ASL 2.0",
    name='stacktraces',
    packages=['stacktraces', 'stacktraces.analyze', 'stacktraces.native', 'stacktraces.python'],
    scripts=['collect.py', 'describe.py', 'describe_python_log.py', 'describe_python_stacktrace.py'],
    url='https://github.com/trawick/stacktraces.py',
    version=VERSION,
)
