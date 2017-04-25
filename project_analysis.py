import gzip
from lxml import etree

from pprint import pprint

def get_name(content):
    # res = content.xpath(".//Name/EffectiveName")
    res = content.find(".//Name/EffectiveName")

    if res is not None:
        return res.attrib["Value"]
    return res

# FIXME : is there a better way to do this?
#         maybe we can put this into the compute_elements_linenos loop
#         what about the node that have no parent's parent?

# FIXME : maybe a better way to do this is to iterate over the all project
#         and add the end line to each node
def find_end(linenos):
    for element, value in linenos.iteritems():
        for entry in value:
            if entry["end"] == 0:

                parent = entry["node"].getparent()
                parent_next = parent.getnext()

                while parent is not None and parent_next is None:
                    parent = parent.getparent()
                    parent_next = parent.getnext()

                if parent_next is not None:
                    entry["end"] = parent_next.sourceline
                else:
                    raise Exception("could not find proper end line")
    return linenos

def compute_elements_linenos(tree, watched, callback = None):
    greedy = len(watched) == 0
    linenos = { w : [] for w in watched }
    flags = { w : False for w in watched }

    for content in tree:
        for k, flag in flags.iteritems():
            if flag == True:
                linenos[k][-1]["end"] = content.sourceline - 2
                flags[k] = False
                break

        if greedy or content.tag in watched:
            if greedy and linenos.get(content.tag) is None:
                linenos[content.tag] = []

            name = get_name(content)

            linenos[content.tag].append({ "begin": content.sourceline,
                                          "end": 0,
                                          "name" : name if name is not None else content.tag,
                                          "node": content })
            flags[content.tag] = True

            if callback is not None:
                callback(content, linenos[content.tag][-1])
    
    return find_end(linenos)

def attach_devices_linenos(tree, lineno_entry):
    """
    Attach Devices and DeviceChain begin and end line nos
    to each Track.
    That way if a change is detected in a Track, we can proceed to checks on device and devicechain too
    """

    # NOTE : put in tracks : that way when you detect an element as being part of a track
    #        you can begin detecting if it's part of devices or devicechain of that same track

    devices = tree.xpath(".//Devices")[0]
    device_elements = []

    lineno_entry['Devices'] = compute_elements_linenos(devices, device_elements)

    devices = tree.xpath(".//DeviceChain")[0]
    device_elements = []
    
    lineno_entry['DeviceChain'] = compute_elements_linenos(devices, device_elements)
 

def project_analysis(file_content):
    # we want to know in what kind of element the change happened
    # for that we have to find it into the tree
    # that way with the xpath we can have the path
    # and detail of the change?
    # tree.getpath

    # to find it into the tree we'll use the lineno of the chunks
    # and the lineno of the tracks

    linenos = {}

    # project analysis

    ### Tracks, MasterTrack, PreHearTrack begin and end line nos
    project = etree.fromstring(file_content)

    liveset = project.xpath("//LiveSet")[0]
    main_elements = ["MasterTrack", "PreHearTrack"] # Tracks

    linenos = compute_elements_linenos(liveset, main_elements)

    ### Track begin and end line nos
    tracks = project.xpath("//Tracks")[0]
    track_elements = ["AudioTrack", "MidiTrack", "GroupTrack", "ReturnTrack"]

    linenos.update(compute_elements_linenos(tracks, track_elements, attach_devices_linenos))

    # pprint(linenos)
   
    return linenos
