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

import StringIO
from collections import deque

import html5lib
from html5lib import treebuilders, treewalkers, serializer
import pxdom

#import processes.index, processes.num, processes.substitutions, processes.toc, processes.xref
import processes.num
import utils

class generator(object):
	""" This oversees all the actual work done """
	
	def process(self, input, output=StringIO.StringIO(), **kwargs):
		""" Process the given "input" (a file-like object) writing to "output".
		Preconditions for each process are here to avoid expensive function
		calls. """
		
		# Parse the HTML
		parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom", pxdom))
		Document = parser.parse(input)
		
		# Create processes
		num = processes.num.num(**kwargs)
		
		# Pass 1
		for Node in descendants(Document):
			if Node.NodeType == 1 and Node.tagName in (u"h2", u"h3", u"h4", u"h5", u"h6"):
				if num.enabled and not utils.elementHasClass(Node, u"no-num"):
					num.pass1(Node)
		
		# Convert back to HTML
		walker = treewalkers.getTreeWalker("dom")
		s = serializer.htmlserializer.HTMLSerializer(**kwargs)
		rendered = s.render(walker(Document))
		
		# Write to the output
		output.write(rendered)

	def descendants(self, Node):
		""" This gets a list of all descendants of a Node, no matter how deep. """
		
		results = [];
		child = deque([Node]);
		while child:
			working = child.popleft()
			child.extend(working.childNodes);
			results.append(working)
		return results