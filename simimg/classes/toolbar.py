""" Modules that defines a oolbar with action items"""
import os
from tkinter import ttk

import simimg.classes.tooltip as TT
import simimg.dialogs.infowindow as IW
import simimg.utils.pillowplus as PP


class Toolbar(ttk.Frame):
    " A toolbar frame that holds the action buttons"

    def __init__(self, parent, Controller=None):
        super().__init__(parent)

        self.Ctrl = Controller
        iconpath = self.Ctrl.Cfg.get("iconpath")
        self.addImg = PP.photoImageOpen(os.path.join(iconpath, "add.png"))
        self.deleteImg = PP.photoImageOpen(os.path.join(iconpath, "delete.png"))
        self.moveImg = PP.photoImageOpen(os.path.join(iconpath, "move.png"))
        self.exitImg = PP.photoImageOpen(os.path.join(iconpath, "exit.png"))
        self.hideImg = PP.photoImageOpen(os.path.join(iconpath, "hide.png"))
        self.infoImg = PP.photoImageOpen(os.path.join(iconpath, "info.png"))
        self.openImg = PP.photoImageOpen(os.path.join(iconpath, "open.png"))
        self.playImg = PP.photoImageOpen(os.path.join(iconpath, "play.png"))
        self.refreshImg = PP.photoImageOpen(os.path.join(iconpath, "refresh.png"))
        self.settingsImg = PP.photoImageOpen(os.path.join(iconpath, "settings.png"))
        self.uncheckImg = PP.photoImageOpen(os.path.join(iconpath, "uncheck.png"))

        self.exitButton = ttk.Button(self, image=self.exitImg, style="Picture.TButton", command=self.Ctrl.exitProgram)
        self.settingsButton = ttk.Button(self, image=self.settingsImg, style="Picture.TButton", command=self.Ctrl.configureProgram)
        #
        self.infoButton = ttk.Button(self, image=self.infoImg, style="Picture.TButton", command=IW.showInfoDialog)

        self.openButton = ttk.Button(self, image=self.openImg, style="Picture.TButton", command=self._openFolder)
        self.addButton = ttk.Button(self, image=self.addImg, style="Picture.TButton", command=self._addFolder)
        #
        self.refreshButton = ttk.Button(self, image=self.refreshImg, style="Picture.TButton", command=self.Ctrl.resetThumbnails)

        self.uncheckButton = ttk.Button(self, image=self.uncheckImg, style="Picture.TButton", command=self.Ctrl.toggleSelectAllThumbnails)
        self.deleteButton = ttk.Button(self, image=self.deleteImg, style="Picture.TButton", command=self.Ctrl.deleteSelected)
        self.moveButton = ttk.Button(self, image=self.moveImg, style="Picture.TButton", command=self.Ctrl.moveSelected)
        self.hideButton = ttk.Button(self, image=self.hideImg, style="Picture.TButton", command=self.Ctrl.hideSelected)
        self.playButton = ttk.Button(self, image=self.playImg, style="Picture.TButton", command=self.Ctrl.viewSelected)

        self.exitButton.grid(column=0, row=0)
        self.settingsButton.grid(column=1, row=0)
        #
        self.infoButton.grid(column=3, row=0)

        self.openButton.grid(column=0, row=1)
        self.addButton.grid(column=1, row=1)
        #
        self.hideButton.grid(column=2, row=1)
        self.refreshButton.grid(column=3, row=1)

        self.deleteButton.grid(column=0, row=2)
        self.moveButton.grid(column=1, row=2)
        self.uncheckButton.grid(column=2, row=2)
        self.playButton.grid(column=3, row=2)

        TT.Tooltip(self.addButton, text="Add folder of images")
        TT.Tooltip(self.deleteButton, text="Delete Selected Images")
        TT.Tooltip(self.moveButton, text="Move Selected Images")
        TT.Tooltip(self.exitButton, text="Quit")
        TT.Tooltip(self.hideButton, text="Hide Selected Images")
        TT.Tooltip(self.infoButton, text="Quick instructions")
        TT.Tooltip(self.openButton, text="Open folder of images")
        TT.Tooltip(self.playButton, text="View Selected Images")
        TT.Tooltip(self.refreshButton, text="Start fresh with all images shown")
        TT.Tooltip(self.settingsButton, text="Settings")
        TT.Tooltip(self.uncheckButton, text="Select/Unselect all images")

    def _openFolder(self, *args):
        self.Ctrl.addOrOpenFolder(action="open")

    def _addFolder(self, *args):
        self.Ctrl.addOrOpenFolder(action="add")
