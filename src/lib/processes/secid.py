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

from lxml import etree
from copy import deepcopy

import utils
import outliner

def Process(tree, url, **kwargs):
    # Set of ids in document
    ids = set()
    for element in tree.iter(tag=etree.Element):
        if element.get(u"id") is not None:
            ids.add(element.get(u"id"))
    
    # Build the outline of the document
    outline = outliner.outliner(tree)
    
    # Get a list of all the top level sections, and their depth (0)
    sections = [(section, 0) for section in reversed(outline)]

    # Loop over all sections in a DFS
    while sections:
        # Get the section and depth at the end of list
        section, depth = sections.pop()

        # Get the element from which the header text comes from
        header_text = section.header_text_element
        
        # Add id if there isn't already one
        if section.element.get(u"id") is None:
            if header_text is not None:
                if header_text.get(u"id") is None:
                    element = removeSecno(deepcopy(header_text))
                    base = id = utils.generateID(element, **kwargs)
                else:
                    base = id = header_text.get(u"id")
                    del header_text.attribs[u"id"]
                    ids.remove(id)
            else:
                base = id = "unknown-section"
            i = 0
            while id in ids:
                id = u"%s-%s" % (base, i)
                i += 1
            section.element.set(u"id", id)
            ids.add(id)
        
        # Add subsections in reverse order (so the next one is executed
        # next) with a higher depth value
        sections.extend([(child_section, depth + 1)
                         for child_section in reversed(section)])

def removeSecno(element):
    # Remove any existing section number
    for descendant in list(element.iter(u"{http://www.w3.org/1999/xhtml}span")):
        if utils.elementHasClass(descendant, u"secno"):
            # Copy content, to prepare for the node being
            # removed
            utils.copyContentForRemoval(descendant, text=False,
                                        children=False)
            # Remove the element (we can do this as we're not
            # iterating over the elements, but over a list)
            descendant.getparent().remove(descendant)
    return element
