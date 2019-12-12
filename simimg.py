#!/usr/bin/python3
''' Project to display similar images from an image catalog '''
import os
from tkinter import PhotoImage
# import sys
import tkinter as tk
import classes.configuration as CONF
import classes.controller as CTRL
import classes.scrollframe as SF

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
            'SIMIMG.png'
        )
        self.title("SIMilar IMaGe finder")
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=appIcon))
        self.geometry(self.Cfg.get('findergeometry'))

        self.Statusbar = tk.Label(self,text="...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.Statusbar.pack(side=tk.BOTTOM, fill='x')
        self.ModulePane = tk.Frame(self)
        self.ModulePane.pack(side=tk.LEFT, fill='y')
        self.ThumbPane = SF.ScrollFrame(self)
        self.ThumbPane.pack(side=tk.RIGHT, fill="both", expand=True)

        #self.update_idletasks()
        # The object responsible for dealing with the data
        # and the display of those data
        self.Ctrl = CTRL.Controller(self)
        #self.Ctrl.createViewWithoutConditions()

# Main routine, shim, do all work inside simim_app
if __name__ == "__main__":
    scriptpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    app = simim_app(ScriptPath=scriptpath)
    app.mainloop()
