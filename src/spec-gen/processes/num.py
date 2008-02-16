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

import pxdom

import utils

import _base

class num(_base.Process):
	""" Adds section numbers, and builds a TOC. """
	
	num = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
	
	def __init__(self, **kwargs):
		""" Create the object. """
		self.__init__(self, **kwargs)
	
	def pass1(self, Node):
		""" This takes a single argument: the current node. We have already
		checked in the generator that we have a h2–h6 element node, so that does
		not need to be checked for again. """
		n = Node.tagName[1:]
		self.num[n] += 1
		section = pxdom.Text().data = u".".join(["%i" % k for (k, v) in num.items()[:n-1]]) + u" "
		Node.insertBefore(section, Node.firstChild)