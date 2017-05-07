from pprint import pprint

from root_description import track, LEVEL_DESCRIPTION

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
                        LEVEL_DESCRIPTION[level](level_index, project_element, element_path_split, chunk, chunks[chunk["replacing"]])
                        break
