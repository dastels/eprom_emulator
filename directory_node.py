import os

class DirectoryNode:

    def __init__(self, on, below=None, named=None):
        self.display = on
        self.parent = below
        self.name = named
        self.files = []
        self.top_offset = 0
        self.old_top_offset = -1
        self.selected_offset = 0
        self.old_selected_offset = -1


    def cleanup(self):
        self.display = None
        self.parent = None
        self.name = None
        self.files = None
        return self

    def is_dir(self, path):
        if path[-2:] == "..":
            return False
        try:
            os.listdir(path)
            return True
        except OSError:
            return False


    def sanitize(self, name):
        if name[-1] == "/":
            return name[:-1]
        else:
            return name
        
            
    def path(self):
        if self.parent:
            return self.parent.path() + os.sep + self.sanitize(self.name)
        else:
            return self.sanitize(self.name)
    

    def make_path(self, filename):
        return self.path() + os.sep + filename

    
    def selected_filename(self):
        self.get_files()
        return self.files[self.selected_offset]

    
    def selected_filepath(self):
        return self.make_path(self.selected_filename())

    
    def number_of_files(self):
        self.get_files()
        return len(self.files)


    def get_files(self):
        if len(self.files) == 0:
            self.files = os.listdir(self.path())
            self.files.sort()
            if self.parent:
                self.files.insert(0, "..")
            for index, name in enumerate(self.files, start=1):
                if self.is_dir(self.make_path(name)):
                    self.files[index] = name + "/"
            
                
    def update_display(self):
        if self.top_offset != self.old_top_offset:
            self.get_files()
            self.display.fill(0)
            for i in range(self.top_offset, min(self.top_offset + 4, self.number_of_files())):
                self.display.text(self.files[i], 10, (i - self.top_offset) * 8)
            self.display.show()
            self.old_top_offset = self.top_offset


    def update_selection(self):
        if self.selected_offset != self.old_selected_offset:
            if self.old_selected_offset > -1:
                self.display.text(">", 0, (self.old_selected_offset - self.top_offset) * 8, 0)
            self.display.text(">", 0, (self.selected_offset - self.top_offset) * 8, 1)
            self.display.show()
            self.old_selected_offset = self.selected_offset


    def update(self):
        self.old_selected_offset = -1
        self.old_top_offset = -1
        self.update_display()
        self.update_selection()
        

    def is_directory_name(self, filename):
        return filename[-1] == '/'


    def down(self):
        if self.selected_offset < self.number_of_files() - 1:
            self.selected_offset += 1
            if self.selected_offset == self.top_offset + 4:
                self.top_offset += 1
                self.update_display()
        self.update_selection()


    def up(self):
        if self.selected_offset > 0:
            self.selected_offset -= 1
            if self.selected_offset < self.top_offset:
                self.top_offset -= 1
                self.update_display()
        self.update_selection()


    def click(self):
        if self.selected_filename() == "..":
            if self.parent:
                p = self.parent
                p.update()
                self.cleanup()
                return p
        elif self.is_directory_name(self.selected_filename()):
            new_node = DirectoryNode(self.display, self, self.selected_filename())
            new_node.update()
            return new_node
        return self
