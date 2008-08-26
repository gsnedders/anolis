# coding=UTF-8
# Copyright (c) 2008 Geoffrey Sneddon
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

import glob
import re
import StringIO
import os
import unittest

import html5lib
from html5lib import treebuilders, treewalkers, serializer

from lxml import etree

from specGen import generator

def get_files(*args):
	return glob.glob(os.path.join(*args))

class TestCase(unittest.TestCase):
	pass

def buildTestSuite():
	for file_name in get_files("tests", "basic", "*.src.html"):
		def testFunc(self, file_name=file_name):
			try:
				# Get the input
				input = open(file_name, "r")
				parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml", etree))
				tree = parser.parse(input)
				
				# Get the expected result
				expected = open(file_name[:-9] + ".html", "r")
				
				# Run the spec-gen
				gen = generator.generator()
				gen.process(tree, set(["sub", "xref", "toc"]))
				
				# Get the output
				walker = treewalkers.getTreeWalker("lxml")
				s = serializer.htmlserializer.HTMLSerializer()
				output = s.render(walker(tree), encoding="utf-8")
				
				# Run the test
				self.assertEquals(output, expected.read())
				
				# Close the files
				input.close()
				expected.close()
			except IOError, err:
				self.fail(err)
		setattr(TestCase, "test_%s" % (file_name), testFunc)

def main():
	buildTestSuite()
	unittest.main()

if __name__ == "__main__":
	main()