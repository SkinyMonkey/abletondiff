def track(track_type, prefix):
    def wrapper(chunk, action):
        track_name = chunk["xml"].iterchildren("Name").next()
        effective_name = track_name.iterchildren("EffectiveName").next().attrib["Value"]
        print ("%s %s track called %s was %s" % (prefix, track_type, effective_name, action))
    return wrapper

HIGH_LEVEL_EXCEPTIONS = {
        "AudioTrack": track("audio", "An"),
        "MidiTrack": track("midi", "A")
}

def high_level_change(chunk):
    if chunk["xml"].tag in HIGH_LEVEL_EXCEPTIONS:
        if chunk["operation_type"] == "SUPPRESSION":
            HIGH_LEVEL_EXCEPTIONS[chunk["xml"].tag](chunk, "removed")
            return True
        if chunk["operation_type"] == "ADDITION":
            HIGH_LEVEL_EXCEPTIONS[chunk["xml"].tag](chunk, "added")
            return True
    return False
