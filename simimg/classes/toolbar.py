''' Modules that defines a oolbar with action items'''
import os
import tkinter as tk
import simimg.classes.tooltip as TT
import simimg.dialogs.infowindow as IW
import simimg.utils.pillowplus as PP

class Toolbar(tk.Frame):
    " A toolbar frame that holds the action buttons"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)
        self.config(bd=1, relief="raised")

        iconpath = Controller.Cfg.get('iconpath')
        self.addImg = PP.photoImageOpen(os.path.join(iconpath, "add.png"))
        self.deleteImg = PP.photoImageOpen(os.path.join(iconpath, "delete.png"))
        self.exitImg = PP.photoImageOpen(os.path.join(iconpath, "exit.png"))
        self.hideImg = PP.photoImageOpen(os.path.join(iconpath, "hide.png"))
        self.infoImg = PP.photoImageOpen(os.path.join(iconpath, "info.png"))
        self.openImg = PP.photoImageOpen(os.path.join(iconpath, "open.png"))
        self.playImg = PP.photoImageOpen(os.path.join(iconpath, "play.png"))
        self.refreshImg = PP.photoImageOpen(os.path.join(iconpath, "refresh.png"))
        self.settingsImg = PP.photoImageOpen(os.path.join(iconpath, "settings.png"))
        self.uncheckImg = PP.photoImageOpen(os.path.join(iconpath, "uncheck.png"))

        self.exitButton = tk.Button(self, image=self.exitImg, relief="flat", command=Controller.exitProgram)
        self.settingsButton = tk.Button(self, image=self.settingsImg, relief="flat", command=Controller.configureProgram)
        #
        self.infoButton = tk.Button(self, image=self.infoImg, relief="flat", command=IW.showInfoDialog)

        self.openButton = tk.Button(self, image=self.openImg, relief="flat", command=Controller.openFolder)
        self.addButton = tk.Button(self, image=self.addImg, relief="flat", command=Controller.addFolder)
        #
        self.refreshButton = tk.Button(self, image=self.refreshImg, relief="flat", command=Controller.resetThumbnails)

        self.uncheckButton = tk.Button(self, image=self.uncheckImg, relief="flat", command=Controller.unselectThumbnails)
        self.deleteButton = tk.Button(self, image=self.deleteImg, relief="flat", command=Controller.deleteSelected)
        self.hideButton = tk.Button(self, image=self.hideImg, relief="flat", command=Controller.hideSelected)
        self.playButton = tk.Button(self, image=self.playImg, relief="flat", command=Controller.viewSelected)

        self.exitButton.grid(column=0, row=0)
        self.settingsButton.grid(column=1, row=0)
        #
        self.infoButton.grid(column=3, row=0)

        self.openButton.grid(column=0, row=1)
        self.addButton.grid(column=1, row=1)
        #
        self.refreshButton.grid(column=3, row=1)

        self.uncheckButton.grid(column=0, row=2)
        self.deleteButton.grid(column=1, row=2)
        self.hideButton.grid(column=2, row=2)
        self.playButton.grid(column=3, row=2)

        TT.Tooltip(self.addButton, text='Add folder of images')
        TT.Tooltip(self.deleteButton, text='Delete Selected Images')
        TT.Tooltip(self.exitButton, text='Quit')
        TT.Tooltip(self.hideButton, text='Hide Selected Images')
        TT.Tooltip(self.infoButton, text='Quick instructions')
        TT.Tooltip(self.openButton, text='Open folder of images')
        TT.Tooltip(self.playButton, text='View Selected Images')
        TT.Tooltip(self.refreshButton, text='Start fresh with all images shown')
        TT.Tooltip(self.settingsButton, text='Settings')
        TT.Tooltip(self.uncheckButton, text='Unselect all images')
