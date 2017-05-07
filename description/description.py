from pprint import pprint

from visit_state import VisitState
from sub_description import events, audioclip, device

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

    clip = v.old_chunk["xml"].iterchildren().next()
    clip_name = v.get_attribute("Name", clip)
    v.display("A clip named %s was removed" % clip_name)
    return level_index


def track(track_type, prefix):
    TRACK_NAMES = {}

    def get_track_name(element, element_path, track_type):
        tag = "%sTrack" % track_type.capitalize()

        track_element = element.iterancestors(tag).next()

        if track_element not in TRACK_NAMES:
            track_name = track_element.iterchildren("Name").next()
            effective_name = track_name.iterchildren("EffectiveName").next()
            TRACK_NAMES[track_element] = effective_name.attrib['Value']

        return TRACK_NAMES[track_element]

    def wrapper(level_index, v):
        track_name = get_track_name(v.element, v.element_path, track_type)
        v.display("In %s %s track called %s" % (prefix, track_type, track_name))

        v.call_next_tag(level_index)

    return wrapper

LEVEL_DESCRIPTION = {
# Main containers
    "AudioTrack": track("audio", "an"),
    "MidiTrack": track("midi", "a"),

    "ClipSlotList": clip_slot_list,
    "ArrangerAutomation": arranger,

# Elements
    "Events": events,
    "AudioClip": audioclip,
    "Devices": device,
}

def element_index(chunk):
    """
    index begins at 0 -> +1
    xml declaration does not matter -> +1
    not sure why -> +1
    """
    return chunk["begin_lineno"] - 3

# TODO:
# keep description in a list or dict for better display?

def coherence_check(project_element, chunk):
    if project_element.tag != chunk["xml"].tag:
        print chunk["xml"].tag
        print project_element.tag
        raise Exception("Algorithm problem : element offset is not right")

def describe_operation(chunks, elements):
    roottree = elements[0].getroottree()
    for chunk in chunks:
        if chunk["operation_type"] == "MODIFICATION"\
           and chunk.get("replacing") is not None:

           current_state_element = elements[element_index(chunk)]
           element_path = roottree.getpath(current_state_element)
           element_path_split = element_path.split('/')[1:]
           
           coherence_check(current_state_element, chunk)

           v = VisitState(current_state_element\
                         ,element_path_split\
                         ,chunk\
                         ,chunks[chunk["replacing"]]
                         ,LEVEL_DESCRIPTION)
 
           v.call_next_tag(0)
