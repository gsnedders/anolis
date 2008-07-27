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
from lxml import etree

from html5lib.constants import spaceCharacters

ids = {}

spaceCharacters = u"".join(spaceCharacters)
spacesRegex = re.compile(u"[%s]+" % spaceCharacters)

heading_content = frozenset(["h1", "h2", "h3", "h4", "h5", "h6", "header"])
sectioning_content = frozenset(["body", "section", "nav", "article", "aside"])
sectioning_root = frozenset(["blockquote", "figure", "td", "datagrid"])

non_sgml_name = re.compile("[^A-Za-z0-9\-_:.]+")

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
	
	source = source.strip(spaceCharacters).lower()
	if source == u"":
		source = u"generatedID"
	elif Element.getroottree().docinfo.public_id in \
		(u"-//W3C//DTD HTML 4.0//EN",
		 u"-//W3C//DTD HTML 4.0 Transitional//EN",
		 u"-//W3C//DTD HTML 4.0 Frameset//EN",
		 u"-//W3C//DTD HTML 4.01//EN",
		 u"-//W3C//DTD HTML 4.01 Transitional//EN",
		 u"-//W3C//DTD HTML 4.01 Frameset//EN",
		 u"ISO/IEC 15445:2000//DTD HyperText Markup Language//EN",
		 u"ISO/IEC 15445:2000//DTD HTML//EN",
		 u"-//W3C//DTD XHTML 1.0 Strict//EN",
		 u"-//W3C//DTD XHTML 1.0 Transitional//EN",
		 u"-//W3C//DTD XHTML 1.0 Frameset//EN",
		 u"-//W3C//DTD XHTML 1.1//EN"):
		source = non_sgml_name.sub(u"-", source)
		if not source[0].isalpha():
			source = u"x" + source
	else:
		source = spacesRegex.sub(u"-", source)
	
	source = source.strip(u"-")
	
	# Initally set the id to the source
	id = source
	
	i = 0
	while getElementById(Element.getroottree().getroot(), id) is not None:
		id = source + u"-" + repr(i)
		i += 1
	
	ids[Element.getroottree().getroot()][id] = Element
	
	return id

def textContent(Element):
	return etree.tostring(Element, encoding=unicode, method='text', with_tail=False)

def getElementById(base, id):
	if base in ids:
		try:
			return ids[base][id]
		except KeyError:
			return None
	else:
		ids[base] = {}
		for element in base.iter(tag=etree.Element):
			if element.get("id"):
				ids[base][element.get("id")] = element
		return getElementById(base, id)

def escapeXPathString(string):
	return u"concat('', '%s')" % string.replace("'", "', \"'\", '")

class SpecGenException(Exception):
	"""Generic spec-gen error."""
	pass
