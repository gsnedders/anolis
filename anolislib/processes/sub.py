# coding=UTF-8
# Copyright (c) 2008 Geoffrey Sneddon
#           (c) 2011 Ms2ger
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
import time
import os
from lxml import etree
from copy import deepcopy

from anolislib import utils

latest_version = re.compile("latest[%s]+version" % utils.spaceCharacters,
                            re.IGNORECASE)

w3c_tr_url_status = r"http://www\.w3\.org/TR/[^/]*/(MO|WD|CR|PR|REC|PER|NOTE)-"
w3c_tr_url_status = re.compile(w3c_tr_url_status)

title = re.compile(r"\[TITLE[^\]]*\]")
title_identifier = "[TITLE"

status = re.compile(r"\[STATUS[^\]]*\]")
status_identifier = "[STATUS"

longstatus = re.compile(r"\[LONGSTATUS[^\]]*\]")
longstatus_identifier = "[LONGSTATUS"
longstatus_map = {
    "MO": "W3C Member-only Draft",
    "ED": "Editor's Draft",
    "WD": "W3C Working Draft",
    "CR": "W3C Candidate Recommendation",
    "PR": "W3C Proposed Recommendation",
    "REC": "W3C Recommendation",
    "PER": "W3C Proposed Edited Recommendation",
    "NOTE": "W3C Working Group Note"
}

shortname = re.compile(r"\[SHORTNAME[^\]]*\]")
shortname_identifier = "[SHORTNAME"

latest = re.compile(r"\[LATEST[^\]]*\]")
latest_identifier = "[LATEST"

version = re.compile(r"\[VERSION[^\]]*\]")
version_identifier = "[VERSION"

w3c_stylesheet = re.compile(r"http://www\.w3\.org/StyleSheets/TR/W3C-[A-Z]+")
w3c_stylesheet_identifier = "http://www.w3.org/StyleSheets/TR/W3C-"

basic_comment_subs = ()


class sub(object):
    """Perform substitutions."""

    def __init__(self, ElementTree, w3c_compat=False,
                 w3c_compat_substitutions=False,
                 w3c_compat_crazy_substitutions=False,
                 w3c_status='',
                 publication_date='',
                 **kwargs):
        if w3c_status:
            self.w3c_status = w3c_status
        elif w3c_compat or w3c_compat_substitutions or \
             w3c_compat_crazy_substitutions:
            self.w3c_status = self.getW3CStatus(ElementTree, **kwargs)
        else:
            self.w3c_status = ''

        self.pubdate = publication_date and time.strptime(publication_date, "%d %b %Y") or time.gmtime()

        self.stringSubstitutions(ElementTree, w3c_compat,
                                 w3c_compat_substitutions,
                                 w3c_compat_crazy_substitutions, **kwargs)
        self.commentSubstitutions(ElementTree, w3c_compat,
                                  w3c_compat_substitutions,
                                  w3c_compat_crazy_substitutions, **kwargs)

    def stringSubstitutions(self, ElementTree, w3c_compat=False,
                            w3c_compat_substitutions=False,
                            w3c_compat_crazy_substitutions=False,
                            w3c_shortname='',
                            **kwargs):
        # Get doc_title from the title element
        try:
            doc_title = utils.textContent(ElementTree.getroot().find("head")
                                                               .find("title"))
        except (AttributeError, TypeError):
            doc_title = ""

        year = re.compile(r"\[YEAR[^\]]*\]")
        year_sub = time.strftime("%Y", self.pubdate)
        year_identifier = "[YEAR"

        date = re.compile(r"\[DATE[^\]]*\]")
        date_sub = time.strftime("%d %B %Y", self.pubdate).lstrip("0")
        date_identifier = "[DATE"

        cdate = re.compile(r"\[CDATE[^\]]*\]")
        cdate_sub = time.strftime("%Y%m%d", self.pubdate)
        cdate_identifier = "[CDATE"

        udate = re.compile(r"\[UDATE[^\]]*\]")
        udate_sub = time.strftime("%Y-%m-%d", self.pubdate)
        udate_identifier = "[UDATE"

        string_subs = ((year, year_sub, year_identifier),
                       (date, date_sub, date_identifier),
                       (cdate, cdate_sub, cdate_identifier),
                       (udate, udate_sub, udate_identifier))

        if w3c_compat or w3c_compat_substitutions:
            # Get the right long status
            doc_longstatus = longstatus_map[self.w3c_status]

        if w3c_compat_crazy_substitutions:
            # Get the right stylesheet
            doc_w3c_stylesheet = "http://www.w3.org/StyleSheets/TR/W3C-%s" % (self.w3c_status, )

        # Get all the subs we want
        string_subs += ((title, doc_title, title_identifier), )

        # And even more in compat. mode
        if w3c_compat or w3c_compat_substitutions:
            try:
                shortname_sub = w3c_shortname or os.path.basename(os.getcwd())
            except OSError:
                shortname_sub = ""
            latest_sub = "http://www.w3.org/TR/%s/" % (shortname_sub, )
            version_sub = "http://www.w3.org/TR/%s/%s-%s-%s/" % (year_sub, self.w3c_status, shortname_sub, cdate_sub)
            string_subs += ((status, self.w3c_status, status_identifier),
                            (longstatus, doc_longstatus, longstatus_identifier),
                            (shortname, shortname_sub, shortname_identifier),
                            (latest, latest_sub, latest_identifier),
                            (version, version_sub, version_identifier))

        # And more that aren't even enabled by default in compat. mode
        if w3c_compat_crazy_substitutions:
            string_subs += ((w3c_stylesheet, doc_w3c_stylesheet, w3c_stylesheet_identifier), )

        for node in ElementTree.iter():
            for regex, sub, identifier in string_subs:
                if node.text is not None and identifier in node.text:
                    node.text = regex.sub(sub, node.text)
                if node.tail is not None and identifier in node.tail:
                    node.tail = regex.sub(sub, node.tail)
                for name, value in node.attrib.items():
                    if identifier in value:
                        node.attrib[name] = regex.sub(sub, value)

    def commentSubstitutions(self, ElementTree, w3c_compat=False,
                             w3c_compat_substitutions=False,
                             w3c_compat_crazy_substitutions=False,
                             enable_woolly=False,
                             **kwargs):
        # Basic substitutions
        instance_basic_comment_subs = basic_comment_subs

        # Add more basic substitutions in compat. mode
        if w3c_compat or w3c_compat_substitutions:
            copyright = "copyright"
            copyright_sub = etree.fromstring('<p class="copyright"><a href="http://www.w3.org/Consortium/Legal/ipr-notice#Copyright">Copyright</a> &#xA9; %s <a href="http://www.w3.org/"><abbr title="World Wide Web Consortium">W3C</abbr></a><sup>&#xAE;</sup> (<a href="http://www.csail.mit.edu/"><abbr title="Massachusetts Institute of Technology">MIT</abbr></a>, <a href="http://www.ercim.eu/"><abbr title="European Research Consortium for Informatics and Mathematics">ERCIM</abbr></a>, <a href="http://www.keio.ac.jp/">Keio</a>, <a href="http://ev.buaa.edu.cn/">Beihang</a>), All Rights Reserved. W3C <a href="http://www.w3.org/Consortium/Legal/ipr-notice#Legal_Disclaimer">liability</a>, <a href="http://www.w3.org/Consortium/Legal/ipr-notice#W3C_Trademarks">trademark</a> and <a href="http://www.w3.org/Consortium/Legal/copyright-documents">document use</a> rules apply.</p>' % time.strftime("%Y", self.pubdate))

            logo = "logo"
            logo_str = '<a href="http://www.w3.org/"><img height="48" width="72" alt="W3C" src="http://www.w3.org/Icons/w3c_home"/></a>'
            if enable_woolly:
                logo_str += '<a class="logo" href="https://www.w3.org/Style/Group/" rel="in-activity"><img alt="CSS WG" src="https://www.w3.org/Style/Woolly/woolly-icon"/></a>'

            logo_sub = etree.fromstring('<p>%s</p>' % logo_str)

            instance_basic_comment_subs += ((logo, logo_sub),
                                            (copyright, copyright_sub))

        # Set of nodes to remove
        to_remove = set()

        # Link
        link_parent = None
        link = None
        for node in ElementTree.iter():
            if link_parent is not None:
                if node.tag is etree.Comment and \
                   node.text.strip(utils.spaceCharacters) == "end-link":
                    if node.getparent() is not link_parent:
                        raise utils.DifferentParentException("begin-link and end-link have different parents")
                    utils.removeInteractiveContentChildren(link)
                    link.set("href", utils.textContent(link))
                    link_parent = None
                else:
                    if node.getparent() is link_parent:
                        link.append(deepcopy(node))
                    to_remove.add(node)
            elif node.tag is etree.Comment and \
                 node.text.strip(utils.spaceCharacters) == "begin-link":
                link_parent = node.getparent()
                link = etree.Element("a")
                link.text = node.tail
                node.tail = None
                node.addnext(link)

        # Basic substitutions
        for comment, sub in instance_basic_comment_subs:
            utils.replaceComment(ElementTree, comment, sub, **kwargs)

        # Remove nodes
        for node in to_remove:
            node.getparent().remove(node)

    def getW3CStatus(self, ElementTree, **kwargs):
        # Get all text nodes that contain case-insensitively "latest version"
        # with any amount of whitespace inside the phrase, or contain
        # http://www.w3.org/TR/
        for text in ElementTree.xpath("//text()[contains(translate(., 'LATEST', 'latest'), 'latest') and contains(translate(., 'VERSION', 'version'), 'version') or contains(., 'http://www.w3.org/TR/')]"):
            if latest_version.search(text):
                return "ED"
            elif w3c_tr_url_status.search(text):
                return w3c_tr_url_status.search(text).group(1)
        # Didn't find any status, return the default (ED)
        else:
            return "ED"

class DifferentParentException(utils.AnolisException):
    """begin-link and end-link do not have the same parent."""
    pass
