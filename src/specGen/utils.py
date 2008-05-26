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
	if Element.get("class") and class_name in splitOnSpaces(Element.get("class")):
		return True
	else:
		return False

def generateID(Element):
	if Element.get(u"id"):
		return Element.get(u"id")
	elif Element.get(u"title"):
		source = Element.get(u"title")
	elif textContent(Element):
		source = textContent(Element)
	else:
		source = u""
	
	source = source.strip(spaceCharacters)
	if source == u"":
		source = u"generatedID"
	else:
		source = spacesRegex.sub(u"-", source)
	
	# Initally set the id to the source
	id = source
	
	i = 0
	while getElementById(Element, id):
		id = source + u"-" + repr(i)
	
	return id

def textContent(Element):
	return u"".join(Element.xpath("child::text()"))

def getElementById(Document, id):
	try:
		return Document.xpath("//*[@id = " + escapeXPathString(id) + "]")[0]
	except IndexError:
		return None

def escapeXPathString(string):
	return u"concat('', '" + string.replace("'", "', \"'\", '") + u"')"
