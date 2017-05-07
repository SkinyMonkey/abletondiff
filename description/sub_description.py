from common import get_next_level, get_next_element, get_name, element_left, compute_change

def call_next_tag(c):
    c.level_index += 1
    next_tag = get_next_level(c.level_index, c.element_path, SUB_LEVEL_DESCRIPTION)
    
    if next_tag is not None:
        c.level_index = c.element_path.index(next_tag)
        return SUB_LEVEL_DESCRIPTION[next_tag](c)

    print element_path
    print element_path[level_index]
    raise Exception("Next tag could not be found")

def audioclip(c):
    # FIXME : add begin and end
    c.indent_print("An audioclip named %s" %\
                   c.element.iterchildren("Name").next().attrib["Value"])

def events(c):
#    import pdb; pdb.set_trace()

    if len(c.element.getchildren()) > len(c.old_chunk["xml"].getchildren()):
        c.indent_print("events were added")
        if element_left(c.level_index, c.element_path):
            call_next_tag(c)
        else:
            for child in c.element:
                SUB_LEVEL_DESCRIPTION[child.tag](c)

    c.indent_print("events removed")

def device(c):
    device_name = get_next_element(c.element_path, "Devices")

    c.indent_print("In a device called %s, %s changed %s" %\
            (device_name
            ,get_next_element(c.element_path, device_name)
            ,compute_change(c.chunk, c.old_chunk)))

    call_next_tag(c)

SUB_LEVEL_DESCRIPTION = {
    "Events": events,
    "AudioClip": audioclip,
    "Devices": device,
}
