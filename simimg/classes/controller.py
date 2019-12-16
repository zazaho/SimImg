''' Controller module:
The main gateway between the information contained in the database,
the fileinfo objects and the display.
 '''
import sys
import os
import glob
import itertools
import tkinter as tk
from tkinter import filedialog as tkfiledialog
from PIL import ImageTk
import simimg.classes.conditionmodules as CM
import simimg.classes.fileobject as FO
import simimg.classes.imageframe as IF
import simimg.classes.toolbar as TB
import simimg.dialogs.confirmdeletedialog as CDD
import simimg.dialogs.configurationwindow as CW
import simimg.dialogs.infowindow as IW
import simimg.dialogs.viewer as VI
import simimg.utils.database as DB
import simimg.utils.handyfunctions as HF
import simimg.utils.pooling as POOL

class Controller():
    'Controller object that initializes the program and reacts to events.'
    def __init__(self, parent):

        self.TopWindow = parent
        self.Cfg = parent.Cfg
        self.maxThumbnails = self.Cfg.get('maxthumbnails')

        # empty starting values
        self.DBConnection = None
        self.fileList = []
        self.filenameCommon = ""
        self.filenameUniqueDict = {}
        self.FODict = {}
        self.TPPositionDict = {}
        self.matchingGroups = []
        self.MD5HashesDict = {}
        self.lastSelectedXY = None

        # call the exitProgram function when the user clicks the X
        self.TopWindow.protocol("WM_DELETE_WINDOW", self.exitProgram)
        # allow some key actions (Ctrl-A, Ctl-D, Ctrl-H, Ctrl-V and F1)
        self.TopWindow.bind("<Key>", self._onKeyPress)
        # bind clicking in an empty area of the thumbPane to unselectThumbnails
        self.TopWindow.ThumbPane.viewPort.bind("<Button-1>",  self.unselectThumbnails)

        # put the toolbar in the self.TopWindow.ModulePane
        Toolbar = TB.Toolbar(self.TopWindow.ModulePane, Controller=self)
        Toolbar.pack(side=tk.TOP, fill='x')

        # create the condition modules in the self.TopWindow.ModulePane
        # put them in a list so that we can easily iterate over them
        self.CMList = []
        if self.Cfg.get('haveimagehash'):
            self.CMList.append(CM.HashCondition(self.TopWindow.ModulePane, Controller=self))

        self.CMList.extend([
            CM.HSVCondition(self.TopWindow.ModulePane, Controller=self),
            CM.DateCondition(self.TopWindow.ModulePane, Controller=self),
            CM.CameraCondition(self.TopWindow.ModulePane, Controller=self),
            CM.ShapeCondition(self.TopWindow.ModulePane, Controller=self),
        ])
        for cm in self.CMList:
            cm.pack(side=tk.TOP, fill='x')

        self.startDatabase()
        self._getFileList()
        self._processFilelist()
        self.onFileListChanged()
        
    def _onKeyPress(self, event):
        if event.keysym == 'F1':
            IW.showInfoDialog()
            return
        if (event.state & 0x4) != 0:
            keyDict = {
                'a':self.selectAllThumbnails,
                'd':self.deleteSelected,
                'h':self.hideSelected,
                'v':self.viewSelected,
                'q':self.exitProgram
            }
            if event.keysym in keyDict:
                keyDict[event.keysym]()
                return

    def startDatabase(self, clear=None):
        self.DBConnection = DB.CreateDBConnection(
            self.Cfg.get('databasename')
        )
        if not self.DBConnection:
            sys.exit(1)

        if not DB.CreateDBTables(self.DBConnection, clear=clear):
            sys.exit(1)

    def stopDatabase(self):
        DB.CloseDBConnection(self.DBConnection)

    def exitProgram(self):
        self.stopDatabase()
        self.Cfg.set('findergeometry', self.TopWindow.geometry())
        self.Cfg.writeConfiguration()
        self.TopWindow.quit()
    
    def configureProgram(self):
        oldThumbsize = self.Cfg.get('thumbnailsize')
        oldShowButtons = self.Cfg.get('showbuttons')
        CW.CfgWindow(self.TopWindow, Controller=self)
        if self.Cfg.get('thumbnailsize') != oldThumbsize or self.Cfg.get('showbuttons') != oldShowButtons:
            self._setThumbnails()
            self._onThumbnailsChanged()

    def addFolder(self):
        selectedFolder = tkfiledialog.askdirectory()
        if not selectedFolder:
            return
        if not os.path.isdir(selectedFolder):
            return
        self._getFileList(Add=selectedFolder)
        self._processFilelist()
        self.onFileListChanged()
        
    def openFolder(self):
        selectedFolder = tkfiledialog.askdirectory()
        if not selectedFolder:
            return
        if not os.path.isdir(selectedFolder):
            return
        self._getFileList(Replace=selectedFolder)
        self._processFilelist()
        self.onFileListChanged()

    def _showInStatusbar(self, txt):
        self.TopWindow.Statusbar.config(text=txt)
        self.TopWindow.Statusbar.update_idletasks()

    def _processFilelist(self):
        ''' Things to do when starting with new image(s)/path'''

        #clear messages from the statusbar
        self._showInStatusbar("...")

        # calculate md5s in multiprocessing
        self._showInStatusbar("Calculating File Hash values, please be patient")
        self._getMD5Hashes()
        self._showInStatusbar("...")

        self._createFileobjects()
        if not self.FODict:
            self._showInStatusbar("Warning: no files containing image data found")

        # calculate thumbnails in multiprocessing
        self._setThumbnails()
        
    def _getFileList(self, Replace=None, Add=None):
        pathList = []
        #determine which mode we are called
        # from openFolder
        if Replace:
            pathList = [Replace]
            oldFiles = []
            self.FODict = {}
        # from add folder    
        if Add:
            pathList = [Add]
            oldFiles = self.fileList

        # from startup
        if not Replace and not Add:
            pathList = self.Cfg.get('cmdlinearguments')
            oldFiles = []
            self.FODict = {}

        # from startup without arguments
        if not pathList:
            oldFiles = []
            startupFolder = self.Cfg.get('startupfolder')
            # start empty
            if not startupFolder:
                self.fileList = []
                return
            pathList = [startupFolder]

        # now we know which folders to search
        doRecurse = self.Cfg.get('searchinsubfolders')
        candidates = []
        for arg in pathList:
            arg = os.path.abspath(arg)
            if os.path.isdir(arg):
                candidates.extend(glob.glob(arg+'/**', recursive=doRecurse))
            else:
                candidates.append(arg)
        self.fileList = [c for c in candidates if os.path.isfile(c)]
        self.fileList.extend(oldFiles)
        self.fileList = list(set(self.fileList))
        self.fileList.sort()

        # split the fileList into a common and a unique part
        self.filenameCommon, filenameUniqueList = HF.stringList2CommonUnique(self.fileList)
        self.filenameUniqueDict = {}
        self.filenameUniqueDict.update(zip(self.fileList, filenameUniqueList))

    def _createFileobjects(self):

        # Make list of image file objects with all files the installed PIL can read
        ImageFileObjectList = []
        # dont create FOs for files that already have a FODict
        existingfiles = []
        for fol in self.FODict.values():
            existingfiles.extend([fo.FullPath for fo in fol])
            
        missingfilelist = list(set(self.fileList) - set(existingfiles))
        for FilePath in missingfilelist:
            ThisFileObject = FO.FileObject(self,
                                           FullPath=FilePath,
                                           MD5HashesDict=self.MD5HashesDict
            )
            if ThisFileObject.IsImage():
                ImageFileObjectList.append(ThisFileObject)
                # do md5 hash and thumbnails
                ThisFileObject.md5()

        if not ImageFileObjectList:
            return

        # transform into a dict based on uniq md5
        newFODict = HF.pairListToDict([(i.md5(), i) for i in ImageFileObjectList])
        self.FODict.update(newFODict)
        
    def _createViewWithoutConditions(self):
        'Create an overview of all images without conditions'
        self._removeAllThumbs()

        # because there are no criteria display thumbnails in order
        # calculate how many thumbs fit in the viewPort
        maxW = self.TopWindow.ThumbPane.winfo_width()
        thumbW = 2 * self.Cfg.get('thumbnailborderwidth') + self.Cfg.get('thumbnailsize')
        nx = maxW // thumbW
        
        # maximum nx*ny thumbs to show
        thumbToShow = 0
        for md5 in HF.sortMd5sByFilename(self.FODict.keys(), self.MD5HashesDict):
            if not self.FODict[md5][0].active:
                continue
            X = thumbToShow % nx
            Y = thumbToShow // nx
            self._showThumbXY(md5, X, Y)
            thumbToShow += 1
            if thumbToShow >= self.maxThumbnails:
                break
        
    def _showThumbXY(self, md5, X, Y):
        # make sure that if a thumb is currently shown it is removed
        # and deleted
        self._removeThumbXY(X,Y)
        # create a new thumbnail
        ThisThumb = IF.ImageFrame(
            self.TopWindow.ThumbPane.viewPort,
            Ctrl=self,
            md5=md5,
            X=X,
            Y=Y
        )
        # show the new one
        ThisThumb.grid(column=X, row=Y)
        # add thisthumb to the TPPositionDict
        self.TPPositionDict[(X, Y)] = ThisThumb

    def _removeThumbXY(self, X, Y):
        ThisThumb = self.TPPositionDict[(X,Y)] if (X,Y) in self.TPPositionDict else None
        if ThisThumb:
            del self.TPPositionDict[(X, Y)]
            ThisThumb.destroy()

    def _removeAllThumbs(self):
        for ThisThumb in self.TPPositionDict.values():
            ThisThumb.destroy()
        self.TPPositionDict = {}

    def _getMatchingGroups(self, activePairs):
        ''' given the matching groups returned by each active condition module
           make a master list of image groups '''

        self.matchingGroups = []
        matchingGroupsList = []
        MMMatchingGroupsList = []
        for cm in self.CMList:
            if not cm.active:
                continue
            thisMatchingGroups = cm.matchingGroups(activePairs)
            matchingGroupsList.append(thisMatchingGroups)
            if cm.mustMatch.get():
                MMMatchingGroupsList.append(thisMatchingGroups)

        # nothing activated. Start-over
        if not matchingGroupsList:
            self._createViewWithoutConditions()
            return

        matchingGroups = HF.mergeGroupLists(matchingGroupsList)

        if not matchingGroups:
            return

        if MMMatchingGroupsList:
            matchingGroups = HF.applyMMGroupLists(matchingGroups, MMMatchingGroupsList)

        if not matchingGroups:
            return

        # remove "groups" of only one image
        matchingGroups = [mg for mg in matchingGroups if len(mg) > 1]

        if not matchingGroups:
            return

        matchingGroups.sort()
        uniqueMatchingGroups = []
        for MG in matchingGroups:
            if not HF.existsAsSubGroup(MG, uniqueMatchingGroups):
                uniqueMatchingGroups.append(MG)

        self.matchingGroups = uniqueMatchingGroups
        self.matchingGroups.sort()

    def _displayMatchingGroups(self):
        #clear messages from the statusbar
        self._showInStatusbar("...")
        sortedGroupsList = HF.sortMd5ListsByFilename(self.matchingGroups, self.MD5HashesDict)
        for Y, group in enumerate(sortedGroupsList):
            md5s = [group[0]]
            md5s.extend(HF.sortMd5sByFilename(group[1:], self.MD5HashesDict))
            for X, md5 in enumerate(md5s):
                self._showThumbXY(md5, X, Y)
            if X*Y > self.maxThumbnails:
                self._showInStatusbar("Warning too many matches: truncated to ~%s" % self.maxThumbnails)
                return

    def onConditionChanged(self):
        # put everything to default
        self.matchingGroups = []
        # make sure to clean the interface
        self._removeAllThumbs()

        activeMD5s = [md5 for md5, FO in self.FODict.items() if FO[0].active]
        if not activeMD5s:
            return
        activeMD5s.sort()

        activePairs = list(itertools.combinations(activeMD5s,2))
        if not activePairs:
            return
        activePairs.sort()

        self._getMatchingGroups(activePairs)

        self._displayMatchingGroups()

    def onFileListChanged(self):
        self.onConditionChanged()

    def _onThumbnailsChanged(self):
        # check if any conditions are active
        someCMActive = False
        for cm in self.CMList:
            if cm.active:
                someCMActive = True
                break
        if someCMActive:
            self._displayMatchingGroups()
        else:
            self._createViewWithoutConditions()

    def resetThumbnails(self):
        for foList in self.FODict.values():
            for fo in foList:
                fo.active = True
        self.onFileListChanged()
    
    # functions related to the selected thumbnails
    def _selectedFOs(self, firstFOOnly = False):
        lst = []
        for tp in self.TPPositionDict.values():
            if tp.selected:
                if firstFOOnly:
                    lst.append(self.FODict[tp.md5][0])
                else:
                    lst.extend(self.FODict[tp.md5])
        return lst
        
    def viewSelected(self):
        fileinfo = [(fo.md5(), fo.FullPath) for fo in self._selectedFOs(firstFOOnly = True)]
        if fileinfo:
            VI.viewer(Fileinfo=fileinfo, Controller=self)

    def hideSelected(self):
        for fo in self._selectedFOs():
            fo.active = False
        self.onFileListChanged()

    def _deleteFile(self, Filename):
        if self.Cfg.get('gzipinsteadofdelete'):
            HF.gzipfile(Filename)
        else:
            os.remove(Filename)
    
    def deleteFOs(self, FOs, Owner=None):
        somethingDeleted = False
        mustconfirm = self.Cfg.get('confirmdelete')
        onlyOneFO = len(FOs) == 1
        for fo in FOs:
            filename = fo.FullPath
            uniqueFilename = self.filenameUniqueDict[filename]
            md5 = fo.md5()
            if mustconfirm:
                answer = CDD.CDDialog(
                    Owner,
                    Filename=uniqueFilename,
                    simple=onlyOneFO
                ).result
            else:
                answer = "yes"
            if answer == "abort":
                break
            if answer == "no":
                continue
            if answer == "yestoall":
                mustconfirm = False
                answer = "yes"
            if answer == "yes":
                if md5 in self.FODict:
                    del self.FODict[md5]
                somethingDeleted = True
                self._deleteFile(filename)

        if somethingDeleted:
            self.onFileListChanged()
        return somethingDeleted
    
    def deleteSelected(self):
        self.deleteFOs(self._selectedFOs(), Owner=self.TopWindow)
                
    def unselectThumbnails(self, *args):
        for tp in self.TPPositionDict.values():
            tp.select(False)
        self.lastSelectedXY = None

    def selectAllThumbnails(self, *args):
        for tp in self.TPPositionDict.values():
            tp.select(True)
        self.lastSelectedXY = None

    def toggleSelectRow(self, Y, value):
        for tp in self.TPPositionDict.values():
            if tp.Y == Y:
                tp.select(value)

    def selectRangeFromLastSelected(self, X, Y):
        def gridXYLargerOrEqual(c1, c2):
            (x1, y1) = c1
            (x2, y2) = c2
            if y1 > y2:
                return True
            if y1 < y2:
                return False
            if x1 < x2:
                return False
            return True
            
        if not self.lastSelectedXY:
            return

        fromXY = self.lastSelectedXY
        toXY = (X,Y)
        if gridXYLargerOrEqual(fromXY, toXY):
            fromXY, toXY = toXY, fromXY

        for tp in self.TPPositionDict.values():
            if (
                    gridXYLargerOrEqual((tp.X, tp.Y), fromXY) and
                    gridXYLargerOrEqual(toXY, (tp.X, tp.Y))
            ):
                tp.select(True)

    # some routines related to expensive calculations done in a
    # multiprocessing pool
    def _getMD5Hashes(self):
        self.MD5HashesDict = POOL.GetMD5Hashes(self.fileList, self.MD5HashesDict)

    def _setThumbnails(self):
        MD5ThumbDict = POOL.GetMD5Thumbnails(
            self.FODict,
            Thumbsize=self.Cfg.get('thumbnailsize')
        )
        if not MD5ThumbDict:
            return
        for md5, thumb in MD5ThumbDict.items():
            if not thumb:
                del self.FODict[md5]
                continue
            fo = self.FODict[md5]
            for afo in fo:
                afo._Thumbnail = ImageTk.PhotoImage(thumb)

    def setImageHashes(self, hashName=None):
        self._showInStatusbar("Calculating Image Hash values, please be patient")
        POOL.GetImageHashes(self.FODict, hashName, self.DBConnection)
        self._showInStatusbar("...")
