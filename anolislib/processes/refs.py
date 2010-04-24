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

class refs(object):
  """Add references section."""

  def __init__(self, ElementTree, **kwargs):
    self.refs = {}
    self.buildReferences(ElementTree, **kwargs)
    self.addReferencesList(ElementTree, **kwargs)
    self.addReferencesLinks(ElementTree, **kwargs)

  def buildReferences(self, ElementTree, **kwargs):
    list = open("references/references.json", "rb")
    self.refs = json.load(list)["references"]

  def addReferencesList(self, ElementTree, **kwargs):
    root = ElementTree.getroot().find(".//div[@id='anolis-references']")
    if root is None:
      return
    dl = etree.Element("dl")
    root.append(dl)
    for ref in self.refs:
      dt = etree.Element("dt")
      dt.set("id", "refs" + ref["key"])
      dt.text = "[" + ref["key"] + "]\n"
      dl.append(dt)
      dl.append(self.createReference(ref))

  def createReference(self, ref, **kwargs):
    a = etree.Element("a")
    a.text = ref["title"]
    a.set("href", ref["href"])

    cite = etree.Element("cite")
    cite.append(a)
    cite.tail = ", " + ref["authors"] + ". " + ref["publisher"] + ".\n"

    dd = etree.Element("dd")
    dd.append(cite)
    return dd
          
  def addReferencesLinks(self, ElementTree, **kwargs):
    for element in ElementTree.getroot().findall(".//span[@data-anolis-ref]"):
      element.tag = "a"
      element.set("href", "#refs" + element.text)
      element.text = "[" + element.text + "]"
