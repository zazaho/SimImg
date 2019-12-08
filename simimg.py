#!/usr/bin/python3
''' Project to display similar images from an image catalog '''
import sys
import os
from tkinter import PhotoImage
# import sys
import tkinter as tk
import classes.configuration as CONF
import classes.controller as CTRL
import classes.scrollframe as SF

class simim_app(tk.Tk):
    ''' Main window for sorting and managing pictures'''

    def __init__(self, arguments=None, ScriptPath=None, IconPath=None):
        # do what any TK app does
        super().__init__()

        # Do nothing much but creating the objects
        # it is those objects that will implement the
        # working of the App.

        # Object that hold configuration database
        self.Cfg = CONF.Configuration(Arguments=arguments, ScriptPath=ScriptPath, IconPath=IconPath)

        # build the basic layout of the app
        # make menubar
        self.Statusbar = tk.Label(self,text="...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.Statusbar.pack(side=tk.BOTTOM, fill='x')

        self.ModulePane = tk.Frame(self)
        self.ModulePane.pack(side=tk.LEFT, fill='y')
        self.ThumbPane = SF.ScrollFrame(self)
        #self.ThumbPane = tk.Frame()
        self.ThumbPane.pack(side=tk.RIGHT, fill="both", expand=True)


        # The object responsible for dealing with the data
        # and the display of those data
        self.Ctrl = CTRL.Controller(self)

        self.Ctrl.createInitialView()


# Main routine, shim, do all work inside simim_app
if __name__ == "__main__":
    # interpret the commandline arguments or lack thereof
    pathargs = sys.argv[1:] if len(sys.argv) > 1 else ['./']
    scriptpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    iconpath = os.path.join(scriptpath,'icons')
    appicon = os.path.join(iconpath,'simimg.png')

    app = simim_app(arguments=pathargs, ScriptPath=scriptpath, IconPath=iconpath)
    app.title("SIMilar IMaGe finder")
    app.tk.call('wm', 'iconphoto', app._w, PhotoImage(file=appicon))
    app.geometry("1200x800+0+0")
    app.mainloop()
