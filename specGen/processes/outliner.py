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

heading_content = frozenset(["h1", "h2", "h3", "h4", "h5", "h6", "header"])
sectioning_content = frozenset(["body", "section", "nav", "article", "aside"])
sectioning_root = frozenset(["blockquote", "figure", "td", "datagrid"])

# Rank of heading elements (these are negative so h1 > h6)
rank = {"h1": -1, "h2": -2, "h3": -3, "h4": -4, "h5": -5, "h6": -6, "header": -1}

class section(list):
	"""Represents the section of a document."""
	
	header = None
	
	def __repr__(self):
		return "<section %s>" % (repr(self.header))

	def append(self, child):
		list.append(self, child)
		child.parent = self
	
	def extend(self, children):
		list.extend(self, children)
		for child in children:
			child.parent = self

class Outliner:
	"""Build the outline of an HTML document."""
	
	def build(self, ElementTree, **kwargs):
		stack = []
		outlines = {}
		current_outlinee = None
		current_section = None
		context = etree.iterwalk(ElementTree, events=("start", "end"))
		for action, element in context:
			# If the top of the stack is an element, and you are exiting that element
			if action == "end" and stack and stack[-1] == element:
				# Note: The element being exited is a heading content element.
				assert element.tag in heading_content
				# Pop that element from the stack.
				stack.pop()
			
			# If the top of the stack is a heading content element
			elif stack and stack[-1].tag in heading_content:
				# Do nothing.
				pass
			
			# When entering a sectioning content element or a sectioning root element
			elif action == "start" and (element.tag in sectioning_content or element.tag in sectioning_root):
				# If current outlinee is not null, push current outlinee onto the stack.
				if current_outlinee is not None:
					stack.append(current_outlinee)
				# Let current outlinee be the element that is being entered.
				current_outlinee = element
				# Let current section be a newly created section for the current outlinee element.
				current_section = section()
				# Let there be a new outline for the new current outlinee, initialized with just the new current section as the only section in the outline.
				outlines[current_outlinee] = [current_section]
				
			# When exiting a sectioning content element, if the stack is not empty
			elif action == "end" and element.tag in sectioning_content and stack:
				# Pop the top element from the stack, and let the current outlinee be that element.
				current_outlinee = stack.pop()
				# Let current section be the last section in the outline of the current outlinee element.
				current_section = outlines[current_outlinee][-1]
				# Append the outline of the sectioning content element being exited to the current section. (This does not change which section is the last section in the outline.)
				current_section += outlines[element]
				
			# When exiting a sectioning root element, if the stack is not empty
			elif action == "end" and element.tag in sectioning_root and stack:
				# Pop the top element from the stack, and let the current outlinee be that element.
				current_outlinee = stack.pop()
				# Let current section be the last section in the outline of the current outlinee element.
				current_section = outlines[current_outlinee][-1]
				# Loop: If current section has no child sections, stop these steps.
				while current_section:
					# Let current section be the last child section of the current current section.
					assert current_section != current_section[-1]
					current_section = current_section[-1]
					# Go back to the substep labeled Loop.
					
			# When exiting a sectioning content element or a sectioning root element
			elif action == "end" and (element.tag in sectioning_content or element.tag in sectioning_root):
				# Note: The current outlinee is the element being exited.
				assert current_outlinee == element
				# Let current section be the first section in the outline of the current outlinee element.
				current_section = outlines[current_outlinee][0]
				# Skip to the next step in the overall set of steps. (The walk is over.)
				break
				
			# If the current outlinee is null.
			elif current_outlinee is None:
				# Do nothing.
				pass
			
			# When entering a heading content element
			elif action == "start" and element.tag in heading_content:
				# If the current section has no heading, let the element being entered be the heading for the current section.
				if current_section.header is None:
					current_section.header = element
				
				# Otherwise, if the element being entered has a rank equal to or greater than the heading of the last section of the outline of the current outlinee, then create a new section and append it to the outline of the current outlinee element, so that this new section is the new last section of that outline. Let current section be that new section. Let the element being entered be the new heading for the current section.
				elif rank[element.tag] >= rank[outlines[current_outlinee][-1].header.tag]:
					current_section = section()
					outlines[current_outlinee].append(current_section)
					current_section.header = element
				
				# Otherwise, run these substeps:
				else:
					# Let candidate section be current section.
					candidate_section = current_section
					while True:
						# If the element being entered has a rank lower than the rank of the heading of the candidate section, then create a new section, and append it to candidate section. (This does not change which section is the last section in the outline.) Let current section be this new section. Let the element being entered be the new heading for the current section. Abort these substeps.
						if rank[element.tag] < rank[candidate_section.header.tag]:
							current_section = section()
							candidate_section.append(current_section)
							current_section.header = element
							break
						# Let new candidate section be the section that contains candidate section in the outline of current outlinee.
						# Let candidate section be new candidate section.
						candidate_section = candidate_section.parent
						# Return to step 2.
				# Push the element being entered onto the stack. (This causes the algorithm to skip any descendants of the element.)
				stack.append(element)
		
		# If the current outlinee is null, then there was no sectioning content element or sectioning root element in the DOM. There is no outline.
		try:
			return outlines[current_outlinee]
		except KeyError:
			return None