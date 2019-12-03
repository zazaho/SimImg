#!/usr/bin/python3
''' Project to display similar images from an image catalog '''
import sys
from tkinter import PhotoImage
# import sys
import tkinter as tk
import config.configuration as CONF
import controller.controller as CTRL

class simim_app(tk.Tk):
    ''' Main window for sorting and managing pictures'''

    def __init__(self, arguments=None, *args, **kwargs):
        # do what any TK app does
        super().__init__()

        # Do nothing much but creating the objects
        # it is those objects that will implement the
        # working of the App.

        # Object that hold configuration database
        self.Cfg = CONF.Configuration(Arguments=arguments)

        # build the basic layout of the app
        # make menubar
        self.ModulePane = tk.Frame()
        self.ThumbPane = tk.Frame()
        self.ModulePane.pack(side=tk.LEFT, fill='y')
        self.ThumbPane.pack(side=tk.RIGHT, fill='y')
        # make statusbar

        # The object responsible for dealing with the data
        # and the display of those data
        self.Ctrl = CTRL.Controller(self)

        self.Ctrl.createInitialView()


# Main routine, shim, do all work inside simim_app
if __name__ == "__main__":
    # interpret the commandline arguments or lack thereof
    pathargs = sys.argv[1:] if len(sys.argv) > 1 else ['./']

    app = simim_app(arguments=pathargs)
    app.title("SIMilar IMaGe finder")
    app.tk.call('wm', 'iconphoto', app._w, PhotoImage(file='simimg.png'))
    app.geometry("+0+0")
    app.mainloop()
