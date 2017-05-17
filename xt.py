from lxml import etree
import xtdiff

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
            return get_child(element, name)
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

def diff_events(before_root, after_root, parent, parent_index, type_index):
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

def diff(before, after, name_cb, before_id_cb = get_id, after_id_cb = get_id):
    before_names = map(name_cb, before)
    after_names = map(name_cb, after)
    
    before_ids = map(before_id_cb, before)
    after_ids = map(after_id_cb, after)

    id_diff = diff_index(before_ids, after_ids)

    diff_description(id_diff, before_names, "removed")

    id_diff = diff_index(after_ids, before_ids)

    diff_description(id_diff, after_names, "added")

    dbefore = dict(zip(before_ids, before)) 
    dafter = dict(zip(after_ids, after)) 

    return (dbefore, dafter, after_names)

def diff_mixer(before_root, after_root, track):
    track_mixer = track.iterdescendants("Mixer").next()

    diff_events(before_root, after_root, track_mixer, -5, -4)

# FIXME : use ids to be sure we are getting data from the same right devices
#         in after and before
#	  when doing diff of params
def diff_devices(before_root, after_root, track_before, track_after):
    getchildren = lambda d: d.getchildren()
    concat = lambda a, b : a + b

    before_devices = reduce(concat, map(getchildren, track_before.iterdescendants("Devices")))
    after_devices = reduce(concat, map(getchildren, track_after.iterdescendants("Devices")))

    (ddevices_before, ddevices_after, after_device_names) =\
         diff(before_devices, after_devices, get_child_named("Name"))

    for id_, device in ddevices_after.iteritems():
        if ddevices_before.get(id_) is not None:
            # FIXME : exception on AUPluginDevice and VSTPluginDevice
            # treat them
            if device.tag == "AuPluginDevice":
                continue

            diff_events(before_root, after_root, device, -5, -4)

def diff_slots():
    pass

def browse(before, after):
    before_root = before.getroottree()
    after_root = after.getroottree()

    before_liveset = get_child(before_root.iter().next(), "LiveSet")
    after_liveset = get_child(after_root.iter().next(), "LiveSet")

    before_tracks = get_child(before_liveset, "Tracks").getchildren()
    after_tracks = get_child(after_liveset, "Tracks").getchildren()

    (dtracks_before, dtracks_after, after_track_names) =\
                 diff(before_tracks, after_tracks, get_name)

    # Detect change inside track

    for id_, track_after in dtracks_after.iteritems():
        track_before = dtracks_before.get(id_)
        if track_before is not None:
            print "In a track named %s" %\
                    after_track_names[dtracks_after.keys().index(id_)]

            diff_mixer(before_root, after_root, track_after)

            diff_devices(before_root, after_root, track_before, track_after)

            # check slots
	    # can't use diff : no Id
	    # use xpath to check?
            # or use index in clipslotlist
            # before_slots = track_before.iterdescendants("ClipSlot")
            # after_slots = track_after.iterdescendants("ClipSlot")
	    # iterdescendants("Name") -> if created there is a name, even empty

            # check clips in arrangement view
	    # "ClipTimeable"
	    # "Events"

            # get cliptimeable
            # get all events

            try:
                cliptimeable_before = get_child(track_before, "ClipTimeable")
                cliptimeable_after = get_child(track_after, "ClipTimeable")

                before_argmnts = list(cliptimeable_before.iterdescendants("ArrangerAutomation"))
                after_argmnts = list(cliptimeable_after.iterdescendants("ArrangerAutomation"))

#                import pdb; pdb.set_trace()
                (dargmnts_before, dargmnts_after, after_argmnt_names) =\
                     diff(before_argmnts, after_argmnts, get_child_named("Name"), generate_id('b'), generate_id('a'))

                for id_, argmnt in dargmnts_after.iteritems():
                    if dargmnts_before.get(id_) is not None:
                        diff_events(before_root, after_root, argmnt, -4, -1)

            except Exception as e:
#                print e
                pass

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

