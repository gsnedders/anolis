# coding=UTF-8
# Copyright (c) 2010 Ms2ger
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
import simplejson as json
from lxml import etree
from anolislib import utils

class refs(object):
  """Add references section."""

  def __init__(self, ElementTree, w3c_compat=False, **kwargs):
    self.refs = {}
    self.usedrefs = []
    self.foundrefs = {}
    self.normativerefs = {}
    self.addReferencesLinks(ElementTree, w3c_compat=w3c_compat, **kwargs)
    self.usedrefs.sort()
    self.buildReferences(ElementTree, **kwargs)
    if not w3c_compat:
      self.addReferencesList(ElementTree, **kwargs)
    else:
      self.addTwoReferencesLists(ElementTree, **kwargs)

  def buildReferences(self, ElementTree, **kwargs):
    list = open("data/references.json", "rb")
    self.refs = json.load(list)
    list.close()

  def addTwoReferencesLists(self, ElementTree, **kwargs):
    informative = []
    normative = []
    for ref in self.usedrefs:
      if ref in self.normativerefs:
        normative.append(ref)
      else:
        informative.append(ref)
    self.addPartialReferencesList(ElementTree, normative, "normative", **kwargs)
    self.addPartialReferencesList(ElementTree, informative, "informative", **kwargs)

  def addPartialReferencesList(self, ElementTree, l, id, **kwargs):
    root = ElementTree.getroot().find(".//div[@id='anolis-references-%s']" % id)
    if root is None:
      raise SyntaxError, "A <div id=anolis-references-%s> is required." % id
    dl = etree.Element("dl")
    root.append(dl)
    for ref in l:
      if not ref in self.refs:
        raise SyntaxError, "Reference not defined: %s." % ref
      dt = etree.Element("dt")
      dt.set("id", "refs" + ref)
      dt.text = "[" + ref + "]\n"
      dl.append(dt)
      dl.append(self.createReference(self.refs[ref], False))

  def addReferencesList(self, ElementTree, **kwargs):
    root = ElementTree.getroot().find(".//div[@id='anolis-references']")
    if root is None:
      raise SyntaxError, "A <div id=anolis-references> is required."
    dl = etree.Element("dl")
    root.append(dl)
    for ref in self.usedrefs:
      if not ref in self.refs:
        raise SyntaxError, "Reference not defined: %s." % ref
      dt = etree.Element("dt")
      dt.set("id", "refs" + ref)
      dt.text = "[" + ref + "]\n"
      dl.append(dt)
      dl.append(self.createReference(self.refs[ref], not ref in self.normativerefs))

  def createReference(self, ref, informative):
    cite = etree.Element("cite")
    if "href" in ref:
      a = etree.Element("a")
      if "title" in ref:
        a.text = ref["title"]
      else:
        a.text = ref["href"]
      a.set("href", ref["href"])
      cite.append(a)
    elif "title" in ref:
      cite.text = ref["title"]

    cite.tail = ""
    if "authors" in ref:
      cite.tail += ", %s." % self.formatAuthors(ref["authors"])
    if "publisher" in ref:
      cite.tail += " %s.\n" % ref["publisher"]

    cite.tail += "\n"
    dd = etree.Element("dd")
    if informative:
      dd.text = "(Non-normative) "
    dd.append(cite)
    return dd

  def formatAuthors(self, authors):
    if len(authors) >= 4:
      return "%s, %s, %s et al." % tuple(authors[:3])
    if len(authors) == 1:
      return "%s" % (authors[0], )
    last = authors.pop()
    return "%s and %s" % (", ".join(authors), last)

  def addReferencesLinks(self, ElementTree, w3c_compat=False, **kwargs):
    for element in ElementTree.getroot().findall(".//span[@data-anolis-ref]"):
      if w3c_compat:
        del element.attrib["data-anolis-ref"]
      ref = element.text
      element.tag = "a"
      element.set("href", "#refs" + ref)
      element.text = "[" + ref + "]"
      if not utils.elementHasClass(element, "informative"):
        self.normativerefs[ref] = True
      if ref not in self.foundrefs:
        self.usedrefs.append(ref)
        self.foundrefs[ref] = True
