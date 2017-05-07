from pprint import pprint

def element_index(chunk):
    """
    index begins at 0 -> 1
    xml declaration does not matter -> 1
    """
    return chunk["begin_lineno"] - 3

TRACK_NAMES = {}

# iterancestors or xpath?
def get_track_name(element, element_path, track_type):
    tag = "%sTrack" % track_type.capitalize()

    track_element = element.iterancestors(tag).next()

    if track_element not in TRACK_NAMES:
        track_name = track_element.iterchildren("Name").next()
        effective_name = track_name.iterchildren("EffectiveName").next()
        TRACK_NAMES[track_element] = effective_name.attrib['Value']

    return TRACK_NAMES[track_element]

def track(track_type, prefix):
    def wrapper(element, element_path, chunk, old_chunk):
        return "In %s %s track called %s" % (prefix, track_type, get_track_name(element, element_path, track_type))
    return wrapper

def get_element_next(element_path, element_name):
    return element_path[element_path.index(element_name) + 1]

def compute_change(chunk, old_chunk):
    for attr, value in chunk["xml"].attrib.iteritems():
        for old_attr, old_value in old_chunk["xml"].attrib.iteritems():
            if old_value != value:
                return " from %s to %s" % (old_value, value)

    raise Exception("No difference found between two chunks?")

def device(element, element_path, chunk, old_chunk):
    device_name = get_element_next(element_path, "Devices")

    return "In a device called %s, %s changed %s" %\
            (device_name
            ,get_element_next(element_path, device_name)
            ,compute_change(chunk, old_chunk))

def clip_slot_list(element, element_path, chunk, old_chunk):
    if len(element.getchildren()) > len(old_chunk["xml"].getchildren()):
        clip = element.iterchildren().next()
        clip_name = clip.iterchildren("Name").next().attrib['Value']
        return "A clip was added with the name : %s" % clip_name

    clip = old_chunk["xml"].iterchildren().next()
    clip_name = clip.iterchildren("Name").next().attrib['Value']
    return "A clip was removed with the name : %s" % clip_name

def events(element, element_path, chunk, old_chunk):
    if len(element.getchildren()) > len(old_chunk["xml"].getchildren()):
        return "events added"

    return "events removed"

def arranger(element, element_path, chunk, old_chunk):
    return "Elements were changed in the arrangement view: %s" %\
            SUB_LEVEL_DESCRIPTION[element.tag](element, element_path, chunk, old_chunk)

SUB_LEVEL_DESCRIPTION = {
        "Events": events,
}

# TODO : instead of LEVEL_DESCRIPTION do?
# a recursive call : track continue and if it find devices in the element_path
# would call devices
# devices would then describe the operations that open on a device in an abstract manner?
LEVEL_DESCRIPTION = {
        "AudioTrack": track("audio", "an"),
        "MidiTrack": track("midi", "a"),
        "Devices": device,
        "ClipSlotList": clip_slot_list,
        "ArrangerAutomation": arranger,
}

# TODO:
# keep description in a list or dict for better display?

# apply blacklisting sooner? would avoid useless treatments
# Defines noisy/useless modification
BLACK_LIST = ["Selected", "FloatEvent", "CurrentTime", "SavedPlayingSlot"]

def blacklisted(level):
    for one in BLACK_LIST:
        if level.find(one) != -1:
            return True
    return False

def describe_operation(chunks, elements):
#    import pdb; pdb.set_trace()
    roottree = elements[0].getroottree()
    for chunk in chunks:
        if chunk["operation_type"] == "MODIFICATION"\
            and chunk.get("replacing") is not None:

            project_element = elements[element_index(chunk)]
            element_path = roottree.getpath(project_element)
            element_path_split = element_path.split('/')
                    
            if not blacklisted(element_path_split[-1]):
                print element_path

                indent = 0
                for level in element_path_split:
                    if level:
                        if level in LEVEL_DESCRIPTION:
                            print "%s%s" % ("\t" * indent, LEVEL_DESCRIPTION[level](project_element, element_path_split, chunk, chunks[chunk["replacing"]]))
                            indent += 1
            
            if project_element.tag != chunk["xml"].tag:
                print chunk["xml"].tag
                print elements[element_index(chunk)].tag
                raise Exception("Algorithm problem : element offset is not right")
