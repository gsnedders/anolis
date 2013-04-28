#!/usr/bin/env python
# coding=UTF-8
# Copyright (c) 2009 Geoffrey Sneddon
#               2013 Ms2ger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
requires = [line for line in open(os.path.join(here, 'requirements.txt'))
            if line.strip()]

setup(
    # Basic project info
    name = "anolis",
    version = "1.3pre",
    packages = ["anolislib", "anolislib/processes"],
    scripts = ["anolis"],
    
    # Useless metadata cruft
    author = "Geoffrey Sneddon",
    author_email = "geoffers@gmail.com",
    maintainer = "Ms2ger",
    maintainer_email = "Ms2ger@gmail.com",
    url = "https://bitbucket.org/ms2ger/anolis/",
    license = "MIT",
    description = "HTML document post-processor",
    long_description = """Anolis is an HTML document post-processor that takes
                          an input HTML file, adds section numbers, a table
                          of contents, and cross-references, and writes the
                          output to another file.""",
    download_url = "https://bitbucket.org/ms2ger/anolis/downloads",
    install_requires = requires,
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Text Processing :: Markup :: HTML"
    ]
)
