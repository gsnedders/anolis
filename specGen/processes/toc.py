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
from collections import deque

from specGen import utils

heading_content = ("h1", "h2", "h3", "h4", "h5", "h6", "header")
sectioning_content = ("body", "section", "nav", "article", "aside")
sectioning_root = ("blockquote", "figure", "td", "datagrid")

rank = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6, "header": 1}

class section(object):
	"""Represents the section of a document."""
	
	header = None
	subsections = []
	associated_nodes = []

class toc(object):
	"""Build and add a TOC to the document."""
	
	# These need to be created in the constructor
	toc = None
	stack = None
	
	# These don't
	level = 0
	num = []
	current_outlinee = None
	current_section = None
	outlines = {}
	sections = {}
	
	def __init__(self, ElementTree, **kwargs):
		self.toc = etree.Element("ol", {"class": "toc"})
		self.stack = deque()
		context = etree.iterwalk(ElementTree, events=("start", "end"))
		for action, element in context:
			if action == "start":
				self.start(element, **kwargs)
			else:
				self.end(element, **kwargs)
	
	def start(self, element, **kwargs):
		# If the top of the stack is a heading content element
		if len(self.stack) and self.stack[-1].tag in heading_content:
			# Do nothing.
			return
		
		# When entering a sectioning content element or a sectioning root element
		elif element.tag in sectioning_content or element.tag in sectioning_root:
			# If current outlinee is not null, push current outlinee onto the stack.
			if self.current_outlinee is not None:
				self.stack.append(self.current_outlinee)
			# Let current outlinee be the element that is being entered.
			self.current_outlinee = element
			# Let current section be a newly created section for the current outlinee element.
			self.sections[element] = self.current_section = section()
			# Let there be a new outline for the new current outlinee, initialized with just the new current section as the only section in the outline.
			self.outlines[element] = [self.current_section]
			
		# If the current outlinee is null.
		elif self.current_outlinee is None:
			# Do nothing.
			return
		
		# When entering a heading content element
		elif element.tag in heading_content:
			# If the current section has no heading, let the element being entered be the heading for the current section.
			if self.current_section.header is None:
				self.current_section.header = element
			
			# Otherwise, if the element being entered has a rank equal to or greater than the heading of the current section, then create a new section and append it to the outline of the current outlinee element, so that this new section is the new last section of that outline. Let current section be that new section. Let the element being entered be the new heading for the current section.
			elif rank[element.tag] <= rank[self.current_section.header.tag]:
				self.current_section = section()
				self.outlines[self.current_outlinee].append(self.current_section)
				self.current_section.header = element
			
			# Otherwise, run these substeps:
			else:
				# Let candidate section be current section.
				candidate_section = self.current_section
				while True:
					# If the element being entered has a rank lower than the rank of the heading of the candidate section, then create a new section, and append it to candidate section. (This does not change which section is the last section in the outline.) Let current section be this new section. Let the element being entered be the new heading for the current section. Abort these substeps.
					if rank[element.tag] > rank[candidate_section.header.tag]:
						self.current_section = section()
						candidate_section.subsections.append(self.current_section)
						self.current_section.header = element
						break
					# Let new candidate section be the section that contains candidate section in the outline of current outlinee.
					for each_section in self.outlines[self.current_outlinee]:
						if candidate_section in each_section.subsections:
							new_candidate_section = each_section
							break
					# Let candidate section be new candidate section.
					candidate_section = new_candidate_section
					# Return to step 2.
			# Push the element being entered onto the stack. (This causes the algorithm to skip any descendants of the element.)
			self.stack.append(element)
	
	def end(self, element, **kwargs):
		# If the top of the stack is an element, and you are exiting that element
		if len(self.stack):
			self.stack.pop()
			
		# If the top of the stack is a heading content element
		elif len(self.stack) and self.stack[-1].tag in heading_content:
			# Do nothing.
			return
			
		# When exiting a sectioning content element, if the stack is not empty
		elif element.tag in sectioning_content and len(self.stack) > 0:
			# Pop the top element from the stack, and let the current outlinee be that element.
			self.current_outlinee = self.stack.pop()
			# Let current section be the last section in the outline of the current outlinee element.
			self.current_section = self.outlines[self.current_outlinee][-1]
			# Append the outline of the sectioning content element being exited to the current section. (This does not change which section is the last section in the outline.)
			self.current_section.subsections += self.outlines[element]
			
		# When exiting a sectioning root element, if the stack is not empty
		elif element.tag in sectioning_root and len(self.stack) > 0:
			# Pop the top element from the stack, and let the current outlinee be that element.
			self.current_outlinee = self.stack.pop()
			# Let current section be the last section in the outline of the current outlinee element.
			self.current_section = self.outlines[self.current_outlinee][-1]
			# Loop: If current section has no child sections, stop these steps.
			while len(self.current_section.subsections) > 0:
				# Let current section be the last child section of the current current section.
				self.current_section = self.current_section.subsections[-1]
				# Go back to the substep labeled Loop.
				
		# When exiting a sectioning content element or a sectioning root element
		elif element.tag in sectioning_content or element.tag in sectioning_root:
			# Let current section be the first section in the outline of the current outlinee element.
			self.current_section = self.outlines[self.current_outlinee][0]
			# Skip to the next step in the overall set of steps. (The walk is over.)
			# TODO: Implement this somehow.
		
		# In addition, whenever you exit a node, after doing the steps above, if current section is not null, associate the node with the section current section.
		if self.current_section is not None:
			self.current_section.associated_nodes.append(element)