#!/usr/bin/python3
''' Project to display similar images from an image catalog '''
import os
from tkinter import PhotoImage
import tkinter as tk
import simimg.classes.configuration as CONF
import simimg.classes.controller as CTRL
import simimg.classes.scrollframe as SF

class simim_app(tk.Tk):
    ''' Main window for sorting and managing pictures'''

    def __init__(self, ScriptPath=None):
        # do what any TK app does
        super().__init__()

        # Do nothing much but creating the objects
        # it is those objects that will implement the
        # working of the App.

        # Object that hold configuration database
        self.Cfg = CONF.Configuration(ScriptPath=ScriptPath)

        appIcon = os.path.join(
            self.Cfg.get('iconpath'),
            'simimg.png'
        )
        self.title("Similar Image Finder")
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=appIcon))
        self.geometry(self.Cfg.get('findergeometry'))

        self.Statusbar = tk.Label(self,text="...", bd=1, relief="sunken", anchor="w")
        self.Statusbar.pack(side="bottom", fill='x')
        self.ModulePane = tk.Frame(self)
        self.ModulePane.pack(side="left", fill='y')
        self.ThumbPane = SF.ScrollFrame(self)
        self.ThumbPane.pack(side="right", fill="both", expand=True)

        # The object responsible for dealing with the data
        # and the display of those data
        self.Ctrl = CTRL.Controller(self)

def main():
    scriptpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    app = simim_app(ScriptPath=scriptpath)
    app.mainloop()

if __name__ == "__main__":
    main()
