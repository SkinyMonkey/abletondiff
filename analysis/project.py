import gzip
from lxml import etree

from pprint import pprint

# FIXME : faults by one?
def element_list(tree):
    """
    Creates a list with each element and line number as index.
    """
    l = []
    for element in tree:

        l.append(element)

        if element.text is not None and element.text.strip():
           lines = element.text.split("\n")
           lines = filter(lambda line : len(line.strip()) > 0, lines) # removing \t's
           l += [ None for each in lines ] # Data and Buffer lines
           l += [ None ] # end tag
           
        if len(element.getchildren()) > 0:
            children = element_list(element)
            l += children
            l.append(None) # end tag

    #       end_line = element.sourceline + len(children) + 1)
    return l


def project_analysis(project_content):
    project = etree.fromstring(project_content)

    elements = [None, project] + element_list(project) + [None]

    if len(elements) != len(project_content.split('\n')[:-1]):
        raise Exception("Parsed number of element does not match the number of lines in the project")

    return elements
