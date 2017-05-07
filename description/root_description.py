from sub_description import SUB_LEVEL_DESCRIPTION
from common import get_next_level, get_next_element, compute_change

def call_next_tag(level_index, element, element_path, chunk, old_chunk):
    next_tag = get_next_level(level_index + 1, element_path, LEVEL_DESCRIPTION)

    if next_tag is not None:
        level_index = element_path.index(next_tag)
        return LEVEL_DESCRIPTION[next_tag](level_index, element, element_path, chunk, old_chunk)

    next_tag = get_next_level(level_index + 1, element_path, SUB_LEVEL_DESCRIPTION)
    
    if next_tag is not None:
        level_index = element_path.index(next_tag)
        return SUB_LEVEL_DESCRIPTION[next_tag](level_index, element, element_path, chunk, old_chunk)

    print element_path[level_index]
    print element_path
    raise Exception("Next tag could not be found")

def arranger(level_index, element, element_path, chunk, old_chunk):
    print "Elements were changed in the arrangement view"
    call_next_tag(level_index, element, element_path, chunk, old_chunk)

def clip_slot_list(level_index, element, element_path, chunk, old_chunk):
    if len(element.getchildren()) > len(old_chunk["xml"].getchildren()):
        clip = element.iterchildren().next()
        clip_name = clip.iterchildren("Name").next().attrib['Value']
        # clip_name = get_name(clip)
        print "A clip was added with the name : %s" % clip_name
        return

    clip = old_chunk["xml"].iterchildren().next()
    clip_name = clip.iterchildren("Name").next().attrib['Value']
    # clip_name = get_name(clip)
    print "A clip was removed with the name : %s" % clip_name
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
    def wrapper(level_index, element, element_path, chunk, old_chunk):
        track_name = get_track_name(element, element_path, track_type)
        print "In %s %s track called %s" % (prefix, track_type, track_name)

        call_next_tag(level_index, element, element_path, chunk, old_chunk)

    return wrapper

# first level functions
LEVEL_DESCRIPTION = {
        "AudioTrack": track("audio", "an"),
        "MidiTrack": track("midi", "a"),
        "ClipSlotList": clip_slot_list,
        "ArrangerAutomation": arranger,
}
