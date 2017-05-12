from pprint import pprint

from visit_state import VisitState
from sub_description import events, clip, device, keytracks
from high_level_change import high_level_change

def arranger(level_index, v):
    v.display("In the arrangement view")
    v.call_next_tag(level_index)

def clip_slot_list(level_index, v):
    v.display("In the live view")
    if len(v.element.getchildren()) > len(v.old_chunk["xml"].getchildren()):
        clip = v.element.iterchildren().next()
        clip_name = v.get_attribute("Name", clip)
        v.display("A clip named %s was added" % clip_name)
        return
    elif len(v.element.getchildren()) < len(v.old_chunk["xml"].getchildren()):
        print v.old_chunk["xml"]
        print v.element_path
        print v.element_path[level_index:]

        clip = v.old_chunk["xml"].iterchildren().next()
        clip_name = v.get_attribute("Name", clip)
        v.display("A clip named %s was removed" % clip_name)
    return level_index

def track(track_type, prefix):
    TRACK_NAMES = {}

    def get_track_name(element, track_type):
        tag = "%sTrack" % track_type.capitalize()

        track_element = element.iterancestors(tag).next()

        if track_element not in TRACK_NAMES:
            track_name = track_element.iterchildren("Name").next()
            effective_name = track_name.iterchildren("EffectiveName").next()
            TRACK_NAMES[track_element] = effective_name.attrib['Value']

        return TRACK_NAMES[track_element]

    def wrapper(level_index, v):
        track_name = get_track_name(v.element, track_type)
        v.display("In %s %s track called %s" % (prefix, track_type, track_name))

        v.call_next_tag(level_index)

    return wrapper

def effective_name(level_index, v):
    v.display("name changed from %s to %s " %\
        (v.old_chunk["xml"].attrib['Value'], v.element.attrib['Value']))
    return level_index

def implement_me(level_index, v):
    print "Implement me"
    return level_index

LEVEL_DESCRIPTION = {
# Main containers
# display data about themselves
    "ClipSlotList": clip_slot_list,
    "ArrangerAutomation": arranger,

    "AudioTrack": track("audio", "an"),
    "MidiTrack": track("midi", "a"),

# Intermediate containers
# do not display, just call
    "Events": events,

# Elements
    "AudioClip": clip("audio", "An"),
    "MidiClip": clip("midi", "A"),

# Leaves :
# do not call next tag
    "Devices": device,
    "KeyTracks": keytracks,

    "EffectiveName": effective_name,
}

# FIXME : implement
def element_index(chunk):
    """
    index begins at 0 -> +1
    not sure why -> +1
    """
    return chunk["begin_lineno"] - 2

# TODO:
# keep description in a list or dict for better display?

def describe_operation(chunks, elements):

    def get_first_previous_tag(chunk, elements):
        current_state_element = None
        index = element_index(chunk)
        while current_state_element is None:
            current_state_element = elements[index]
            index -= 1
        return current_state_element
    
    
    def coherence_check(project_element, chunk):
        if project_element.tag != chunk["xml"].tag:
            print chunk["xml"].tag
            print project_element.tag
            raise Exception("Algorithm problem : element offset is not right")

    roottree = elements[1].getroottree()
    for chunk in chunks:
        if high_level_change(chunk):
            continue

        current_state_element = elements[element_index(chunk)]

        # We get back to the last valid element
        if current_state_element is None:
            current_state_element = get_first_previous_tag(chunk, elements)

        element_path = roottree.getpath(current_state_element)
        element_path_split = element_path.split('/')[1:]
        v = None

        if chunk["operation_type"] == "MODIFICATION"\
           and chunk.get("replacing") is not None:

           coherence_check(current_state_element, chunk)

           v = VisitState(current_state_element\
                         ,element_path_split\
                         ,chunk\
                         ,chunks[chunk["replacing"]]
                         ,LEVEL_DESCRIPTION)
 
        elif chunk["operation_type"] == "ADDITION":

           coherence_check(current_state_element, chunk)

           v = VisitState(current_state_element\
                         ,element_path_split\
                         ,chunk\
                         ,None
                         ,LEVEL_DESCRIPTION)
           
        elif chunk["operation_type"] == "SUPPRESSION":
           # no need for coherence check : the element was removed

           v = VisitState(current_state_element\
                         ,element_path_split\
                         ,None\
                         ,chunk
                         ,LEVEL_DESCRIPTION)

        if v is not None:
            v.call_next_tag(0)
