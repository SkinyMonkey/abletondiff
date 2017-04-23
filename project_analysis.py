import gzip
from lxml import etree

from pprint import pprint

def get_name(content):
    # res = content.xpath(".//Name/EffectiveName")
    res = content.find(".//Name/EffectiveName")

    if res is not None:
        return res.attrib["Value"]
    return res

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

            linenos[content.tag].append({ "begin": content.sourceline , "end": 0, "name" : get_name(content)})
            flags[content.tag] = True

            if callback is not None:
                callback(content, linenos[content.tag][-1])

# FIXME : todo, outside of here if possible
#    pprint(flags)
#    for flag, value in flags.iteritems():
#        if value == True:
#            linenos[flag][-1]["end"] = VALUE_FROM_MAIN_ELEMENTS_LINENO

    return linenos

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
 

def project_analysis(project_name):
    # we want to know in what kind of element the change happened
    # for that we have to find it into the tree
    # that way with the xpath we can have the path
    # and detail of the change?
    # tree.getpath

    # to find it into the tree we'll use the lineno of the chunks
    # and the lineno of the tracks

    linenos = {}

    # project analysis
    with gzip.open(project_name, 'rb') as f:
        file_content = f.read()

        ### Tracks, MasterTrack, PreHearTrack begin and end line nos
        project = etree.fromstring(file_content)

        liveset = project.xpath("//LiveSet")[0]
        main_elements = ["MasterTrack", "PreHearTrack"] # Tracks

        linenos = compute_elements_linenos(liveset, main_elements)

        ### Track begin and end line nos
        tracks = project.xpath("//Tracks")[0]
        track_elements = ["AudioTrack", "MidiTrack", "GroupTrack", "ReturnTrack"]

        linenos.update(compute_elements_linenos(tracks, track_elements, attach_devices_linenos))

#        pprint(linenos)
   
        return linenos
