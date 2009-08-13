from lxml import etree
import urlparse
import urllib2

statuses =   {"UNKNOWN": "Section",
              "TBW": "Idea; yet to be specified",
              "WIP": "Being edited right now",
              "OCBE": "Overcome by events",
              "FD": "First draft",
              "WD": "Working draft",
              "CWD": "Controversial Working Draft",
              "LC": "Last call for comments",
              "ATRISK": "Being considered for removal",
              "CR": "Awaiting implementation feedback",
              "REC": "Implemented and widely deployed",
              "SPLITFD": "Marked for extraction - First draft",
              "SPLIT": "Marked for extraction - Awaiting implementation feedback",
              "SPLITREC": "Marked for extraction - Implemented and widely deployed"}

url = 'http://www.whatwg.org/specs/web-apps/current-work/status.cgi?action=get-all-annotations'

def annotate(ElementTree, **kwargs):
    if not "annotation" in kwargs or not  kwargs["annotation"]:
        return
    else:
        annotation_location = kwargs["annotation"]

    if urlparse.urlsplit(annotation_location)[0]:
        annotations_data = urllib2.urlopen(annotation_location)
    else:
        annotations_data = open(annotations_data)

    annotations = etree.parse(annotations_data)
    entries = {}
    used_entries = set([])
    for entry in annotations.xpath("//entry"):
        entries[entry.attrib["section"]] = entry

   
    for element in ElementTree.getroot().iterdescendants():
        if "id" in element.attrib and element.attrib["id"] in entries:    
            entry = entries[element.attrib["id"]]
            annotation = make_annotation(entry)
            element.addnext(annotation)
            used_entries.add(element.attrib["id"])
#        print "Missed %i of %i"%(len(set(entries.keys()) - used_entries),
#                                 len(entries))


def make_annotation(entry):
    p = etree.Element("p")
    status = etree.Element("b")
    status.text = "Status: "
    status_text = etree.Element("i")
    status_text.text = statuses[entry.attrib["status"]]
    p.append(status)
    p.append(status_text)
    return p
