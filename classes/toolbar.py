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
        self.deleteImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "delete.png")))
        self.hideImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "hide.png")))
        self.playImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "play.png")))

        self.exitButton = tk.Button(self, image=self.exitImg, relief="flat", command=self.onexit )
        self.settingsButton = tk.Button(self, image=self.settingsImg, relief="flat", command=self.onsettings )
        self.infoButton = tk.Button(self, image=self.infoImg, relief="flat", command=self.oninfo )
        self.deleteButton = tk.Button(self, image=self.deleteImg, relief="flat", command=self.ondelete )
        self.hideButton = tk.Button(self, image=self.hideImg, relief="flat", command=self.onhide )
        self.playButton = tk.Button(self, image=self.playImg, relief="flat", command=self.onplay )

        self.exitButton.grid(column=0, row=0, padx=2, pady=2)
        self.settingsButton.grid(column=1, row=0, padx=2, pady=2)
        self.infoButton.grid(column=2, row=0, padx=2, pady=2)
        self.deleteButton.grid(column=0, row=1, padx=2, pady=2)
        self.hideButton.grid(column=1, row=1, padx=2, pady=2)
        self.playButton.grid(column=2, row=1, padx=2, pady=2)

        TT.Tooltip(self.exitButton, text='Quit')
        TT.Tooltip(self.settingsButton, text='Settings')
        TT.Tooltip(self.infoButton, text='Quick instructions')
        TT.Tooltip(self.deleteButton, text='Delete Selected Images')
        TT.Tooltip(self.hideButton, text='Hide Selected Images')
        TT.Tooltip(self.playButton, text='View Selected Images')

    def onexit(self):
        pass
    
    def onsettings(self):
        pass

    def oninfo(self):
        IW.showInfoDialog()
    
    def ondelete(self):
        pass
    
    def onhide(self):
        self.Ctrl.hideSelected()
    
    def onplay(self):
        pass
