import os

class DirectoryNode:
    """Display and navigate the SD card contents"""

    def __init__(self, on, below=None, named=None):
        """Initialize a new instance.
           :param adafruit_ssd1306.SSD1306 on: the OLED instance to display on
           :param DirectoryNode below: optional parent directory node
           :param string named: the optional name of the new node
        """
        self.display = on
        self.parent = below
        self.name = named
        self.files = []
        self.top_offset = 0
        self.old_top_offset = -1
        self.selected_offset = 0
        self.old_selected_offset = -1


    def cleanup(self):
        """Dereference things for speedy gc."""
        self.display = None
        self.parent = None
        self.name = None
        self.files = None
        return self

    def is_dir(self, path):
        """Determine whether a path identifies a machine code bin file.
           :param string path: path of the file to check
        """
        if path[-2:] == "..":
            return False
        try:
            os.listdir(path)
            return True
        except OSError:
            return False


    def sanitize(self, name):
        """Nondestructively strip off a trailing slash, if any, and return the result.
           :param string name: the filename
        """
        if name[-1] == "/":
            return name[:-1]
        else:
            return name
        

    @property
    def path(self):
        """Return the result of recursively follow the parent links, building a full 
           path to this directory."""
        if self.parent:
            return self.parent.path + os.sep + self.sanitize(self.name)
        else:
            return self.sanitize(self.name)
    

    def make_path(self, filename):
        """Return a full path to the specified file in this directory.
           :param string filename: the name of the file in this directory
         """
        return self.path + os.sep + filename


    @property
    def selected_filename(self):
        """The name of the currently selected file in this directory."""
        self.get_files()
        return self.files[self.selected_offset]


    @property
    def selected_filepath(self):
        """The full path of the currently selected file in this directory."""
        return self.make_path(self.selected_filename)


    @property
    def number_of_files(self):
        """The number of files in this directory, including the ".." for the parent 
            directory if this isn't the top directory on the SD card."""
        self.get_files()
        return len(self.files)


    def get_files(self):
        """Return a list of the files in this directory.
           If this is not the top directory on the SD card, a ".." entry is the first element.
           Any directories have a slash appended to their name."""
        if len(self.files) == 0:
            self.files = os.listdir(self.path)
            self.files.sort()
            if self.parent:
                self.files.insert(0, "..")
            for index, name in enumerate(self.files, start=1):
                if self.is_dir(self.make_path(name)):
                    self.files[index] = name + "/"
            
                
    def update_display(self):
        """Update the displayed list of files if required."""
        if self.top_offset != self.old_top_offset:
            self.get_files()
            self.display.fill(0)
            for i in range(self.top_offset, min(self.top_offset + 4, self.number_of_files)):
                self.display.text(self.files[i], 10, (i - self.top_offset) * 8)
            self.display.show()
            self.old_top_offset = self.top_offset


    def update_selection(self):
        """Update the selected file lighlight if required."""
        if self.selected_offset != self.old_selected_offset:
            if self.old_selected_offset > -1:
                self.display.text(">", 0, (self.old_selected_offset - self.top_offset) * 8, 0)
            self.display.text(">", 0, (self.selected_offset - self.top_offset) * 8, 1)
            self.display.show()
            self.old_selected_offset = self.selected_offset


    def force_update(self):
        """Force an update of the file list and selected file highlight."""
        self.old_selected_offset = -1
        self.old_top_offset = -1
        self.update_display()
        self.update_selection()
        

    def is_directory_name(self, filename):
        """Is a filename the name of a directory.
           :param string filename: the name of the file
        """
        return filename[-1] == '/'


    def down(self):
        """Move down in the file list if possible, adjusting the selected file indicator 
           and scrolling the display as required."""
        if self.selected_offset < self.number_of_files - 1:
            self.selected_offset += 1
            if self.selected_offset == self.top_offset + 4:
                self.top_offset += 1
                self.update_display()
        self.update_selection()


    def up(self):
        """Move up in the file list if possible, adjusting the selected file indicator 
           and scrolling the display as required."""
        if self.selected_offset > 0:
            self.selected_offset -= 1
            if self.selected_offset < self.top_offset:
                self.top_offset -= 1
                self.update_display()
        self.update_selection()


    def click(self):
        """Handle a selection and return the new current directory.
           If the selected file is the parent, i.e. "..", return to the parent directory.
           If the selected file is a directory, go into it."""
        if self.selected_filename == "..":
            if self.parent:
                p = self.parent
                p.force_update()
                self.cleanup()
                return p
        elif self.is_directory_name(self.selected_filename):
            new_node = DirectoryNode(self.display, self, self.selected_filename)
            new_node.force_update()
            return new_node
        return self
