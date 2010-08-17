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

from lxml import etree
from anolislib import utils

class lof(object):
  """Add a List of Figures."""

  def __init__(self, ElementTree, **kwargs):
    #self.figures = []
    self.tables = []
    self.readDoc(ElementTree, u"Table", u"table", u"caption", self.tables)
    self.addList(ElementTree, self.tables, u"tables")

  def readDoc(self, ElementTree, name, localName, captionLocalName, figures):
    i = 0
    for element in ElementTree.getroot().findall(u".//%s" % localName):
      i += 1
      if utils.elementHasClass(element, u"no-num"):
        continue

      if not u"id" in element.attrib:
        element.set(u"id", u"anolis-%s-%d" % (localName, i))
      id = element.get(u"id")

      cap = element.find(u".//%s" % captionLocalName)
      if not cap:
        cap = etree.Element(u"%s" % captionLocalName)
        cap.text = u"(untitled)"
        element.append(cap)

      caption = utils.textContent(cap)
      cap.text = u"%s %d: %s" % (name, i, caption)

      figures.append((id, caption))

  def addList(self, ElementTree, figures, id):
    root = ElementTree.getroot().find(u".//div[@id='anolis-listof%s']" % id)
    if root is None:
      raise SyntaxError, u"A <div id=anolis-listof%s> is required." % id
    ol = etree.Element(u"ol")
    root.append(ol)
    for figure in figures:
      a = etree.Element(u"a",
                        { u"href": u"#" + figure[0] })
      a.text = figure[1]
      li = etree.Element("li")
      li.append(a)
      ol.append(li)
