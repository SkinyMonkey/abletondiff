from pprint import pprint

from root_description import track, LEVEL_DESCRIPTION

class Cursor(object):
    """
    level_index = current level in the element_path
    element = targeted element in the existing project
    element_path = split path of the element
    chunk = chunk found in the new version
    old_chunk = chunk found in the old version
    """
    def __init__(self, level_index, element, element_path, chunk, old_chunk):
        super(Cursor, self).__init__()
        self.level_index = level_index
        self.element = element
        self.element_path = element_path
        self.chunk = chunk
        self.old_chunk = old_chunk
        self.indent = 0

    def indent_print(self, toprint):
        print "%s%s" % (self.indent * "\t", toprint)
        self.indent += 1

# TODO:
# keep description in a list or dict for better display?

def element_index(chunk):
    """
    index begins at 0 -> 1
    xml declaration does not matter -> 1
    """
    return chunk["begin_lineno"] - 3

# apply blacklisting sooner? would avoid useless treatments
# Defines noisy/useless modification
BLACK_LIST = ["Selected", "FloatEvent", "CurrentTime", "SavedPlayingSlot"]

def blacklisted(level):
    for one in BLACK_LIST:
        if level.find(one) != -1:
            return True
    return False

def describe_operation(chunks, elements):
    roottree = elements[0].getroottree()
    for chunk in chunks:
        if chunk["operation_type"] == "MODIFICATION"\
            and chunk.get("replacing") is not None:

            project_element = elements[element_index(chunk)]
            element_path = roottree.getpath(project_element)
            element_path_split = element_path.split('/')
                    
            if project_element.tag != chunk["xml"].tag:
                print chunk["xml"].tag
                print elements[element_index(chunk)].tag
                raise Exception("Algorithm problem : element offset is not right")

            if not blacklisted(element_path_split[-1]):
                print element_path

                for level in LEVEL_DESCRIPTION:
                    try:
                        level_index = element_path_split.index(level)
                    except:
                        level_index = None

                    cursor = Cursor(level_index
                                   ,project_element
                                   ,element_path_split
                                   ,chunk
                                   ,chunks[chunk["replacing"]])

                    if level_index is not None:
                        LEVEL_DESCRIPTION[level](cursor)
                        break
