def get_next_level(level_index, element_path, level_map):
    element_path = element_path[level_index:]
    for level in element_path:
        if level in level_map:
            return level

def get_next_element(element_path, element_name):
    return element_path[element_path.index(element_name) + 1]

def get_name(element):
    return element.iterchildren("Name").next().attrib['Value']

def compute_change(chunk, old_chunk):
    for attr, value in chunk["xml"].attrib.iteritems():
        for old_attr, old_value in old_chunk["xml"].attrib.iteritems():
            if old_value != value:
                return " from %s to %s" % (old_value, value)

    raise Exception("No difference found between two chunks?")

def element_left(level_index, element_path):
    return len(element_path[level_index + 1:]) > 0
