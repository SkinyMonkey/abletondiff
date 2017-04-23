ADDITION = True
SUPPRESSION = False
MODIFICATION = "MODIFICATION"

action_translation = {
    ADDITION: "added",
    SUPPRESSION: "removed",
}

from pprint import pprint

def get_old_device(device, devices):
    for d in devices:
        if device.attrib["Id"] == d.attrib["Id"]:
            print device.tag
            return d

def which_devices(track, xml, old_xml, action):
    for device in xml:
        if device.tag in TAG_CALLBACKS:

            if action == MODIFICATION:
                old_device = get_old_device(device, old_xml);
            else:
                old_device = old_xml

            TAG_CALLBACKS[device.tag](track, device, old_device, action)

def devices(xml, old_xml):
    if len(old_xml.getchildren()) < len(xml.getchildren()):
        print "Devices were added"
        which_devices(xml, old_xml, ADDITION)
    elif len(old_xml.getchildren()) > len(xml.getchildren()):
        print "All devices were removed"
        which_devices(xml, old_xml, SUPPRESSION)
    elif len(old_xml.getchildren()) == len(xml.getchildren()):
        print "Devices were modified"
        which_devices(xml, old_xml, MODIFICATION)


def print_device_action(track, device, action):
    print "in %s : %s was %s" % (track, device.tag, action_translation[action])

def autofilter(track, device, old_device, action):
    print_device_action(track, device, action)


TAG_CALLBACKS = {
    "Devices": devices,
    "AutoFilter": autofilter
}

def ableton_operations(chunk, old_chunk):
    if chunk["xml"].tag in TAG_CALLBACKS:
        TAG_CALLBACKS[chunk["xml"].tag](chunk['name'], chunk["xml"], old_chunk["xml"])
