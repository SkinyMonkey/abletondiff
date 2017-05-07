def audioclip(level_index, v):
    # FIXME : add begin and end
    v.display("An audioclip named %s" % v.get_attribute("Name"))
    v.display("Starting at %s, ending at %s" % (v.get_attribute("CurrentStart"), v.get_attribute("CurrentEnd")))
    return level_index

def events(level_index, v):
    if v.old_chunk is None or\
        len(v.element.getchildren()) > len(v.old_chunk["xml"].getchildren()):
        v.display("events were added")
        if v.element_left(level_index):
            v.call_next_tag(level_index)
        else:
            for child in v.element:
                v.element = child
                v.call_level_map(level_index, child.tag)
        return level_index

    v.display("events removed")
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
