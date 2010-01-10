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

import re
import sys
from lxml import etree
import urlparse
from collections import deque

from html5lib.constants import spaceCharacters

ids = {}

spaceCharacters = u"".join(spaceCharacters)
spacesRegex = re.compile(u"[%s]+" % spaceCharacters)

heading_content = frozenset([u"{http://www.w3.org/1999/xhtml}h1",
                             u"{http://www.w3.org/1999/xhtml}h2",
                             u"{http://www.w3.org/1999/xhtml}h3",
                             u"{http://www.w3.org/1999/xhtml}h4",
                             u"{http://www.w3.org/1999/xhtml}h5",
                             u"{http://www.w3.org/1999/xhtml}h6",
                             u"{http://www.w3.org/1999/xhtml}hgroup"])
                             
sectioning_content = frozenset([u"{http://www.w3.org/1999/xhtml}section",
                                u"{http://www.w3.org/1999/xhtml}nav",
                                u"{http://www.w3.org/1999/xhtml}article",
                                u"{http://www.w3.org/1999/xhtml}aside"])
                                
sectioning_root = frozenset([u"{http://www.w3.org/1999/xhtml}body",
                             u"{http://www.w3.org/1999/xhtml}blockquote",
                             u"{http://www.w3.org/1999/xhtml}figure",
                             u"{http://www.w3.org/1999/xhtml}td",
                             u"{http://www.w3.org/1999/xhtml}datagrid"])

always_interactive_content = frozenset([u"{http://www.w3.org/1999/xhtml}a",
                                        u"{http://www.w3.org/1999/xhtml}bb",
                                        u"{http://www.w3.org/1999/xhtml}details",
                                        u"{http://www.w3.org/1999/xhtml}datagrid"])
media_elements = frozenset([u"{http://www.w3.org/1999/xhtml}audio",
                            u"{http://www.w3.org/1999/xhtml}video"])

non_sgml_name = re.compile("[^A-Za-z0-9_:.]+")

html4ish_dtd = frozenset([u"-//W3C//DTD HTML 4.0//EN",
                          u"-//W3C//DTD HTML 4.0 Transitional//EN",
                          u"-//W3C//DTD HTML 4.0 Frameset//EN",
                          u"-//W3C//DTD HTML 4.01//EN",
                          u"-//W3C//DTD HTML 4.01 Transitional//EN",
                          u"-//W3C//DTD HTML 4.01 Frameset//EN",
                          u"ISO/IEC 15445:2000//DTD HyperText Markup Language//EN",
                          u"ISO/IEC 15445:2000//DTD HTML//EN",
                          u"-//W3C//DTD XHTML 1.0 Strict//EN",
                          u"-//W3C//DTD XHTML 1.0 Transitional//EN",
                          u"-//W3C//DTD XHTML 1.0 Frameset//EN",
                          u"-//W3C//DTD XHTML 1.1//EN"])

if sys.maxunicode == 0xFFFF:
    # UTF-16 Python
    non_ifragment = re.compile(u"([\u0000-\u0020\u0022\u0023\u0025\\\u002D\u003C\u003E\u005B-\u005E\u0060\u007B-\u007D\u007F-\u0099\uD800-\uF8FF\uFDD0-\uFDDF\uFFF0-\uFFFF]|\U0001FFFE|\U0001FFFF|\U0002FFFE|\U0002FFFF|\U0003FFFE|\U0003FFFF|\U0004FFFE|\U0004FFFF|\U0005FFFE|\U0005FFFF|\U0006FFFE|\U0006FFFF|\U0007FFFE|\U0007FFFF|\U0008FFFE|\U0008FFFF|\U0009FFFE|\U0009FFFF|\U000AFFFE|\U000AFFFF|\U000BFFFE|\U000BFFFF|\U000CFFFE|\U000CFFFF|\uDB3F[\uDFFE-\uDFFF]|[\uDB40-\uDB43][\uDC00-\uDFFF]|\uDB7F[\uDFFE-\uDFFF]|[\uDB80-\uDBFF][\uDC00-\uDFFF])+")
else:
    # UTF-32 Python
    non_ifragment = re.compile(u"[^A-Za-z0-9._~!$&'()*+,;=:@/?\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF\U00010000-\U0001FFFD\U00020000-\U0002FFFD\U00030000-\U0003FFFD\U00040000-\U0004FFFD\U00050000-\U0005FFFD\U00060000-\U0006FFFD\U00070000-\U0007FFFD\U00080000-\U0008FFFD\U00090000-\U0009FFFD\U000A0000-\U000AFFFD\U000B0000-\U000BFFFD\U000C0000-\U000CFFFD\U000D0000-\U000DFFFD\U000E1000-\U000EFFFD]+")


def splitOnSpaces(string):
    return spacesRegex.split(string)


def elementHasClass(element, class_name):
    if (element.get(u"class") and
        class_name in splitOnSpaces(element.get(u"class"))):
        return True
    else:
        return False


def generateID(element, force_html4_id=False, **kwargs):
    if element.get(u"id") is not None:
        return element.get(u"id")
    elif (element.get(u"title") is not None and
          element.get(u"title").strip(spaceCharacters)):
        source = element.get(u"title")
    else:
        source = textContent(element)

    source = source.strip(spaceCharacters).lower()

    if not source:
        source = u"generatedID"
    elif (force_html4_id or
          element.getroottree().docinfo.public_id in html4ish_dtd):
        source = non_sgml_name.sub(u"-", source).strip(u"-")
        try:
            if not source[0].isalpha():
                source = u"x%s" % source
        except IndexError:
            source = u"generatedID"
    else:
        source = non_ifragment.sub(u"-", source).strip(u"-")
        if not source:
            source = u"generatedID"

    return source


def textContent(element):
    return etree.tostring(element, encoding=unicode, method='text',
                          with_tail=False)


def removeInteractiveContentChildren(element):
    to_remove = set()
    for child in element.iterdescendants():
        if isInteractiveContent(child):
            copyContentForRemoval(child)
            to_remove.add(child)
    for node in to_remove:
        node.getparent().remove(node)


def isInteractiveContent(element):
    if (element.tag in always_interactive_content or
        element.tag in media_elements and element.get(u"controls") is not None or
        element.tag is u"{http://www.w3.org/1999/xhtml}menu" and 
            element.get(u"type") is not None and
            element.get(u"type").lower() == u"toolbar"):
        return True
    else:
        return False


def copyContentForRemoval(node, text=True, children=True, tail=True):
    # Preserve the text, if it is an element
    if isinstance(node.tag, basestring) and node.text is not None and text:
        if node.getprevious() is not None:
            if node.getprevious().tail is None:
                node.getprevious().tail = node.text
            else:
                node.getprevious().tail += node.text
        else:
            if node.getparent().text is None:
                node.getparent().text = node.text
            else:
                node.getparent().text += node.text
    # Re-parent all the children of the element we're removing
    if children:
        for child in node:
            node.addprevious(child)
    # Preserve the element tail
    if node.tail is not None and tail:
        if node.getprevious() is not None:
            if node.getprevious().tail is None:
                node.getprevious().tail = node.tail
            else:
                node.getprevious().tail += node.tail
        else:
            if node.getparent().text is None:
                node.getparent().text = node.tail
            else:
                node.getparent().text += node.tail


def relativeURL(base, to):
    base = urlparse.urlsplit(base)
    to = urlparse.urlsplit(to)
    result = []
    if base.scheme == to.scheme:
        result.append(u"")
        if base.netloc == to.netloc:
            result.append(u"")
            if base.path == to.path:
                result.append(u"")
                if base.query == to.query:
                    result.append(u"")
                else:
                    result.append(to.query)
            else:
                basesegments = deque(base.path.split(u"/"))
                tosegments = deque(to.path.split(u"/"))
                if basesegments[0] != tosegments[0]:
                    result.extend(to[2:4])
                else:
                    basesegments.pop()
                    try:
                        while basesegments[0] == tosegments[0]:
                            basesegments.popleft()
                            last = tosegments.popleft()
                    except IndexError:
                        pass
                    if not basesegments:
                        result.append(u"/".join(tosegments))
                    elif not tosegments:
                        result.append(u"../" * (len(basesegments) + 1) + last)
                    else:
                        result.append(u"../" * len(basesegments) +
                                      u"/".join(tosegments))
                result.append(to.query)
        else:
            result.extend(to[1:4])
        result.append(to.fragment)
    else:
        result = to
    return urlparse.urlunsplit(result)


class AnolisException(Exception):
    """Generic anolis error."""
    pass
