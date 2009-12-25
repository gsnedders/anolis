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

def process(trees, processes, **kwargs):
    for processModule in processes:
        process = processModule.Process(**kwargs)
        passes = [getattr(process, u"pass%i" % i) for i in
                  xrange(1, process.passes + 1)]
        for current in passes:
            for tree, url in trees:
                current(tree, url, **kwargs)


def file(files, processes, **kwargs):
    trees = []
    for input, output, parser, serializer, output_encoding, url in files:
        if parser == "xml":
            tree = etree.parse(input)
        elif parser == "lxml.html":
            tree = lxml.html.parse(input)
        else:
            tree = html5lib.parse(input, treebuilder="lxml")
        
        trees.append((tree, url))
    
    process(trees, processes, **kwargs)
    
    for atree, afile in zip(trees, files):
        tree = atree[0]
        input, output, parser, serializer, output_encoding, url = afile
        
        if serializer == "xml":
            output.write(etree.tostring(tree, encoding=output_encoding))
        elif serializer == "lxml.html":
            output.write(lxml.html.tostring(tree, encoding=output_encoding))
        else:
            walker = treewalkers.getTreeWalker("lxml")
            s = htmlserializer.HTMLSerializer(**kwargs)
            for n in s.serialize(walker(tree), encoding=output_encoding):
                output.write(n)
