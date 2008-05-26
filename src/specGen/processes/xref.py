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

from lxml import etree
from copy import deepcopy

from specGen import utils

class xref(object):
	"""Add cross-references."""
	
	dfns = {}
	refs = ("span", "abbr", "code", "var", "i")
	not_within = ("a", "dfn", "datagrid")
	
	def __init__(self, ElementTree, **kwargs):
		self.buildReferences(ElementTree, **kwargs)
		self.addReferences(ElementTree, **kwargs)
	
	def buildReferences(self, ElementTree):
		for dfn in ElementTree.iter("dfn"):
			if dfn.get(u"title"):
				term = dfn.get(u"title")
			else:
				term = utils.textContent(dfn)
			
			term = term.strip(utils.spaceCharacters).lower()
			
			if len(term) > 0:
				id = utils.generateID(dfn)
				
				dfn.set(u"id", id)
				
				self.dfns[term] = id
	
	def addReferences(self, ElementTree):
		for element in ElementTree.iter(tag=etree.Element):
			if element.tag in self.refs:
				goodParentingAndChildren = True
				
				current = element
				while (current.getparent()):
					current = current.getparent()
					if current.tag in self.not_within:
						goodParentingAndChildren = False
						break
				
				if goodParentingAndChildren:
					for tag in self.not_within:
						if not element.find(".//" + tag):
							goodParentingAndChildren = False
							break
				
				if goodParentingAndChildren:
					if element.get(u"title"):
						term = element.get(u"title")
					else:
						term = utils.textContent(element)
					
					term = term.strip(utils.spaceCharacters).lower()
					
					if term in self.dfns:
						if element.tag == "span":
							element.tag = "a"
							element.set("href", "#" + self.dfns[term])
						else:
							link = etree.Element("a", {"href": "#" + self.dfns[term]})
							link.append(deepcopy(element))
							link.tail = link[0].tail
							link[0].tail = None
							element.addprevious(link)
							element.getparent().remove(element)