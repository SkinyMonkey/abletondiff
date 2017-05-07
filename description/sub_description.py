from common import get_next_level, element_left, get_next_element, compute_change

def call_next_tag(level_index, element, element_path, chunk, old_chunk):
    next_tag = get_next_level(level_index + 1, element_path, SUB_LEVEL_DESCRIPTION)
    
    if next_tag is not None:
        level_index = element_path.index(next_tag)
        return SUB_LEVEL_DESCRIPTION[next_tag](level_index, element, element_path, chunk, old_chunk)

    print element_path
    print element_path[level_index]
    raise Exception("Next tag could not be found")

def audioclip(level_index, element, element_path, chunk, old_chunk):
    # FIXME : add begin and end
    print "An audioclip named %s" % element.iterchildren("Name").next().attrib["Value"]

def events(level_index, element, element_path, chunk, old_chunk):
#    import pdb; pdb.set_trace()

    if len(element.getchildren()) > len(old_chunk["xml"].getchildren()):
        print "events were added"
        if element_left(level_index, element_path):
            call_next_tag(level_index, element, element_path, chunk, old_chunk)
        else:
            for child in element:
                SUB_LEVEL_DESCRIPTION[child.tag](level_index, child, element_path, chunk, old_chunk)

    print "events removed"

def device(level_index, element, element_path, chunk, old_chunk):
    device_name = get_next_element(element_path, "Devices")

    print "In a device called %s, %s changed %s" %\
            (device_name
            ,get_next_element(element_path, device_name)
            ,compute_change(chunk, old_chunk))

    call_next_tag(level_index, element, element_path, chunk, old_chunk)

SUB_LEVEL_DESCRIPTION = {
    "Events": events,
    "AudioClip": audioclip,
    "Devices": device,
}
