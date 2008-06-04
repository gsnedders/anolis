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

from collections import deque

import html5lib
from html5lib import treebuilders, treewalkers, serializer
from lxml import etree

#import processes.index, processes.num, processes.substitutions, processes.toc, processes.xref

from processes import xref

class generator(object):
	""" This oversees all the actual work done """
	
	def process(self, input, output, processes = [xref.xref], xml_input = False, xml_output = False, **kwargs):
		""" Process the given "input" (a file-like object) writing to "output".
		Preconditions for each process are here to avoid expensive function
		calls. """
		
		if xml_input:
			# Parse the XML
			tree = etree.parse(input)
		else:
			# Parse the HTML
			parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml", etree))
			tree = parser.parse(input)
		
		# Find number of passes to do
		for process in processes:
			process(tree, **kwargs)
		
		if xml_output:
			# Serialize to XML
			rendered = etree.tostring(tree, encoding="utf-8")
		else:
			# Serialize to HTML
			walker = treewalkers.getTreeWalker("lxml")
			s = serializer.htmlserializer.HTMLSerializer(**kwargs)
			rendered = s.render(walker(tree), encoding="utf-8")
		
		# Write to the output
		output.write(rendered)