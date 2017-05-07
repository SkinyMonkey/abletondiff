from sub_description import SUB_LEVEL_DESCRIPTION
from common import get_next_level, get_next_element, compute_change

def call_next_tag(c):
    c.level_index += 1
    next_tag = get_next_level(c.level_index, c.element_path, LEVEL_DESCRIPTION)

    if next_tag is not None:
        c.level_index = c.element_path.index(next_tag)
        return LEVEL_DESCRIPTION[next_tag](c)

    next_tag = get_next_level(c.level_index, c.element_path, SUB_LEVEL_DESCRIPTION)
    
    if next_tag is not None:
        c.level_index = c.element_path.index(next_tag)
        return SUB_LEVEL_DESCRIPTION[next_tag](c)

    print c.element_path[c.level_index]
    print c.element_path
    raise Exception("Next tag could not be found")

def arranger(c):
    c.indent_print("Elements were changed in the arrangement view")
    call_next_tag(c)

def clip_slot_list(c):
    if len(c.element.getchildren()) > len(c.old_chunk["xml"].getchildren()):
        clip = c.element.iterchildren().next()
        clip_name = clip.iterchildren("Name").next().attrib['Value']
        # clip_name = get_name(clip)
        c.indent_print("A clip was added with the name : %s" % clip_name)
        return

    clip = c.old_chunk["xml"].iterchildren().next()
    clip_name = clip.iterchildren("Name").next().attrib['Value']
    # clip_name = get_name(clip)
    cd.indent_print("A clip was removed with the name : %s" % clip_name)
    return

TRACK_NAMES = {}

def get_track_name(element, element_path, track_type):
    tag = "%sTrack" % track_type.capitalize()

    track_element = element.iterancestors(tag).next()

    if track_element not in TRACK_NAMES:
        track_name = track_element.iterchildren("Name").next()
        effective_name = track_name.iterchildren("EffectiveName").next()
        TRACK_NAMES[track_element] = effective_name.attrib['Value']

    return TRACK_NAMES[track_element]

def track(track_type, prefix):
    def wrapper(c):
        track_name = get_track_name(c.element, c.element_path, track_type)
        c.indent_print("In %s %s track called %s" % (prefix, track_type, track_name))

        call_next_tag(c)

    return wrapper

# first level functions
LEVEL_DESCRIPTION = {
        "AudioTrack": track("audio", "an"),
        "MidiTrack": track("midi", "a"),
        "ClipSlotList": clip_slot_list,
        "ArrangerAutomation": arranger,
}
