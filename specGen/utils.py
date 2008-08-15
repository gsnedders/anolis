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
import sys
from lxml import etree

from html5lib.constants import spaceCharacters

ids = {}

spaceCharacters = u"".join(spaceCharacters)
spacesRegex = re.compile(u"[%s]+" % spaceCharacters)

heading_content = frozenset([u"h1", u"h2", u"h3", u"h4", u"h5", u"h6", u"header"])
sectioning_content = frozenset([u"body", u"section", u"nav", u"article", u"aside"])
sectioning_root = frozenset([u"blockquote", u"figure", u"td", u"datagrid"])

non_sgml_name = re.compile("[^A-Za-z0-9_:.]+")

if sys.maxunicode == 0xFFFF:
	# UTF-16 Python
	non_ifragment = re.compile(u"([\u0000-\u0020\u0022\u0023\u0025\\\u002D\u003C\u003E\u005B-\u005E\u0060\u007B-\u007D\u007F-\u0099\uD800-\uF8FF\uFDD0-\uFDDF\uFFF0-\uFFFF]|\U0001FFFE|\U0001FFFF|\U0002FFFE|\U0002FFFF|\U0003FFFE|\U0003FFFF|\U0004FFFE|\U0004FFFF|\U0005FFFE|\U0005FFFF|\U0006FFFE|\U0006FFFF|\U0007FFFE|\U0007FFFF|\U0008FFFE|\U0008FFFF|\U0009FFFE|\U0009FFFF|\U000AFFFE|\U000AFFFF|\U000BFFFE|\U000BFFFF|\U000CFFFE|\U000CFFFF|\uDB3F[\uDFFE-\uDFFF]|[\uDB40-\uDB43][\uDC00-\uDFFF]|\uDB7F[\uDFFE-\uDFFF]|[\uDB80-\uDBFF][\uDC00-\uDFFF])+")
else:
	# UTF-32 Python
	non_ifragment = re.compile(u"[^A-Za-z0-9._~!$&'()*+,;=:@/?\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF\U00010000-\U0001FFFD\U00020000-\U0002FFFD\U00030000-\U0003FFFD\U00040000-\U0004FFFD\U00050000-\U0005FFFD\U00060000-\U0006FFFD\U00070000-\U0007FFFD\U00080000-\U0008FFFD\U00090000-\U0009FFFD\U000A0000-\U000AFFFD\U000B0000-\U000BFFFD\U000C0000-\U000CFFFD\U000D0000-\U000DFFFD\U000E1000-\U000EFFFD]+")

def splitOnSpaces(string):
	return spacesRegex.split(string)

def elementHasClass(Element, class_name):
	if Element.get(u"class") and class_name in splitOnSpaces(Element.get(u"class")):
		return True
	else:
		return False

def generateID(Element, force_html4_id=False, **kwargs):
	if Element.get(u"id") is not None:
		return Element.get(u"id")
	elif Element.get(u"title") is not None and Element.get(u"title").strip(spaceCharacters) is not u"":
		source = Element.get(u"title")
	else:
		source = textContent(Element)
	
	source = source.strip(spaceCharacters).lower()
	
	if source == u"":
		source = u"generatedID"
	elif force_html4_id or Element.getroottree().docinfo.public_id in \
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
		source = non_sgml_name.sub(u"-", source).strip(u"-")
		try:
			if not source[0].isalpha():
				source = u"x" + source
		except IndexError:
			source = u"generatedID"
	else:
		source = non_ifragment.sub(u"-", source).strip(u"-")
	
	# Initally set the id to the source
	id = source
	
	i = 0
	while getElementById(Element.getroottree().getroot(), id) is not None:
		id = source + u"-" + unicode(i)
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
			if element.get(u"id"):
				ids[base][element.get(u"id")] = element
		return getElementById(base, id)

def escapeXPathString(string):
	return u"concat('', '%s')" % string.replace(u"'", u"', \"'\", '")

def removeInteractiveContentChildren(element):
	# Set of elements to remove
	to_remove = set()
	
	# Iter over decendants of element
	for child in element.iterdescendants(etree.Element):
		if isInteractiveContent(child):
			# Copy content, to prepare for the node being removed
			copyContentForRemoval(child)
			# Add the element of the list of elements to remove
			to_remove.add(child)
	
	# Remove all elements to be removed
	for element in to_remove:
		element.getparent().remove(element)

def isInteractiveContent(element):
	if element.tag in (u"a", u"bb", u"details") \
	or element.tag in (u"audio", u"video") and element.get(u"controls") is not None \
	or element.tag == u"menu" and element.get(u"type") is not None and element.get(u"type").lower() == u"toolbar":
		return True
	else:
		return False

def copyContentForRemoval(node):
	# Preserve the text, if it is an element
	if isinstance(node.tag, basestring) and node.text is not None:
		if node.getprevious() is not None:
			if node.getprevious().tail is None:
				node.getprevious().tail = node.text
			else:
				node.getprevious().tail += node.text
		else:
			if node.getparent().text is None:
				node.getparent().text = node.text
			else:
				node.getparent().text += node.text
	# Re-parent all the children of the element we're removing
	for child in node.iterchildren():
		node.addprevious(child)
	# Preserve the element tail
	if node.tail is not None:
		if node.getprevious() is not None:
			if node.getprevious().tail is None:
				node.getprevious().tail = node.tail
			else:
				node.getprevious().tail += node.tail
		else:
			if node.getparent().text is None:
				node.getparent().text = node.tail
			else:
				node.getparent().text += node.tail
						
class SpecGenException(Exception):
	"""Generic spec-gen error."""
	pass
