class Cursor(object):
    """
    level_index = current level in the element_path
    element = targeted element in the existing project
    element_path = split path of the element
    chunk = chunk found in the new version
    old_chunk = chunk found in the old version
    """
    def __init__(self, level_index, element, element_path, chunk, old_chunk):
        super(Cursor, self).__init__()
        self.level_index = level_index
        self.element = element
        self.element_path = element_path
        self.chunk = chunk
        self.old_chunk = old_chunk
        self.indent = 0

    def indent_print(toprint):
        print "%s%s" (self.indent * "\t", toprint)
        self.indent += 1
