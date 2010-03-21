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
from collections import deque

import utils
import outliner, sub

# These are just the non-interactive elements to be removed
remove_elements_from_toc = frozenset([u"dfn", ])
# These are, however, all the attributes to be removed
remove_attributes_from_toc = frozenset([u"id", ])


class Process(object):
    """Build and add TOC."""
    
    passes = 2
    
    def __init__(self, **kwargs):
        self.toc = {}

    def buildToc(self, tree, url, w3c_compat=False,
                 w3c_compat_class_toc=False, **kwargs):
        # Set of ids in document
        ids = set()
        for element in tree.iter(tag=etree.Element):
            if element.get(u"id") is not None:
                ids.add(element.get(u"id"))
        
        # Build the outline of the document
        outline = outliner.outliner(tree)
        
        # Create empty TOC
        self.toc[url] = etree.Element(u"ol", {u"class": u"toc"})
        
        # Effective root depth
        rootDepth = 0

        # Get a list of all the top level sections, and their depth (0)
        sections = deque([(section, 0) for section in outline])
        
        # Find effective root depth with a BFS
        while sections:
            # Get the section and depth at the start of list
            section, depth = sections.popleft()
            
            # Get the element from which the header text comes from
            header_text = section.header_text_element
            
            if (header_text is None or 
                not utils.elementHasClass(header_text, u"no-toc")):
                rootDepth = depth
                break
            
            # Add subsections in reverse order (so the next one is executed
            # next) with a higher depth value
            sections.extend([(child_section, depth + 1)
                             for child_section in section])

        # Get a list of all the top level sections, and their depth (0)
        sections = [(section, 0) for section in reversed(outline)]

        # Loop over all sections in a DFS
        while sections:
            # Get the section and depth at the end of list
            section, depth = sections.pop()

            header_text = section.header_text_element

            # If we're deep enough to actually want to number this section
            if depth >= rootDepth:
                if section.element.get(u"id") is None:
                    if header_text is not None:
                        if header_text.get(u"id") is None:
                            base = id = utils.generateID(header_text, **kwargs)
                        else:
                            base = id = header_text.get(u"id")
                            del header_text.attribs[u"id"]
                    else:
                        base = id = "unknown-section"
                    i = 0
                    while id in ids:
                        id = u"%s-%s" % (base, i)
                        i += 1
                    section.element.set(u"id", id)
                    ids.add(id)
                else:
                    id = section.element.get(u"id")

                # Get the current TOC section for this depth, and add another
                # item to it
                if (header_text is None or 
                    not utils.elementHasClass(header_text, u"no-toc")):
                    # Find the appropriate section of the TOC
                    toc_section = self.toc[url]
                    for i in xrange(0, depth - rootDepth):
                        try:
                            # If the final li has no children, or the last
                            # child isn't an ol element
                            if (len(toc_section[-1]) == 0 or
                                toc_section[-1][-1].tag != u"ol"):
                                toc_section[-1].append(etree.Element(u"ol"))
                                if w3c_compat or w3c_compat_class_toc:
                                    toc_section[-1][-1].set(u"class", u"toc")
                        except IndexError:
                            # If the current ol has no li in it
                            toc_section.append(etree.Element(u"li"))
                            toc_section[0].append(etree.Element(u"ol"))
                            if w3c_compat or w3c_compat_class_toc:
                                toc_section[0][0].set(u"class", u"toc")
                        # TOC Section is now the final child (ol) of the final
                        # item (li) in the previous section
                        assert toc_section[-1].tag == u"li"
                        assert toc_section[-1][-1].tag == u"ol"
                        toc_section = toc_section[-1][-1]
                    # Add the current item to the TOC
                    item = etree.Element(u"li")
                    toc_section.append(item)
                    
                    # Add to TOC, if @class doesn't contain no-toc
                    if header_text is not None:
                        link = deepcopy(header_text)
                        item.append(link)
                        # Make it link to the header
                        link.tag = u"a"
                        link.set(u"href", u"#" + id)
                        # Remove interactive content child elements
                        utils.removeInteractiveContentChildren(link)
                        # Remove other child elements
                        for element_name in remove_elements_from_toc:
                            # Iterate over all the desendants of the new link
                            # with that element name
                            for element in link.findall(u".//" + element_name):
                                # Copy content, to prepare for the node being
                                # removed
                                utils.copyContentForRemoval(element)
                                # Remove the element (we can do this as we're
                                # not iterating over the elements, but over a
                                # list)
                                element.getparent().remove(element)
                        # Remove unwanted attributes
                        for element in link.iter(tag=etree.Element):
                            for attribute_name in remove_attributes_from_toc:
                                if element.get(attribute_name) is not None:
                                    del element.attrib[attribute_name]
                        # We don't want the old tail
                        link.tail = None
                        # Check we haven't changed the content in all of that
                        assert utils.textContent(header_text) == \
                               utils.textContent(link)
                    else:
                        item.append(etree.Element(u"a"))
                        item[-1].set(u"href", u"#" + id)
                        item[-1].text = "Unknown Section"
            
            # Add subsections in reverse order (so the next one is executed
            # next) with a higher depth value
            sections.extend([(child_section, depth + 1)
                             for child_section in reversed(section)])

    def addToc(self, tree, url, **kwargs):
        try:
            self.toc[url] = etree.fromstring(etree.tostring(self.toc[url], pretty_print=True))
        except etree.XMLSyntaxError:
            pass
        replace = {"toc": self.toc[url]}
        sub.doCommentSubstitutions(replace, tree)
    
    pass1 = buildToc
    pass2 = addToc
