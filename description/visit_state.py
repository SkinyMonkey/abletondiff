class VisitState(object):
    def __init__(self, element, element_path, chunk, old_chunk, level_map):
        """
        element = element found in current state of the project
        element_path = split xpath of the element

        chunk = xml chunk from the current state of the project
        old_chunk = xml chunk from the previous state of the project

        level_index = index of the current xpath depth
        indent = indentation, used for display
        """
        super(VisitState, self).__init__()

        self.element = element
        self.element_path = element_path

        self.chunk = chunk
        self.old_chunk = old_chunk
        
        self.indent = -1
        self.level_map = level_map

    def get_next_element(self, element_name):
        """
        Get the next element with the given $element_name
        """
        return self.element_path[self.element_path.index(element_name) + 1]
    
    def get_attribute(self, name, element = None):
        """
        Retrieve the value of an attribute in self.element
        """
        if element is None:
           element = self.element
        return element.iterchildren(name).next().attrib['Value']

    # TODO : return a list of change tuples?
    def compute_change(self):
        """
        Returns the difference between two Attribute value
        """
        for attr, value in self.chunk["xml"].attrib.iteritems():
            for old_attr, old_value in self.old_chunk["xml"].attrib.iteritems():
                if old_value != value:
                    return (old_value, value)
    
        raise Exception("No difference found between two chunks?")
    
    def element_left(self, level_index):
        """
        Check if their is an element left in xpath
        """
        return len(self.element_path[level_index + 1:]) > 0
 
    def get_next_level(self, level_index):
        """
        Get the next level in the xpath that has a callback in self.level_map
        """
        tail_element_path = self.element_path[level_index:]
        for level in tail_element_path:
            try:
                bracket_index = level.index('[')
                level_name = level[:bracket_index]
            except:
                level_name = level
            
            if level_name in self.level_map:
                return level

    def call_level_map(self, level_index, tag):
        self.indent += 1
        try:
            bracket_index = tag.index('[')
            tag_name = tag[:bracket_index]
        except:
            tag_name = tag
        next_level_index = self.level_map[tag_name](level_index, self)
        self.indent -= 1
        return next_level_index
    
    def call_next_tag(self, level_index):
        """
        Call the next level in the xpath has a callback in $level_map
        """
        next_tag = self.get_next_level(level_index + 1)
    
        if next_tag is not None:
            # FIXME : bracket removal behaviour?
            level_index = self.element_path.index(next_tag)

            return self.call_level_map(level_index, next_tag)

        raise Exception("No handler for %s" % self.element_path[-1])

    def display(self, message):
        print "%s%s" % ("\t" * self.indent, message)

    def current_tag(self, level_index):
        return self.element_path[level_index]
