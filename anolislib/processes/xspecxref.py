# coding=UTF-8
# Copyright (c) 2008 Geoffrey Sneddon
#               2010 Ms2ger
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

class xspecxref(object):
  """Add cross-references."""

  def __init__(self, ElementTree, **kwargs):
    self.dfns = {}
    self.notfound = []
    self.buildReferences(ElementTree, **kwargs)
    self.addReferences(ElementTree, **kwargs)

  def buildReferences(self, ElementTree, xref, allow_duplicate_dfns=False, **kwargs):
    manifest = open(xref + "/specs.json", "r")
    specs = json.load(manifest)
    manifest.close()

    for (k, v) in specs.items():
      file = open(xref + "/xrefs/" + v, "r")
      dfn = json.load(file)
      file.close()
      self.dfns[k] = { "url" : dfn["url"], "values" : dfn["definitions"] }

  def addReferences(self, ElementTree, w3c_compat=False,
                    w3c_compat_xref_elements=False,
                    w3c_compat_xref_a_placement=False,
                    use_strict=False,
                    **kwargs):
    for element in ElementTree.iter(tag=etree.Element):
      if ((element.tag in instance_elements
          or (w3c_compat or w3c_compat_xref_elements)
          and element.tag in w3c_instance_elements)
          and (element.get("data-anolis-spec") is not None)):
        term = self.getTerm(element, **kwargs)
        spec = element.get("data-anolis-spec")
        if w3c_compat:
          del element.attrib["data-anolis-spec"]
        if element.get("class") is not None:
          element.set("class", element.get("class") + " external")
        else:
          element.set("class", "external")

        if not spec in self.dfns or not self.dfns[spec]:
          raise SyntaxError("Specification not found: %s." % spec)
        if not self.dfns[spec]["values"]:
          raise SyntaxError("No values for specification: %s." % spec)
        if not term in self.dfns[spec]["values"]:
          self.notfound.append([term, spec])
          continue

        obj = self.dfns[spec]
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
            element.set("href", obj["url"] + obj["values"][term])
          else:
            link = etree.Element("a",
                       {"href":
                        obj["url"] + obj["values"][term]})
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
    if self.notfound:
      raise SyntaxError("Terms not defined: %s." % self.notfound)

  def getTerm(self, element, w3c_compat=False,
              w3c_compat_xref_normalization=False, **kwargs):
    if element.get("data-anolis-xref") is not None:
      term = element.get("data-anolis-xref")
    elif element.get("title") is not None:
      term = element.get("title")
    else:
      term = utils.textContent(element)

    term = term.strip(utils.spaceCharacters).lower()

    return utils.spacesRegex.sub(" ", term)
