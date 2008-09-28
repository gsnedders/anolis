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

import html5lib
from html5lib import treebuilders, treewalkers, serializer
import lxml.html
from lxml import etree


def process(tree, processes=set(["sub", "toc", "xref"]), **kwargs):
    """ Process the given tree. """

    # Find number of passes to do
    for process in processes:
        try:
            process_module = getattr(__import__('processes', globals(),
                                                locals(), [process], -1),
                                    process)
        except ImportError:
            process_module = __import__(process, globals(), locals(), [], -1)

        getattr(process_module, process)(tree, **kwargs)


def fromFile(input, processes=set(["sub", "toc", "xref"]), xml=False,
             lxml_html=False, profile=False, **kwargs):
    # Parse as XML:
    #if xml:
    if False:
        tree = etree.parse(input)
    # Parse as HTML using lxml.html
    elif lxml_html:
        tree = lxml.html.parse(input)
    # Parse as HTML using html5lib
    else:
        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml",
                                                                      etree))
        tree = parser.parse(input)

    # Close the input file
    input.close()

    # Run the generator, and profile, or not, as the case may be
    if profile:
        import hotshot
        import hotshot.stats
        import os
        import tempfile
        statfile = tempfile.mkstemp()[1]
        prof = hotshot.Profile(statfile)
        prof.runcall(process, tree, processes, **kwargs)
        prof.close()
        stats = hotshot.stats.load(statfile)
        stats.strip_dirs()
        stats.sort_stats('time')
        stats.print_stats()
        os.remove(statfile)
    else:
        process(tree, processes, **kwargs)

    # Return the tree
    return tree


def toFile(tree, output, xml=False, lxml_html=False, **kwargs):
    # Serialize to XML
    #if xml:
    if False:
        rendered = etree.tostring(tree, encoding="utf-8")
    # Serialize to HTML using lxml.html
    elif lxml_html:
        rendered = lxml.html.tostring(tree, encoding="utf-8")
    # Serialize to HTML using html5lib
    else:
        walker = treewalkers.getTreeWalker("lxml")
        s = serializer.htmlserializer.HTMLSerializer(**kwargs)
        rendered = s.render(walker(tree), encoding="utf-8")

    # Write to the output
    output.write(rendered)


def fromToFile(input, output, **kwargs):
    tree = fromFile(input, **kwargs)
    toFile(tree, output, **kwargs)
