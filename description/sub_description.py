# FIXME : finish
def keytracks(level_index, v):
    v.display("clip was changed")
    if v.element_left(level_index):
        v.call_next_tag(level_index)
    else:
        for keytrack in v.chunk["xml"]:
            for note in keytrack:
                print "note: %s" % note
                print "children"
                print note.getchildren()

def clip(clip_type, prefix):
    def wrapper(level_index, v):
        if not v.element_left(level_index):
            # FIXME : added? removed?
            v.display("%s %s clip named '%s'" % (prefix, clip_type, v.get_attribute("Name")))
            v.display("Starting at %s, ending at %s" % (v.get_attribute("CurrentStart")
                                                       ,v.get_attribute("CurrentEnd")))
        else:
            clip_tag = clip_type.capitalize() + "Clip"
            parent_clip = v.element.iterancestors(clip_tag).next()
            v.display("In %s %s clip named '%s'" % (prefix.lower(), clip_type, v.get_attribute("Name", parent_clip)))
            v.display("Starting at %s, ending at %s" % (v.get_attribute("CurrentStart", parent_clip)
                                                       ,v.get_attribute("CurrentEnd", parent_clip)))
            v.call_next_tag(level_index)
        return level_index
    return wrapper

def events(level_index, v):
    if v.old_chunk is None or\
        len(v.element.getchildren()) > len(v.old_chunk["xml"].getchildren()):

        if v.element_left(level_index):
            v.call_next_tag(level_index)
        else:
            # we reached the element but there is more data inside to display
            for child in v.element: # chunk["xml"]
                v.element = child
                v.call_level_map(level_index, child.tag)
        return level_index

    v.element = v.old_chunk["xml"]
    v.call_next_tag(level_index)
    return level_index

def device(level_index, v):
    def parameter_change(device_name, v):
        parameter_name = v.get_next_element(device_name)
    
        (from_, to) = v.compute_change()
    
        v.display("%s changed from %s to %s" %\
            (parameter_name
            ,from_
            ,to))

    device_name = v.get_next_element("Devices")
 
    v.display("In a device called %s" % device_name)

    v.indent += 1
    parameter_change(device_name, v)
    v.indent -= 1

    # v.call_next_tag(level_index)
