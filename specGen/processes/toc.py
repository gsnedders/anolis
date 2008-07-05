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
from specGen.processes import outliner

class toc(object):
	"""Build and add TOC."""
	
	toc = None
	
	def __init__(self, ElementTree, **kwargs):
		self.toc = etree.Element("ol", {"class": "toc"})
		self.buildToc(ElementTree, **kwargs)
		self.addToc(ElementTree, **kwargs)
	
	def buildToc(self, ElementTree, **kwargs):
		# Build the outline of the document
		outline_creator = outliner.Outliner()
		outline = outline_creator.build(ElementTree)
		
		# Get a list of all the top level sections, and their depth (0)
		sections = [(section, 0) for section in outline]
		
		# Numbering
		num = []
		
		# Loop over all sections in a DFS
		while sections:
			# Get the section and depth at the end of list
			section, depth = sections.pop()
			
			# Numbering:
			# No children, no sibling, move back to parent's sibling
			if depth + 1 < len(num):
				del num[depth + 1:]
			# Children
			elif depth == len(num):
				num.append(0)
			
			# If we have a header
			if section.header is not None:
				# Add ID to header
				id = utils.generateID(section.header)
				section.header.set("id", id)
				# Add number, if @class doesn't contain no-num
				if not utils.elementHasClass(section.header, "no-num"):
					num[-1] += 1
					section.header[0:0] = [etree.Element("span", {"class": "secno"})]
					section.header[0].tail = section.header.text
					section.header.text = None
					section.header[0].text = u".".join(map(str, num)) + u". "
				# Add to TOC, if @class doesn't contain no-toc
				if not utils.elementHasClass(section.header, "no-toc"):
					# Find the appropriate section of the TOC 
					i = 0
					toc_section = self.toc
					while i < depth:
						try:
							# If the final li has no children, or the last children isn't an ol element
							if len(toc_section[-1]) == 0 or toc_section[-1][-1].tag != "ol":
								toc_section[-1].append(etree.Element("ol"))
						except IndexError:
							# If the current ol has no li in it
							toc_section.append(etree.Element("li"))
							toc_section[0].append(etree.Element("ol"))
						# TOC Section is now the final child (ol) of the final item (li) in the previous section
						assert toc_section[-1].tag == "li"
						assert toc_section[-1][-1].tag == "ol"
						toc_section = toc_section[-1][-1]
						i += 1
					# Add the current item to the TOC
					item = etree.Element("li")
					toc_section.append(item)
					link = deepcopy(section.header)
					item.append(link)
					# Make it link to the header
					link.tag = "a"
					link.set("href", "#" + id)
					# TODO: Need to remove @id and @class, not set it to an empty string
					link.set("id", "")
					link.set("class", "")
					# We don't want the old tail (or any tail, for that matter)
					link.tail = None
			# Add subsections in reverse order (so the next one is executed next) with a higher depth value
			sections.extend((child_section, depth + 1) for child_section in reversed(section))
	
	def addToc(self, ElementTree, **kwargs):
		in_toc = False
		for node in ElementTree.iter():
			if in_toc:
				if isinstance(node, etree._Comment) and node.text.strip(utils.spaceCharacters) == "end-toc":
					in_toc = False
				else:
					node.getparent().remove(node)
			elif isinstance(node, etree._Comment):
				if node.text.strip(utils.spaceCharacters) == "begin-toc":
					in_toc = True
					node.addnext(deepcopy(self.toc))
				elif node.text.strip(utils.spaceCharacters) == "toc":
					node.addprevious(etree.Comment("begin-toc"))
					node.addprevious(deepcopy(self.toc))
					node.addprevious(etree.Comment("end-toc"))
					node.getparent().remove(node)