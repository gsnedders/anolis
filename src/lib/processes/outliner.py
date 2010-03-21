# coding=UTF-8
# Copyright (c) 2008-2010 Geoffrey Sneddon
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

from weakref import WeakKeyDictionary
from lxml import etree

import utils

# Rank of heading elements (these are negative so h1 > h6)
fixedRank = {
    u"{http://www.w3.org/1999/xhtml}h1": -1,
    u"{http://www.w3.org/1999/xhtml}h2": -2,
    u"{http://www.w3.org/1999/xhtml}h3": -3,
    u"{http://www.w3.org/1999/xhtml}h4": -4,
    u"{http://www.w3.org/1999/xhtml}h5": -5,
    u"{http://www.w3.org/1999/xhtml}h6": -6
}


# Cache for outlines
# lxml.etree._Element objects can't have weakrefs, what should I do?
# cache = WeakKeyDictionary()
cache = {}


class section(list):
    """Represents the section of a document."""
    
    def __init__(self, element=None, header=None, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.header = header
        self.element = element

    def __repr__(self):
        return "<section %s>" % (repr(self.header))
    
    @property
    def header_text_element(self):
        if self.header is not None:
            # Get the element that represents the section header's text
            if self.header.tag == u"{http://www.w3.org/1999/xhtml}hgroup":
                for i in xrange(1, 7):
                    header_text = self.header.find(u".//{http://www.w3.org/1999/xhtml}h%i" % i)
                    if header_text is not None:
                        return header_text
            else:
                return self.header
        return None

    def append(self, child):
        list.append(self, child)
        child.parent = self

    def extend(self, children):
        list.extend(self, children)
        for child in children:
            child.parent = self


def _rank(element):
    if element.tag in fixedRank:
        return fixedRank[element.tag]
    # The rank of an hgroup element is the rank of the highest-ranked
    # h1–h6 element descendant of the hgroup element, if there are any such
    # elements, or otherwise the same as for an h1 element (the highest
    # rank).
    elif element.tag == u"{http://www.w3.org/1999/xhtml}hgroup":
        for i in xrange(1, 7):
            if element.find(u".//{http://www.w3.org/1999/xhtml}h%i" % i) is not None:
                return -i
        else:
            return -1
    else:
        raise ValueError, "Only h1–h6 and hgroup elements have a rank, not %s" % element.tag


def outliner(tree):
    # Return a cached outline if possible
    if tree in cache:
        return cache[tree]
    
    # Otherwise compute it
    stack = []
    outlines = {}
    current_outlinee = None
    current_section = None
    for action, element in etree.iterwalk(tree, events=("start", "end")):
        # If the top of the stack is an element, and you are exiting that
        # element
        if action == "end" and stack and stack[-1] == element:
            # Note: The element being exited is a heading content element.
            assert element.tag in utils.heading_content
            # Pop that element from the stack.
            stack.pop()

        # If the top of the stack is a heading content element
        elif stack and stack[-1].tag in utils.heading_content:
            # Do nothing.
            pass

        # When entering a sectioning content element or a sectioning root
        # element
        elif (action == "start" and
              (element.tag in utils.sectioning_content or
               element.tag in utils.sectioning_root)):
            # If current outlinee is not null, push current outlinee onto the
            # stack.
            if current_outlinee is not None:
                stack.append(current_outlinee)
            # Let current outlinee be the element that is being entered.
            current_outlinee = element
            # Let current section be a newly created section for the current
            # outlinee element.
            current_section = section(element=element)
            # Let there be a new outline for the new current outlinee,
            # initialized with just the new current section as the only section
            # in the outline.
            outlines[current_outlinee] = [current_section]

        # When exiting a sectioning content element, if the stack is not empty
        elif (action == "end" and
              element.tag in utils.sectioning_content and
              stack):
            # Pop the top element from the stack, and let the current outlinee
            # be that element.
            current_outlinee = stack.pop()
            # Let current section be the last section in the outline of the
            # current outlinee element.
            current_section = outlines[current_outlinee][-1]
            # Append the outline of the sectioning content element being exited
            # to the current section. (This does not change which section is
            # the last section in the outline.)
            current_section += outlines[element]

        # When exiting a sectioning root element, if the stack is not empty
        elif (action == "end" and
              element.tag in utils.sectioning_root and
              stack):
            # Pop the top element from the stack, and let the current outlinee
            # be that element.
            current_outlinee = stack.pop()
            # Let current section be the last section in the outline of the
            # current outlinee element.
            current_section = outlines[current_outlinee][-1]
            # Loop: If current section has no child sections, stop these steps.
            while current_section:
                # Let current section be the last child section of the current
                # current section.
                assert current_section != current_section[-1]
                current_section = current_section[-1]
                # Go back to the substep labeled Loop.

        # When exiting a sectioning content element or a sectioning root
        # element
        elif (action == "end" and
              (element.tag in utils.sectioning_content or
               element.tag in utils.sectioning_root)):
            # Note: The current outlinee is the element being exited.
            assert current_outlinee == element
            # Let current section be the first section in the outline of the
            # current outlinee element.
            current_section = outlines[current_outlinee][0]
            # Skip to the next step in the overall set of steps. (The walk is
            # over.)
            break

        # If the current outlinee is null.
        elif current_outlinee is None:
            # Do nothing.
            pass

        # When entering a heading content element
        elif action == "start" and element.tag in utils.heading_content:
            # If the current section has no heading, let the element being
            # entered be the heading for the current section.
            if current_section.header is None:
                current_section.header = element

            # Otherwise, if the element being entered has a rank equal to or
            # greater than the heading of the last section of the outline of
            # the current outlinee, then create a new section and append it to
            # the outline of the current outlinee element, so that this new
            # section is the new last section of that outline. Let current
            # section be that new section. Let the element being entered be the
            # new heading for the current section.
            elif (_rank(element) >=
                  _rank(outlines[current_outlinee][-1].header)):
                current_section = section(element=element,
                                               header=element)
                outlines[current_outlinee].append(current_section)

            # Otherwise, run these substeps:
            else:
                # Let candidate section be current section.
                candidate_section = current_section
                while True:
                    # If the element being entered has a rank lower than the
                    # rank of the heading of the candidate section, then create
                    # a new section, and append it to candidate section. (This
                    # does not change which section is the last section in the
                    # outline.) Let current section be this new section. Let
                    # the element being entered be the new heading for the
                    # current section. Abort these substeps.
                    if _rank(element) < _rank(candidate_section.header):
                        current_section = section(element=element,
                                                       header=element)
                        candidate_section.append(current_section)
                        break
                    # Let new candidate section be the section that contains
                    # candidate section in the outline of current outlinee.
                    # Let candidate section be new candidate section.
                    candidate_section = candidate_section.parent
                    # Return to step 2.
            # Push the element being entered onto the stack. (This causes
            # the algorithm to skip any descendants of the element.)
            stack.append(element)

    # If the current outlinee is null, then there was no sectioning content
    # element or sectioning root element in the DOM. There is no outline.
    try:
        cache[tree] = outlines[current_outlinee]
        return outlines[current_outlinee]
    except KeyError:
        return None
