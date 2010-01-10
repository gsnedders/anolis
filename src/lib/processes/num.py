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


class Process(object):
    
    passes = 1
    
    def __init__(self, **kwargs):
        self.num = []

    def pass1(self, tree, perFileNum=True, **kwargs):
        # Reset if we have per-file numbering
        if perFileNum:
            self.num = []
        
        # Build the outline of the document
        outline_creator = outliner.Outliner(tree, **kwargs)
        outline = outline_creator.build(**kwargs)

        # Get a list of all the top level sections, and their depth (0)
        sections = [(section, 0) for section in reversed(outline)]

        # Loop over all sections in a DFS
        while sections:
            # Get the section and depth at the end of list
            section, depth = sections.pop()

            # If we have a header, regardless of how deep we are
            if section.header is not None:
                # Get the element that represents the section header's text
                if section.header.tag == u"{http://www.w3.org/1999/xhtml}hgroup":
                    for i in xrange(1, 7):
                        header_text = section.header.find(u".//{http://www.w3.org/1999/xhtml}h%i" % i)
                        if header_text is not None:
                            break
                    else:
                        header_text = None
                else:
                    header_text = section.header
            else:
                header_text = None

            # If we have a section heading text element, regardless of depth
            if header_text is not None:
                # Remove any existing number
                for element in list(header_text.iter(u"{http://www.w3.org/1999/xhtml}span")):
                    if utils.elementHasClass(element, u"secno"):
                        # Copy content, to prepare for the node being
                        # removed
                        utils.copyContentForRemoval(element, text=False,
                                                    children=False)
                        # Remove the element (we can do this as we're not
                        # iterating over the elements, but over a list)
                        element.getparent().remove(element)

            # No children, no sibling, move back to parent's sibling
            if depth + 1 < len(self.num):
                del self.num[depth + 1:]
            # Children
            elif depth == len(self.num):
                self.num.append(0)

            # Increment the current section's number
            if header_text is not None and \
               not utils.elementHasClass(header_text, u"no-num") or \
               header_text is None and section:
                self.num[-1] += 1

            # If we have a header
            if header_text is not None:
                # Add number, if @class doesn't contain no-num
                if not utils.elementHasClass(header_text, u"no-num"):
                    header_text[0:0] = [etree.Element(u"{http://www.w3.org/1999/xhtml}span",
                                                      {u"class": u"secno"})]
                    header_text[0].tail = header_text.text
                    header_text.text = None
                    header_text[0].text = u".".join(map(unicode, self.num))
                    header_text[0].text += u" "
            
            # Add subsections in reverse order (so the next one is executed
            # next) with a higher depth value
            sections.extend([(child_section, depth + 1)
                             for child_section in reversed(section)])
