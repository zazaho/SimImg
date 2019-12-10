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
        self.addImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "add.png")))

        self.uncheckImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "uncheck.png")))
        self.deleteImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "delete.png")))
        self.hideImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "hide.png")))
        self.playImg = ImageTk.PhotoImage(Image.open(os.path.join(iconpath, "play.png")))

        self.exitButton = tk.Button(self, image=self.exitImg, relief="flat", command=self.onExit )
        self.settingsButton = tk.Button(self, image=self.settingsImg, relief="flat", command=self.onSettings )
        self.infoButton = tk.Button(self, image=self.infoImg, relief="flat", command=self.onInfo )

        self.refreshButton = tk.Button(self, image=self.refreshImg, relief="flat", command=self.onRefresh )
        self.openButton = tk.Button(self, image=self.openImg, relief="flat", command=self.onOpen )
        self.addButton = tk.Button(self, image=self.addImg, relief="flat", command=self.onAdd )

        self.uncheckButton = tk.Button(self, image=self.uncheckImg, relief="flat", command=self.onUncheck )
        self.deleteButton = tk.Button(self, image=self.deleteImg, relief="flat", command=self.onDelete )
        self.hideButton = tk.Button(self, image=self.hideImg, relief="flat", command=self.onHide )
        self.playButton = tk.Button(self, image=self.playImg, relief="flat", command=self.onPlay )

        self.exitButton.grid(column=0, row=0)
        self.settingsButton.grid(column=1, row=0)
        self.infoButton.grid(column=3, row=0)

        self.openButton.grid(column=0, row=1)
        self.addButton.grid(column=1, row=1)
        self.refreshButton.grid(column=3, row=1)

        self.uncheckButton.grid(column=0, row=2)
        self.deleteButton.grid(column=1, row=2)
        self.hideButton.grid(column=2, row=2)
        self.playButton.grid(column=3, row=2)

        TT.Tooltip(self.exitButton, text='Quit')
        TT.Tooltip(self.settingsButton, text='Settings')
        TT.Tooltip(self.infoButton, text='Quick instructions')

        TT.Tooltip(self.refreshButton, text='Start fresh with all images shown')
        TT.Tooltip(self.openButton, text='Open folder of images')
        TT.Tooltip(self.addButton, text='Add folder of images')

        TT.Tooltip(self.uncheckButton, text='Unselect all images')
        TT.Tooltip(self.deleteButton, text='Delete Selected Images')
        TT.Tooltip(self.hideButton, text='Hide Selected Images')
        TT.Tooltip(self.playButton, text='View Selected Images')

    def onExit(self):
        self.Ctrl.exitProgram()
    
    def onSettings(self):
        self.Ctrl.configureProgram()

    def onInfo(self):
        IW.showInfoDialog()
    
    def onDelete(self):
        self.Ctrl.deleteSelected()
    
    def onHide(self):
        self.Ctrl.hideSelected()
    
    def onPlay(self):
        self.Ctrl.viewSelected()

    def onRefresh(self):
        self.Ctrl.resetThumbnails()

    def onUncheck(self):
        self.Ctrl.unselectThumbnails()

    def onAdd(self):
        self.Ctrl.addFolder()
        self.Ctrl.processFilelist()
        self.Ctrl.onThumbnailChanged()

    def onOpen(self):
        self.Ctrl.openFolder()
        self.Ctrl.processFilelist()
        self.Ctrl.onThumbnailChanged()
