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

from __future__ import unicode_literals

import re
from lxml import etree

try:
    import json
except ImportError:
    import simplejson as json

from anolislib import utils

instance_elements = frozenset(["span", "abbr", "code", "var", "i"])
w3c_instance_elements = frozenset(["abbr", "acronym", "b", "bdo", "big",
                                   "code", "del", "em", "i", "ins",
                                   "kbd", "label", "legend", "q", "samp",
                                   "small", "span", "strong", "sub",
                                   "sup", "tt", "var"])

# Instances cannot be in the stack with any of these element, or with
# interactive elements
instance_not_in_stack_with = frozenset(["dfn", ])

non_alphanumeric_spaces = re.compile(r"[^a-zA-Z0-9 \-\_\/\|]+")


class xref(object):
    """Add cross-references."""

    def __init__(self, ElementTree, dump_xrefs='', dump_backrefs=False, **kwargs):
        self.dfns = {}
        self.instances = {}
        self.buildReferences(ElementTree, dump_backrefs=dump_backrefs, **kwargs)
        if dump_xrefs:
            self.dump(self.getDfns(dump_xrefs), dump_xrefs, **kwargs)
        self.addReferences(ElementTree, dump_backrefs=dump_backrefs, **kwargs)
        if dump_backrefs:
            self.dump(self.instances, "backrefs.json", **kwargs)

    def buildReferences(self, ElementTree, allow_duplicate_dfns=False,
                        **kwargs):
        for dfn in ElementTree.iter("dfn"):
            terms = self.getTerm(dfn, **kwargs).split("|")
            for term in set(t for t in terms if t):
                if not allow_duplicate_dfns and term in self.dfns:
                    raise DuplicateDfnException('The term "%s" is defined more than once' % term)

                link_to = dfn

                for parent_element in dfn.iterancestors(tag=etree.Element):
                    if parent_element.tag in utils.heading_content:
                        link_to = parent_element
                        break

                id = utils.generateID(link_to, **kwargs)

                link_to.set("id", id)

                self.dfns[term] = id
                self.instances[term] = []

    def getDfns(self, dump_xrefs, **kwargs):
        try:
            fp = open(dump_xrefs, "r")
            data = json.load(fp)
            fp.close()
            data["definitions"] = self.dfns
            return data
        except IOError:
            raise XrefsFileNotCreatedYetException("""No such file or directory: '%s'. Please create it first.
It should contain a an object with a 'url' property (whose value ends with a '#').""" % dump_xrefs)

    def dump(self, obj, f, **kwargs):
        d = json.dumps(obj, sort_keys=True, allow_nan=False, indent=2, separators=(',', ': '))
        fp = open(f, "w")
        fp.write(d + "\n")
        fp.close()

    def addReferences(self, ElementTree, w3c_compat=False,
                      w3c_compat_xref_elements=False,
                      w3c_compat_xref_a_placement=False,
                      use_strict=False,
                      dump_backrefs=False,
                      **kwargs):
        for element in ElementTree.iter(tag=etree.Element):
            if element.tag in instance_elements or \
               (w3c_compat or w3c_compat_xref_elements) and \
               element.tag in w3c_instance_elements:
                term = self.getTerm(element, w3c_compat=w3c_compat, **kwargs)

                if term in self.dfns:
                    goodParentingAndChildren = True

                    for parent_element in \
                        element.iterancestors(tag=etree.Element):
                        if (parent_element.tag in instance_not_in_stack_with or
                            utils.isInteractiveContent(parent_element)):
                            goodParentingAndChildren = False
                            break
                    else:
                        for child_element in \
                            element.iterdescendants(tag=etree.Element):
                            if child_element.tag in instance_not_in_stack_with\
                               or utils.isInteractiveContent(child_element):
                                goodParentingAndChildren = False
                                break

                    if goodParentingAndChildren:
                        if element.tag == "span":
                            element.tag = "a"
                            element.set("href", "#" + self.dfns[term])
                            link = element
                        else:
                            link = etree.Element("a",
                                                 {"href":
                                                  "#" + self.dfns[term]})
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
                        if dump_backrefs:
                            t = utils.non_ifragment.sub("-", term.strip(utils.spaceCharacters)).strip("-")
                            id = "instance_" + t + "_" + str(len(self.instances[term]))
                            link.set("id", id)
                            self.instances[term].append(id)
                elif use_strict and term and \
                     not utils.elementHasClass(element, "secno") and \
                     not "data-anolis-spec" in element.attrib and \
                     not "data-anolis-ref" in element.attrib and \
                     not element.getparent().tag in instance_not_in_stack_with:
                    raise SyntaxError("Term not defined: %s, %s." % (term, element))

    def getTerm(self, element, w3c_compat=False,
                w3c_compat_xref_normalization=False, **kwargs):
        if element.get("data-anolis-xref") is not None:
            term = element.get("data-anolis-xref")
        elif element.get("title") is not None:
            term = element.get("title")
        else:
            term = utils.textContent(element)

        term = term.strip(utils.spaceCharacters).lower()

        term = utils.spacesRegex.sub(" ", term)

        if w3c_compat or w3c_compat_xref_normalization:
            term = non_alphanumeric_spaces.sub("", term)

        return term


class DuplicateDfnException(utils.AnolisException):
    """Term already defined."""
    pass

class XrefsFileNotCreatedYetException(utils.AnolisException):
    """The argument to --dump-xrefs does not exist yet."""
    pass
