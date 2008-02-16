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

from html5lib.constants import spaceCharacters
spaceCharacters = u"".join(spaceCharacters)
spacesRegex = re.compile(u"[%s]+" % spaceCharacters)

def splitOnSpaces(string):
	return spacesRegex.split(string)

def elementHasClass(Element, class_name):
	if Element.getAttribute(u"class"):
		if class_name in splitOnSpaces(Element.getAttribute(u"class")):
			return True
	return False

def generateID(Element):
	if Element.getAttribute(u"id"):
		return Element.getAttribute(u"id")
	elif Element.getAttribute(u"title"):
		source = Element.getAttribute(u"title")
	#else Element.textContent:
	#	source = Element.textContent
	
	source = source.strip(spaceCharacters)
	if source == u"":
		source = "generatedID"
	else:
		source = spacesRegex.sub(u"-", source)
	
	# Initally set the id to the source
	id = source
	
	if Element.ownerDocument:
		i = 0
		while Element.ownerDocument.getElementById(id):
			id = source + u"-" + repr(i)
	
	return id