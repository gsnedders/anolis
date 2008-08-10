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

heading_content = frozenset([u"h1", u"h2", u"h3", u"h4", u"h5", u"h6", u"header"])
sectioning_content = frozenset([u"body", u"section", u"nav", u"article", u"aside"])
sectioning_root = frozenset([u"blockquote", u"figure", u"td", u"datagrid"])

non_sgml_name = re.compile("[^A-Za-z0-9\-_:.]+")

def splitOnSpaces(string):
	return spacesRegex.split(string)

def elementHasClass(Element, class_name):
	if Element.get(u"class") and class_name in splitOnSpaces(Element.get(u"class")):
		return True
	else:
		return False

def generateID(Element, force_html4_id=False, **kwargs):
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
		if not source[0].isalpha():
			source = u"x" + source
	else:
		source = spacesRegex.sub(u"-", source).strip(u"-")
	
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
	for node in node.iterchildren():
		node.addprevious(node)
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
