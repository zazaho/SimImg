import os
import tkinter as tk
from PIL import ImageTk, Image
import classes.tooltip as TT
import classes.infowindow as IW

class Toolbar(tk.Frame):
    " A toolbar frame that holds the action buttons"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)
        self.Ctrl = Controller
        self.config(bd=1, relief="raised")

        iconpath = self.Ctrl.Cfg.get('IconPath')

        self.exitImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "exit.png")))
        self.settingsImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "settings.png")))
        self.infoImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "info.png")))

        self.refreshImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "refresh.png")))
        self.openImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "open.png")))
        self.uncheckImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "uncheck.png")))

        self.deleteImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "delete.png")))
        self.hideImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "hide.png")))
        self.playImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "play.png")))

        self.exitButton = tk.Button(self, image=self.exitImg, relief="flat", command=self.onexit )
        self.settingsButton = tk.Button(self, image=self.settingsImg, relief="flat", command=self.onsettings )
        self.infoButton = tk.Button(self, image=self.infoImg, relief="flat", command=self.oninfo )

        self.refreshButton = tk.Button(self, image=self.refreshImg, relief="flat", command=self.onrefresh )
        self.openButton = tk.Button(self, image=self.openImg, relief="flat", command=self.onopen )
        self.uncheckButton = tk.Button(self, image=self.uncheckImg, relief="flat", command=self.onuncheck )
        
        self.deleteButton = tk.Button(self, image=self.deleteImg, relief="flat", command=self.ondelete )
        self.hideButton = tk.Button(self, image=self.hideImg, relief="flat", command=self.onhide )
        self.playButton = tk.Button(self, image=self.playImg, relief="flat", command=self.onplay )

        self.exitButton.grid(column=0, row=0, padx=2, pady=2)
        self.settingsButton.grid(column=1, row=0, padx=2, pady=2)
        self.infoButton.grid(column=2, row=0, padx=2, pady=2)

        self.refreshButton.grid(column=0, row=1, padx=2, pady=2)
        self.openButton.grid(column=1, row=1, padx=2, pady=2)
        self.uncheckButton.grid(column=2, row=1, padx=2, pady=2)
        
        self.deleteButton.grid(column=0, row=2, padx=2, pady=2)
        self.hideButton.grid(column=1, row=2, padx=2, pady=2)
        self.playButton.grid(column=2, row=2, padx=2, pady=2)

        TT.Tooltip(self.exitButton, text='Quit')
        TT.Tooltip(self.settingsButton, text='Settings')
        TT.Tooltip(self.infoButton, text='Quick instructions')

        TT.Tooltip(self.refreshButton, text='Start fresh with all images shown')
        TT.Tooltip(self.openButton, text='Open folder of images')
        TT.Tooltip(self.uncheckButton, text='Unselect all images')

        TT.Tooltip(self.deleteButton, text='Delete Selected Images')
        TT.Tooltip(self.hideButton, text='Hide Selected Images')
        TT.Tooltip(self.playButton, text='View Selected Images')

        
    def onexit(self):
        self.Ctrl.exitProgram()
    
    def onsettings(self):
        self.Ctrl.configureProgram()

    def oninfo(self):
        IW.showInfoDialog()
    
    def ondelete(self):
        self.Ctrl.deleteSelected()
    
    def onhide(self):
        self.Ctrl.hideSelected()
    
    def onplay(self):
        self.Ctrl.viewSelected()

    def onrefresh(self):
        self.Ctrl.resetThumbnails()

    def onuncheck(self):
        self.Ctrl.unselectThumbnails()

    def onopen(self):
        self.Ctrl.openFolder()
