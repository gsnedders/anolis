# coding=UTF-8
# Copyright (c) 2008-2009 Geoffrey Sneddon
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
import html5lib
import urllib2

from .. import utils

instance_elements = frozenset([u"{http://www.w3.org/1999/xhtml}span",
                               u"{http://www.w3.org/1999/xhtml}abbr",
                               u"{http://www.w3.org/1999/xhtml}code",
                               u"{http://www.w3.org/1999/xhtml}var",
                               u"{http://www.w3.org/1999/xhtml}i"])

w3c_instance_elements = frozenset([u"{http://www.w3.org/1999/xhtml}abbr",
                                   u"{http://www.w3.org/1999/xhtml}acronym",
                                   u"{http://www.w3.org/1999/xhtml}b",
                                   u"{http://www.w3.org/1999/xhtml}bdo",
                                   u"{http://www.w3.org/1999/xhtml}big",
                                   u"{http://www.w3.org/1999/xhtml}code",
                                   u"{http://www.w3.org/1999/xhtml}del",
                                   u"{http://www.w3.org/1999/xhtml}em",
                                   u"{http://www.w3.org/1999/xhtml}i",
                                   u"{http://www.w3.org/1999/xhtml}ins",
                                   u"{http://www.w3.org/1999/xhtml}kbd",
                                   u"{http://www.w3.org/1999/xhtml}label",
                                   u"{http://www.w3.org/1999/xhtml}legend",
                                   u"{http://www.w3.org/1999/xhtml}q",
                                   u"{http://www.w3.org/1999/xhtml}samp",
                                   u"{http://www.w3.org/1999/xhtml}small",
                                   u"{http://www.w3.org/1999/xhtml}span",
                                   u"{http://www.w3.org/1999/xhtml}strong",
                                   u"{http://www.w3.org/1999/xhtml}sub",
                                   u"{http://www.w3.org/1999/xhtml}sup",
                                   u"{http://www.w3.org/1999/xhtml}tt",
                                   u"{http://www.w3.org/1999/xhtml}var"])

non_alphanumeric_spaces = re.compile(r"[^a-zA-Z0-9 \-]+")


class xref(object):
    """Add cross-references."""
    
    passes = 2

    # XXX: Should this support random file paths as well as just absolute URLs?
    def __init__(self, externalURLs = [], **kwargs):
        self.dfns = {}
        for url in externalURLs:
            if urlparse.urlsplit(url).scheme is "":
                raise NonAbsoluteURLException(u"%s is not an absolute URL. All external URLs to load for xref must be absolute." % url)
            fp = urllib2.urlopen(url)
            mimetype = fp.info().get_content_type()
            if mimetype == "text/html":
                tree = html5lib.parse(fp, "lxml")
            elif mimetype.endswith("+xml") or mimetype.endswith("-xml"):
                tree = etree.parse(fp)
            fp.close()
            self.buildReferences(tree, url, **kwargs)

    def buildReferences(self, tree, url, allow_duplicate_dfns = False,
                        **kwargs):
        for dfn in tree.iter(u"{http://www.w3.org/1999/xhtml}dfn"):
            term = self.getTerm(dfn, **kwargs)

            if len(term) > 0:
                if not allow_duplicate_dfns and term in self.dfns:
                    raise DuplicateDfnException(u'The term "%s" is defined more than once' % term)

                link_to = dfn

                for parent_element in dfn.iterancestors(tag=etree.Element):
                    if parent_element.tag in utils.heading_content:
                        link_to = parent_element
                        break

                id = utils.generateID(link_to, **kwargs)

                link_to.set(u"id", id)

                self.dfns[term] = urllib.urljoin(url, u"#%s" % id)

    def addReferences(self, tree, url, w3c_compat=False,
                      w3c_compat_xref_elements=False,
                      w3c_compat_xref_a_placement=False, **kwargs):
        stack = []
        currentIgnoreElements = 0
        for element in tree.iter(tag=etree.Element):
            try:
                while stack[-1] is not element.getparent():
                    parent = stack.pop()
                    if (parent.tag is "{http://www.w3.org/1999/xhtml}dfn" or
                        utils.isInteractiveContent(parent)):
                        currentIgnoreElements -= 1
            except IndexError:
                pass
            stack.append(element)
            if (element.tag is "{http://www.w3.org/1999/xhtml}dfn" or
                utils.isInteractiveContent(element)):
                currentIgnoreElements += 1
            
            if (not currentIgnoreElements and
                element.tag in instance_elements or
                (w3c_compat or w3c_compat_xref_elements) and
                element.tag in w3c_instance_elements):
                term = self.getTerm(element, w3c_compat=w3c_compat, **kwargs)

                if term in self.dfns:
                    # XXX: Do we want to create a set of dirty elements?
                    goodChildren = True
                    
                    for child_element in element.iterdescendants(tag=etree.Element):
                        if (child_element.tag is "{http://www.w3.org/1999/xhtml}dfn" or
                            utils.isInteractiveContent(child_element)):
                            goodChildren = False
                            break

                    if goodChildren:
                        href = urlparse.urljoin(url, self.dfns[term])
                        if element.tag is u"{http://www.w3.org/1999/xhtml}span":
                            element.tag = u"{http://www.w3.org/1999/xhtml}a"
                            element.set(u"href", href)
                        else:
                            link = etree.Element(u"{http://www.w3.org/1999/xhtml}a",
                                                 {u"href": href})
                            if w3c_compat or w3c_compat_xref_a_placement:
                                for node in element:
                                    link.append(node)
                                link.text = element.text
                                element.text = None
                                element.append(link)
                            else:
                                element.addprevious(link)
                                link.append(element)
                                link.tail = link[0].tail
                                link[0].tail = None
    
    # Add these merely as an alias for readability's sake
    pass1 = buildReferences
    pass2 = addReferences

    def getTerm(self, element, w3c_compat=False,
                w3c_compat_xref_normalization=False, **kwargs):
        if element.get(u"data-xref") is not None:
            term = element.get(u"data-xref")
        elif element.get(u"title") is not None:
            term = element.get(u"title")
        else:
            term = utils.textContent(element)

        term = term.strip(utils.spaceCharacters).lower()

        term = utils.spacesRegex.sub(u" ", term)

        if w3c_compat or w3c_compat_xref_normalization:
            term = non_alphanumeric_spaces.sub(u"", term)

        return term


class DuplicateDfnException(utils.AnolisException):
    """Term already defined."""
    pass
