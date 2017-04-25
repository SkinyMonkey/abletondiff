from pygit2 import Repository

from lxml import etree
from pprint import pprint
import re

from ableton import ableton_operations

ADDITION = True
SUPPRESSION = False

OPERATION_TYPE = {
        "ADDITION": "added",
        "SUPPRESSION": "removed",
        "MODIFICATION": "modified"
}

TARGET_NAME = {}

OPEN_TAG = "<.*>"

def line_removed(line):
    return line.new_lineno == -1

def line_added(line):
    return line.old_lineno == -1

def target_name(target_tag):
    return TARGET_NAME[target_tag] if TARGET_NAME.get(target_tag) else target_tag

# TODO : rewrite, cleanly
def display_changed_attributes(chunk_tag, old_chunk, new_chunk):
    for attribute_name, value in old_chunk["xml"].attrib.iteritems():
        if value != new_chunk["xml"].attrib[attribute_name]:
            if new_chunk.get("device_name"):
                print "In %s , %s: parameter %s, %s changed from %s to %s" %\
                    (new_chunk["track_name"], new_chunk["device_name"], chunk_tag, attribute_name, value, new_chunk["xml"].attrib[attribute_name])
            else:
                # FIXME : device, need a more precise context
                print "In %s : %s, %s changed from %s to %s" %\
                    (new_chunk["track_name"], chunk_tag, attribute_name, value, new_chunk["xml"].attrib[attribute_name])

def describe_operation(chunks, linenos):
    # description could be a hashmap with attributes, there is a lot of attributes to check

    for chunk in chunks:
        if chunk["xml"] is not None:
            chunk_tag = target_name(chunk["xml"].tag)

            if chunk["operation_type"] == "MODIFICATION" and chunk.get("replacing"):
                display_changed_attributes(chunk_tag, chunks[chunk["replacing"]], chunk)
                ableton_operations(chunk, chunks[chunk["replacing"]])
            elif chunk["operation_type"] != "MODIFICATION":
                print "%s was %s" % (chunk_tag, OPERATION_TYPE[chunk["operation_type"]])
                # get value too?

def get_chunk_content(chunk):
    return "".join([ line.content for line in chunk["lines"] ])

def label_modifications(chunks, recursion = False):
    """
    Rename a chunk operation to MODIFICATION if needed
    """
    index = 0
    while index < len(chunks):
        subindex = index + 1

        while subindex < len(chunks):
            if  chunks[subindex]["xml"] is not None \
            and chunks[index]["xml"] is not None \
            and chunks[subindex]["xml"].tag == chunks[index]["xml"].tag\
            and chunks[index]["operation_type"] != "MODIFICATION"\
            and chunks[subindex]["operation_type"] != "MODIFICATION":

                 chunks[index]["replaced_by"] = subindex
                 chunks[subindex]["replacing"] = index

                 chunks[index]["operation_type"] = "MODIFICATION"
                 chunks[subindex]["operation_type"] = "MODIFICATION"
            subindex += 1

        index += 1
    return chunks

# print chunk["xml"].tag
def eval_operations(chunks):
    res = []
    for chunk in chunks:
        chunk_content = get_chunk_content(chunk)
        try:
            chunk["xml"] = etree.fromstring(chunk_content)
            res.append(chunk)
        except Exception as e:
            # use the lines instead of the all chunk
            for line in chunk["lines"]:
                try:
                    new_chunk = create_chunk([line], ADDITION if chunk["operation_type"]  == "ADDITION" else SUPPRESSION)
                    new_chunk["xml"] = etree.fromstring(line.content)
                    res.append(new_chunk)
                except Exception as e:
                    pass

            # FIXME : remove real broken one
    return res


def begin_lineno(chunk):
    return chunk[0].old_lineno if chunk[0].new_lineno == -1 else chunk[0].new_lineno

def end_lineno(chunk):
    return chunk[-1].old_lineno if chunk[-1].new_lineno == -1 else chunk[-1].new_lineno

def create_chunk(lines, operation_type):
    return { "operation_type" : "ADDITION" if operation_type == ADDITION else "SUPPRESSION",
             "lines" : lines,
             "begin_lineno" : begin_lineno(lines),
             "end_lineno" : end_lineno(lines)}

def bind_objects(patches):
    """
    Group lines by operations into chunks
    """
    operation = SUPPRESSION
    line_operation = SUPPRESSION
    operation_chunks = []

    addition_buffer = []
    suppression_buffer = []

#    operation = line_added(hunks[0].lines[0]) # TODO : get the first line where line.new_lineno != line.old_lineno

    index = 0

    for patch in patches:
        for hunk in patch.hunks:
            for line in hunk.lines:
                if line_added(line) or line_removed(line):
                    line_operation = line_added(line)

                    # when operation type change, so is the buffer
                    if line_operation != operation:
                        if operation == ADDITION and len(addition_buffer) > 0:
                            operation_chunks.append(create_chunk(addition_buffer, ADDITION))
                            addition_buffer = []
                        elif operation == SUPPRESSION and len(suppression_buffer) > 0:
                            operation_chunks.append(create_chunk(suppression_buffer, SUPPRESSION))
                            suppression_buffer = []

                        operation = not operation
 
                    if line_operation == ADDITION:
                        addition_buffer.append(line)
                    else:
                        suppression_buffer.append(line)

            # create a new chunk when the chunk is done and flush the buffers
            if len(addition_buffer) > 0:
                operation_chunks.append(create_chunk(addition_buffer, ADDITION))
                addition_buffer = []
            elif len(suppression_buffer) > 0:
                operation_chunks.append(create_chunk(suppression_buffer, SUPPRESSION))
                suppression_buffer = []

            index += 1

    return operation_chunks

def print_chunk_tags(chunks):
    for chunk in chunks:
        if chunk["xml"] is not None:
            print chunk["xml"].tag

def get_track(chunk, track_linenos):
    for track_type, tracks in track_linenos.iteritems():
        for track in tracks:
            if chunk["begin_lineno"] >= track["begin"]\
             and chunk["end_lineno"] <= track["end"]:
                return track

    pprint(chunk)
    print(get_chunk_content(chunk))
    raise Exception("could not determine the track name")

def get_device(chunk, track, subtype):
    for device_type, devices in track[subtype].iteritems():
        for device in devices:
            if chunk["begin_lineno"] >= device["begin"]\
            and chunk["end_lineno"] <= device["end"]:
                return (device, device_type)
    return (None, None)

def name_chunk_parent(chunks, linenos):
    for chunk in chunks:
        track = get_track(chunk, linenos)
        chunk["track_name"] = track["name"]

        (device, device_type) = get_device(chunk, track, "Devices")
        if device is not None:
            chunk["device_type"] = "Devices"
            chunk["device_name"] = device["name"]
        
        if chunk.get("device_type") is None:
            (device, device_type) = get_device(chunk, track, "DeviceChain")
            if device is not None:
                chunk["device_type"] = "DeviceChain"
                chunk["device_name"] = device["name"]

    return chunks


def git_analysis(repository_name, linenos):
    repo = Repository(repository_name)
    commit1 = None # repo.get("d04b7a21c4eabe7058d2649ef6d2d59de70b5352")
    commit2 = None # repo.get("f25108a7c1d96317d2026f4f19d2a6fe49283151")
    d = repo.diff(commit1, commit2)

    # FIXME : how to reference and older commit?
    
    patches = [p for p in d]

    if len(patches) == 0:
        print "No modification applied"
        exit(-1)

    chunks = bind_objects(patches)
    chunks = eval_operations(chunks)
    chunks = label_modifications(chunks)
    chunks = name_chunk_parent(chunks, linenos)

    # print_chunk_tags(chunks)
    
    describe_operation(chunks, linenos)
