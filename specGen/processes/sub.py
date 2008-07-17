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

import re
import time
from lxml import etree

from specGen import utils

year = re.compile(r"\[YEAR(:[^\]]*)?\]")
year_sub = time.strftime("%Y", time.gmtime())
year_identifier = u"[YEAR"

date = re.compile(r"\[DATE(:[^\]]*)?\]")
date_sub = time.strftime("%d %B %Y", time.gmtime())
date_identifier = u"[DATE"

cdate = re.compile(r"\[CDATE(:[^\]]*)?\]")
cdate_sub = time.strftime("%", time.gmtime())
cdate_identifier = u"[DATE"

string_subs = ((year, year_sub, year_identifier),
               (date, date_sub, date_identifier),
               (cdate, cdate_sub, cdate_identifier))

class sub(object):
	"""Perform substitutions."""
	
	def __init__(self, ElementTree, **kwargs):
		self.stringSubstitutions(ElementTree, **kwargs)
		self.commentSubstitutions(ElementTree, **kwargs)
	
	def stringSubstitutions(self, ElementTree, **kwargs):
		for node in ElementTree.iter():
			for regex, sub, identifier in string_subs:
				if node.text is not None and identifier in node.text:
					node.text = regex.sub(sub, node.text)
				if node.tail is not None and identifier in node.tail:
					node.tail = regex.sub(sub, node.tail)
				for name, value in node.attrib.items():
					if identifier in value:
						node.attrib[name] = regex.sub(sub, value)
	
	def commentSubstitutions(self, ElementTree, **kwargs):
		pass
