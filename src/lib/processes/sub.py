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
import time
from lxml import etree
from copy import deepcopy

import utils

latest_version = re.compile(u"latest[%s]+version" % utils.spaceCharacters,
                            re.IGNORECASE)

w3c_tr_url_status = r"http://www\.w3\.org/TR/[^/]*/(MO|WD|CR|PR|REC|PER|NOTE)-"
w3c_tr_url_status = re.compile(w3c_tr_url_status)

year = re.compile(r"\[YEAR[^\]]*\]")
year_sub = time.strftime(u"%Y", time.gmtime())
year_identifier = u"[YEAR"

date = re.compile(r"\[DATE[^\]]*\]")
date_sub = time.strftime(u"%d %B %Y", time.gmtime()).lstrip(u"0")
date_identifier = u"[DATE"

cdate = re.compile(r"\[CDATE[^\]]*\]")
cdate_sub = time.strftime(u"%Y%m%d", time.gmtime())
cdate_identifier = u"[CDATE"

title = re.compile(r"\[TITLE[^\]]*\]")
title_identifier = u"[TITLE"

status = re.compile(r"\[STATUS[^\]]*\]")
status_identifier = u"[STATUS"

longstatus = re.compile(r"\[LONGSTATUS[^\]]*\]")
longstatus_identifier = u"[LONGSTATUS"
longstatus_map = {
    u"MO": u"W3C Member-only Draft",
    u"ED": u"Editor's Draft",
    u"WD": u"W3C Working Draft",
    u"CR": u"W3C Candidate Recommendation",
    u"PR": u"W3C Proposed Recommendation",
    u"REC": u"W3C Recommendation",
    u"PER": u"W3C Proposed Edited Recommendation",
    u"NOTE": u"W3C Working Group Note"
}

w3c_stylesheet = re.compile(r"http://www\.w3\.org/StyleSheets/TR/W3C-[A-Z]+")
w3c_stylesheet_identifier = u"http://www.w3.org/StyleSheets/TR/W3C-"

logo = u"logo"
logo_sub = etree.fromstring(u'<p xmlns="http://www.w3.org/1999/xhtml"><a href="http://www.w3.org/"><img alt="W3C" src="http://www.w3.org/Icons/w3c_home"/></a></p>')

copyright = u"copyright"
copyright_sub = etree.fromstring(u'<p class="copyright" xmlns="http://www.w3.org/1999/xhtml"><a href="http://www.w3.org/Consortium/Legal/ipr-notice#Copyright">Copyright</a> &#xA9; %s <a href="http://www.w3.org/"><acronym title="World Wide Web Consortium">W3C</acronym></a><sup>&#xAE;</sup> (<a href="http://www.csail.mit.edu/"><acronym title="Massachusetts Institute of Technology">MIT</acronym></a>, <a href="http://www.ercim.org/"><acronym title="European Research Consortium for Informatics and Mathematics">ERCIM</acronym></a>, <a href="http://www.keio.ac.jp/">Keio</a>), All Rights Reserved. W3C <a href="http://www.w3.org/Consortium/Legal/ipr-notice#Legal_Disclaimer">liability</a>, <a href="http://www.w3.org/Consortium/Legal/ipr-notice#W3C_Trademarks">trademark</a> and <a href="http://www.w3.org/Consortium/Legal/copyright-documents">document use</a> rules apply.</p>' % time.strftime(u"%Y", time.gmtime()))

basic_comment_subs = ()

def Process(tree, url, w3c_compat=False, w3c_compat_substitutions=False,
            w3c_compat_crazy_substitutions=False, **kwargs):
    xml = etree.tostring(tree)
    string_substitutions = []
    if year_identifier in xml:
        string_substitutions.append((year, year_sub, year_identifier))
        
    if date_identifier in xml:
        string_substitutions.append((date, date_sub, date_identifier))
        
    if cdate_identifier in xml:
        string_substitutions.append((cdate, cdate_sub, cdate_identifier))
        
    if title_identifier in xml:
        try:
            title_sub = utils.textContent(tree.getroot().find(u"{http://www.w3.org/1999/xhtml}head")
                                                        .find(u"{http://www.w3.org/1999/xhtml}title"))
        except (AttributeError, TypeError):
            title_sub = u""
        string_substitutions.append((title, title_sub, title_identifier))
    
    if w3c_compat or w3c_compat_substitutions:
        if status_identifier in xml:
            w3c_status = getW3CStatus(tree)
            string_substitutions.append([status, w3c_status, status_identifier])
        
        if longstatus_identifier in xml:
            try:
                w3c_status
            except NameError:
                w3c_status = getW3CStatus(tree)
            string_substitutions.append([longstatus, w3c_status, longstatus_identifier])
    
    if w3c_compat_crazy_substitutions:
        if w3c_stylesheet_identifier in xml:
            try:
                w3c_status
            except NameError:
                w3c_status = getW3CStatus(tree)
            stylesheet = u"http://www.w3.org/StyleSheets/TR/W3C-%s" % w3c_status
            string_substitutions.append([w3c_stylesheet, stylesheet, w3c_stylesheet_identifier])
    
    if string_substitutions:
        doStringSubstitutions(string_substitutions, tree)
    
    comment_substitutions = {}
    
    if w3c_compat or w3c_compat_substitutions:
        if logo in xml:
            comment_substitutions[logo] = logo_sub
        
        if copyright in xml:
            comment_substitutions[copyright] = copyright_sub
    
    if comment_substitutions:
        doCommentSubstitutions(comment_substitutions, tree)

def doStringSubstitutions(string_substitutions, tree):
    for node in tree.iter():
        for regex, sub, identifier in string_substitutions:
            if node.text is not None and identifier in node.text:
                node.text = regex.sub(sub, node.text)
            if node.tail is not None and identifier in node.tail:
                node.tail = regex.sub(sub, node.tail)
            for name, value in node.attrib.items():
                if identifier in value:
                    node.attrib[name] = regex.sub(sub, value)

def doCommentSubstitutions(comment_substitutions, tree):
    in_sub = False
    to_remove = set()
    for node in tree.iter():
        if in_sub:
            if (node.tag is etree.Comment and
                node.text.strip(utils.spaceCharacters) == u"end-%s" % in_sub):
                if node.getparent() is not sub_parent:
                    raise DifferentParentException(u"%s and %s have different parents" % begin_sub, end_sub)
                in_sub = False
            else:
                to_remove.add(node)
        elif node.tag is etree.Comment:
            stripped = node.text.strip(utils.spaceCharacters)
            if stripped in comment_substitutions:
                node.addprevious(etree.Comment(u"begin-%s" % stripped))
                node.addprevious(deepcopy(comment_substitutions[stripped]))
                node.addprevious(etree.Comment(u"end-%s" % stripped))
                node.getprevious().tail = node.tail
                to_remove.add(node)
            elif (stripped.startswith(u"begin-") and
                  stripped[6:] in comment_substitutions):
                sub_parent = node.getparent()
                in_sub = stripped[6:]
                node.tail = None
                node.addnext(deepcopy(comment_substitutions[stripped[6:]]))

    for node in to_remove:
        node.getparent().remove(node)

def getW3CStatus(self, tree):
    for text in tree.xpath(u"//text()[contains(translate(., 'LATEST', 'latest'), 'latest') and contains(translate(., 'VERSION', 'version'), 'version') or contains(., 'http://www.w3.org/TR/')]"):
        if latest_version.search(text):
            return u"ED"
        elif w3c_tr_url_status.search(text):
            return w3c_tr_url_status.search(text).group(1)
    # Didn't find any status, return the default (ED)
    else:
        return u"ED"
