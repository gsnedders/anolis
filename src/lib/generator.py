# coding=UTF-8
# Copyright (c) 2009 Geoffrey Sneddon
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
import types
import lxml.html
import html5lib

def process(trees, processes, **kwargs):
    for processObject in processes:
        process = processObject(**kwargs)
        if isinstance(process, types.FunctionType):
            passes = (process,)
        else:
            passes = [getattr(process, u"pass%i" % i) for i in
                      xrange(1, process.passes + 1)]
        for current in passes:
            for tree, url in trees:
                current(tree, url, **kwargs)

class File(object):
    def __init__(self, input, output, url, parser = u"html5lib",
                 serializer = u"html5lib",
                 output_encoding = u"utf-8"):
        self._input = input
        self._output = output
        self._url = url
        self._parser = parser
        self._serializer = serializer
        self._output_encoding = output_encoding
        
        if parser == "xml":
            self._tree = etree.parse(input)
        elif parser == "lxml.html":
            self._tree = lxml.html.parse(input)
        elif parser == "html5lib":
            self._tree = html5lib.parse(input, treebuilder="lxml")
        else:
            raise Exception("Unknown parser!")
    
    def __getattr__(self, name):
        return getattr(self, u"_%s" % name)

def files(files, processes, **kwargs):
    trees = []
    for file in files:
        trees.append((file.tree, file.url))
    
    process(trees, processes, **kwargs)
    
    for file in files:
        if file.serializer == "xml":
            output.write(etree.tostring(file.tree,
                                        encoding=file.output_encoding))
        elif file.serializer == "lxml.html":
            output.write(lxml.html.tostring(file.tree,
                                            encoding=file.output_encoding))
        else:
            walker = html5lib.treewalkers.getTreeWalker("lxml")
            s = html5lib.htmlserializer.HTMLSerializer(**kwargs)
            for n in s.serialize(walker(file.tree),
                                 encoding=file.output_encoding):
                output.write(n)
