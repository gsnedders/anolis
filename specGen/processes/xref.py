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
from copy import deepcopy

from specGen import utils

term_elements = ("span", "abbr", "code", "var", "i")
w3c_term_elements = ("abbr", "acronym", "b", "bdo", "big", "code", "del", "em", "i", "ins", "kbd", "label", "legend", "q", "samp", "small", "span", "strong", "sub", "sup", "tt", "var")
term_not_in_stack_with = ("a", "dfn", "datagrid")

non_alphanumeric_spaces = re.compile(r"[^a-zA-Z0-9 ]+")

class xref(object):
	"""Add cross-references."""
	
	def __init__(self, ElementTree, **kwargs):
		self.dfns = {}
		self.buildReferences(ElementTree, **kwargs)
		self.addReferences(ElementTree, **kwargs)
	
	def buildReferences(self, ElementTree, allow_duplicate_terms=False, **kwargs):
		for dfn in ElementTree.iter("dfn"):
			term = self.getTerm(dfn, **kwargs)
			
			if len(term) > 0:
				if not allow_duplicate_terms and term in self.dfns:
					raise DuplicateTermException, term
				
				id = utils.generateID(dfn)
				
				dfn.set(u"id", id)
				
				self.dfns[term] = id
	
	def addReferences(self, ElementTree, w3c_compat = False, w3c_compat_xref_elements = False, w3c_compat_xref_a_placement = False, **kwargs):
		to_remove = []
		for element in ElementTree.iter(tag=etree.Element):
			if element.tag in term_elements or (w3c_compat or w3c_compat_xref_elements) and element.tag in w3c_term_elements:
				term = self.getTerm(element, **kwargs)
				
				if term in self.dfns:
					goodParentingAndChildren = True
					
					for parent_element in element.iterancestors(tag=etree.Element):
						if parent_element.tag in term_not_in_stack_with:
							goodParentingAndChildren = False
							break
					else:
						for child_element in element.iterdescendants(tag=etree.Element):
							if child_element.tag in term_not_in_stack_with:
								goodParentingAndChildren = False
								break
					
					if goodParentingAndChildren:
						if element.tag == "span":
							element.tag = "a"
							element.set("href", "#" + self.dfns[term])
						else:
							link = etree.Element("a", {"href": "#" + self.dfns[term]})
							if w3c_compat or w3c_compat_xref_a_placement:
								for node in element.iterchildren():
									link.append(node)
								link.text = element.text
								element.text = None
								element.append(link)
							else:
								link.append(deepcopy(element))
								link.tail = link[0].tail
								link[0].tail = None
								element.addprevious(link)
								to_remove.append(element)
		for element in to_remove:
			element.getparent().remove(element)
	
	def getTerm(self, element, w3c_compat = False, w3c_compat_xref_normalization = False, **kwargs):
		if element.get(u"title") is not None:
			term = element.get(u"title")
		else:
			term = utils.textContent(element)
		
		term = term.strip(utils.spaceCharacters).lower()
		
		term = utils.spacesRegex.sub(" ", term)
		
		if w3c_compat or w3c_compat_xref_normalization:
			term = non_alphanumeric_spaces.sub("", term)
		
		return term

class DuplicateTermException(utils.SpecGenException):
	"""Term already defined."""
	pass
