from lxml import etree
from functools import partial

def db(value):
    return value

def percent(value):
    return value

def frequency(value):
    return value

def panning(value):
    return "%sL" % (value * 50) if value > 0 else "%sR" % (value * 50)

VALUE_TRANSLATE = {
    "Volume": db,
    "Pan": panning,
}

def get_child(element, name):
#    try:
        return element.iterdescendants(name).next()
#    except:
#        return element.tag

def get_child_named(name):
    def wrapper(element):
        try:
            return get_value(get_child(element, name))
        except:
            return element.tag
    return wrapper

def get_attribute(element, name):
    return element.attrib[name]

def get_value(element):
    return get_attribute(element, "Value")

def get_name(element):
    return get_attribute(get_child(get_child(element, "Name"), "EffectiveName"), "Value")

def get_id(element):
    return get_attribute(element, "Id")

def get_time(element):
    return get_attribute(element, "Time")

IDS = {}

def generate_id(key):
    def wrapper(element):
        if not IDS.get(key):
            IDS[key] = 0
        IDS[key] += 1
        return IDS[key]
    return wrapper

def diff_index(first, second):
    second = set(second)
    index = 0
    res = []
    while index < len(first):
        if first[index] not in second:
            res.append(index)
        index += 1
    return res

def diff_description(diff, names, action, prefix = ""):
    for index in diff:
        print "%s%s was added" % (prefix, names[index])

def diff_events_generator(parent_index, type_index, prefix = ""):
    def wrapper(before_root, after_root, parent):
        for param_events in parent.iterdescendants("Events"):
            for param_event in param_events:
                param_event_path = after_root.getpath(param_event)
                before_event = before_root.xpath(param_event_path)
                        
                if (len(before_event)) > 0:
                    after_value = get_value(param_event)
                    before_value = get_value(before_event[0])
                    if before_value != after_value:
                        print "\t\t%s's %s changed from %s to %s" %\
                            (param_event_path.split('/')[parent_index]
                            ,param_event_path.split('/')[type_index]
                            ,before_value
                            ,after_value)
                else:
                    # FIXME: get device name or default to path name
                    # add value, add time
                    print "\t\t%s's %s event was added in automation" %\
                            (param_event_path.split('/')[parent_index]
                            ,param_event_path.split('/')[type_index])
    return wrapper

#       add message to display to contextualize action
#       add details about what was added or removed (AudioClip, MidiClip etc)
def diff_generator(name_cb, before_id_cb = get_id, after_id_cb = get_id, prefix = "", message = ""):
    def wrapper(before, after, element_name = None):
        before_names = map(name_cb, before)
        after_names = map(name_cb, after)
    
        before_ids = map(before_id_cb, before)
        after_ids = map(after_id_cb, after)
    
        id_diff = diff_index(before_ids, after_ids)
    
        diff_description(id_diff, before_names, "removed", prefix)
    
        id_diff = diff_index(after_ids, before_ids)
    
        diff_description(id_diff, after_names, "added", prefix)
    
        dbefore = dict(zip(before_ids, before)) 
        dafter = dict(zip(after_ids, after)) 
    
        return (dbefore, dafter, after_names)
    return wrapper

__diff_events_mixer = diff_events_generator(-5, -4)

def diff_mixer(before_root, after_root, track):
    print "In the mixer"

    track_mixer = track.iterdescendants("Mixer").next()

    __diff_events_mixer(before_root, after_root, track_mixer)

# FIXME : use ids to be sure we are getting data from the same right devices
#         in after and before
#	  when doing diff of params
__diff_devices = diff_generator(get_child_named("Name"), prefix="", message="")
__diff_devices_events = diff_events_generator(-5, -4)

def diff_devices(before_root, after_root, track_before, track_after):
    getchildren = partial(map, lambda d: d.getchildren())
    concat = lambda a : reduce(lambda c, d: c + d, a, [])
    #       partial(reduce, lambda a, b : a + b, partial=[])

    get = compose(concat, getchildren)

    before_devices = get(track_before.iterdescendants("Devices"))
    after_devices = get(track_after.iterdescendants("Devices"))

    (ddevices_before, ddevices_after, after_device_names) =\
         __diff_devices(before_devices, after_devices)

    for id_, device in ddevices_after.iteritems():
        if ddevices_before.get(id_) is not None:
            # FIXME : exception on AUPluginDevice and VSTPluginDevice
            # treat them
            if device.tag == "AuPluginDevice":
                continue

            __diff_devices_events(before_root, after_root, device)

def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

__diff_slots = diff_generator(get_child_named("Name"), get_time, get_time, "\t\t", "")
__diff_slots_events = diff_events_generator(-5, -4)

def diff_slots(before_root, after_root, track_before, track_after):
    has_clip = partial(filter, lambda x : len(x.getchildren()) > 0)
    getchildren = partial(map, lambda x : x.getchildren())
    concat = lambda a : reduce(lambda c, d: c + d, a, [])
    #       partial(reduce, lambda a, b : a + b, partial=[])

    get = compose(concat, getchildren, has_clip, list)

    clipslots_before = get(get_child(track_before, "ClipSlotList").iterdescendants("Value"))
    clipslots_after =  get(get_child(track_after, "ClipSlotList").iterdescendants("Value"))

    # FIXME : condition, we don't want it all the time
    print "\tIn the Live view"

    (dclipslots_before, dclipslots_after, after_clipslots_names) =\
        __diff_slots(clipslots_before, clipslots_after)

    for time, clipslot in dclipslots_after.iteritems():
        if dclipslots_before.get(time) is not None:
            pass
            # __diff_slots_events(before_root, after_root, device)

__diff_arrangement = diff_generator(get_child_named("Name"), generate_id('b'), generate_id('a'), "\t\t", "")
__diff_arrangement_events = diff_events_generator(-4, -1)

def diff_arrangement(before_root, after_root, track_before, track_after):
    try:
        cliptimeable_before = get_child(track_before, "ClipTimeable")
        cliptimeable_after = get_child(track_after, "ClipTimeable")

        getchildren = partial(map, lambda d: d.getchildren())
        concat = lambda a, b : a + b

        get = compose(reduce, concat, getchildren)

        after_argmnts = get(cliptimeable_after.iterdescendants("Events"))
        before_argmnts = get(cliptimeable_before.iterdescendants("Events"))

        # FIXME : condition, we don't want it all the time
        print "\tIn the Arrangement view"

        (dargmnts_before, dargmnts_after, after_argmnt_names) =\
             __diff_arrangement(before_argmnts, after_argmnts)

        for id_, argmnt in dargmnts_after.iteritems():
            if dargmnts_before.get(id_) is not None:
                diff_events(before_root, after_root, argmnt)

    except Exception as e:
        pass

__diff_tracks = diff_generator(get_name, prefix="\t\t")

# FIXME : instead of printing the values
#         store everything in dict and lists
#         have helper functions display them in order?

def browse(before, after):
    before_root = before.getroottree()
    after_root = after.getroottree()

    before_liveset = get_child(before_root.iter().next(), "LiveSet")
    after_liveset = get_child(after_root.iter().next(), "LiveSet")

    before_tracks = get_child(before_liveset, "Tracks").getchildren()
    after_tracks = get_child(after_liveset, "Tracks").getchildren()

    (dtracks_before, dtracks_after, after_track_names) =\
                 __diff_tracks(before_tracks, after_tracks)

    # Detect change inside track

    for id_, track_after in dtracks_after.iteritems():
        track_before = dtracks_before.get(id_)
        if track_before is not None:
            # FIXME : display should be conditionned
            # it's not because the track existed
            # and exist that it changed

            print "In a track named %s" %\
                    after_track_names[dtracks_after.keys().index(id_)]

            diff_mixer(before_root, after_root, track_after)

            diff_devices(before_root, after_root, track_before, track_after)

            diff_slots(before_root, after_root, track_before, track_after)

            diff_arrangement(before_root, after_root, track_before, track_after)

def main():
    with open('./tests/test Project/test') as current_state:
        current_state_content = current_state.read()

        with open('./tests/test Project/test.tmp') as previous_state:
            previous_state_content = previous_state.read()

            before = etree.fromstring(current_state_content)
            after = etree.fromstring(previous_state_content)

            browse(after, before)


if __name__ == '__main__':
    main()

