""" Controller module:
The main gateway between the information contained in the database,
the fileinfo objects and the display of the thumbnails.
 """
import glob
import os
import sys
from tkinter import ttk
from tkinter import filedialog as tkfiledialog

from PIL import ImageTk

import simimg.classes.conditionmodules as CM
import simimg.classes.fileobject as FO
import simimg.classes.imageframe as IF
import simimg.classes.miscmodules as MM
import simimg.classes.toolbar as TB
import simimg.classes.tooltip as TT
import simimg.dialogs.configurationwindow as CW
import simimg.dialogs.confirmdeletedialog as CDD
import simimg.dialogs.infowindow as IW
import simimg.dialogs.viewer as VI
import simimg.utils.database as DB
import simimg.utils.handyfunctions as HF
import simimg.utils.pooling as POOL

# decorator to change cursor when calling a method that might take time
def longrunning(f):
    """ Show with the cursor that the program is doing a (long) calculation"""

    def wrapper(self, *args, **kwargs):
        self.busyCursorCount += 1
        self.TopWindow.config(cursor="watch")
        f(self, *args, **kwargs)
        self.busyCursorCount -= 1
        # make sure not to go below 0
        self.busyCursorCount = max(0, self.busyCursorCount)
        if not self.busyCursorCount:
            self.TopWindow.config(cursor="")
    return wrapper


# decorator to show message in status bar for the duration of a function call
def tellstatus(msg):
    def decorator_tellstatus(f):
        def wrapper_tellstatus(self, *args, **kwargs):
            if msg:
                self.showInStatusbar(msg)
            f(self, *args, **kwargs)
            self.showInStatusbar("...")
        return wrapper_tellstatus
    return decorator_tellstatus


class Controller():
    "Controller object that initializes the program and reacts to events."

    def __init__(self, parent):

        self.TopWindow = parent
        self.Cfg = parent.Cfg
        self.lastSelectedXY = None

        self._maxThumbnails = self.Cfg.get("maxthumbnails")

        # empty starting values
        self.FODict = {}
        self._DBConnection = None
        self._fileList = []
        self._filenameCommon = ""
        self._filenameUniqueDict = {}
        self._TPPositionDict = {}
        self._matchingGroups = {}
        self._checksumFilenameDict = {}
        self._filenameChecksumDict = {}
        self.busyCursorCount = 0
        self._someConditionActive = False

        # call the exitProgram function when the user clicks the X
        self.TopWindow.protocol("WM_DELETE_WINDOW", self.exitProgram)
        # allow some key actions (Ctrl-A, Ctl-D, Ctrl-H, Ctrl-V and F1)
        self.TopWindow.bind("<Key>", self._onKeyPress)
        # bind clicking in an empty area of the thumbPane to unselectThumbnails
        self.TopWindow.ThumbPane.viewPort.bind("<Button-1>", self.unselectThumbnails)
        self.TopWindow.ThumbPane.canvas.bind("<Button-1>", self.unselectThumbnails)

        # allow some key actions (Ctrl-A, Ctl-D, Ctrl-H, Ctrl-V and F1)
        self.TopWindow.ThumbPane.bind("<Configure>", self._onConfigure)
        self._TPWidth = 0

        # put the toolbar in the self.TopWindow.ModulePane
        Toolbar = TB.Toolbar(self.TopWindow.ModulePane, Controller=self)
        Toolbar.pack(side="top", fill="x")

        ttk.Label(
            self.TopWindow.ModulePane,
            text="Display",
            style="HeaderText.TLabel"
        ).pack(fill="x")

        ThumbOpt = MM.ThumbOptions(self.TopWindow.ModulePane, Controller=self)
        ThumbOpt.pack(side="top", fill="x")

        ttk.Label(
            self.TopWindow.ModulePane,
            text="Filters",
            style="HeaderText.TLabel"
        ).pack(fill="x")

        # create the condition modules in the self.TopWindow.ModulePane
        # put them in a list so that we can easily iterate over them
        self._CMList = []
        self._CMList.extend([
            CM.ColorCondition(self.TopWindow.ModulePane, Controller=self),
            CM.GradientCondition(self.TopWindow.ModulePane, Controller=self),
            CM.DateCondition(self.TopWindow.ModulePane, Controller=self),
            CM.CameraCondition(self.TopWindow.ModulePane, Controller=self),
            CM.ShapeCondition(self.TopWindow.ModulePane, Controller=self),
        ])
        for cm in self._CMList:
            cm.pack(side="top", fill="x")
            # restore the saved folded/unfolded state
            if self.Cfg.get(f"{cm.name}_folded"):
                cm.toggleFolding()

        moveheader = ttk.Label(
            self.TopWindow.ModulePane,
            text="Move",
            style="HeaderText.TLabel"
        )
        moveheader.pack(fill="x")
        msg = """Move file(s) to the folder selected below.

1) Click on the move button below each thumbnail

2) For selected pictures by clicking on the move icon in the toolbar or pressing Ctrl-m

3) Press m in the viewer window

Right click on the folders below to set or change its path"""
        TT.Tooltip(moveheader, text=msg)

        self._MovePanel = MM.MovePanel(self.TopWindow.ModulePane, Controller=self)
        self._MovePanel.pack(side="top", fill="x")

        self.startDatabase()
        self._getFileList()
        self._processFilelist()
        self.onChange()

    def _onConfigure(self, event):
        thumbW = self.Cfg.get("thumbnailsize") + 2
        oldTPWidth = self._TPWidth
        self._TPWidth = event.width
        # check of the number of thumb columns will change
        if oldTPWidth // thumbW == self._TPWidth // thumbW:
            return
        if not self._someConditionActive:
            self._createViewWithoutConditions()

    def _onKeyPress(self, event):
        if event.keysym == "F1":
            IW.showInfoDialog()
            return
        if (event.state & 0x4) != 0:
            keyDict = {
                "a": self.toggleSelectAllThumbnails,
                "d": self.deleteSelected,
                "h": self.hideSelected,
                "m": self.moveSelected,
                "v": self.viewSelected,
                "q": self.exitProgram
            }
            if event.keysym in keyDict:
                keyDict[event.keysym]()
                return

    def showInStatusbar(self, txt):
        self.TopWindow.Statusbar.config(text=txt)
        self.TopWindow.Statusbar.update_idletasks()

    def _showThumbXY(self, checksum, X, Y):
        # make sure that if a thumb is currently shown it is removed
        # and deleted
        self._removeThumbXY(X, Y)
        # create a new thumbnail
        ThisThumb = IF.ImageFrame(
            self.TopWindow.ThumbPane.viewPort,
            Ctrl=self,
            checksum=checksum,
            X=X,
            Y=Y
        )
        # show the new one
        ThisThumb.grid(column=X, row=Y)
        # add thisthumb to the _TPPositionDict
        self._TPPositionDict[(X, Y)] = ThisThumb

    def _removeThumbXY(self, X, Y):
        if (X, Y) in self._TPPositionDict:
            self._TPPositionDict[(X, Y)].destroy()
            del self._TPPositionDict[(X, Y)]

    def _removeAllThumbs(self):
        for ThisThumb in self._TPPositionDict.values():
            ThisThumb.destroy()
        self._TPPositionDict = {}

    def startDatabase(self, clear=None):
        self._DBConnection = DB.createConnection(
            self.Cfg.get("databasename")
        )
        if not self._DBConnection:
            sys.exit(1)

        if not DB.createTables(self._DBConnection, clear=clear):
            sys.exit(1)

    def stopDatabase(self):
        DB.closeConnection(self._DBConnection)

    def exitProgram(self):
        self.stopDatabase()
        self.Cfg.set("findergeometry", self.TopWindow.geometry())
        # make a dictionary of cm.name: is_folded
        folding_dict = {cm.name: cm.is_folded for cm in self._CMList}
        self.Cfg.set("folding_dict", folding_dict)
        self.Cfg.writeConfiguration()
        self.TopWindow.quit()

    def configureProgram(self):
        oldThumbsize = self.Cfg.get("thumbnailsize")
        oldUpscale = self.Cfg.get("upscalethumbnails")
        CW.CfgWindow(self.TopWindow, Controller=self)
        if (
                self.Cfg.get("thumbnailsize") != oldThumbsize or
                self.Cfg.get("upscalethumbnails") != oldUpscale
        ):
            self.onThumbParamsChanged()

    def addOrOpenFolder(self, action=None):
        selectedFolder = tkfiledialog.askdirectory()
        if not selectedFolder:
            return
        if not os.path.isdir(selectedFolder):
            return
        if action == "add":
            self._getFileList(Add=selectedFolder)
        else:
            self._getFileList(Replace=selectedFolder)
        self._processFilelist()
        self.onChange()

    @longrunning
    @tellstatus(msg="Gathering the files to show")
    def _getFileList(self, Replace=None, Add=None):
        pathList = []
        # determine with which mode we are called
        # from openFolder
        if Replace:
            pathList = [Replace]
            oldFiles = []
            self.FODict = {}
        # from add folder
        if Add:
            pathList = [Add]
            oldFiles = self._fileList

        # from startup
        if not Replace and not Add:
            pathList = self.Cfg.get("cmdlinearguments")
            oldFiles = []
            self.FODict = {}

        # from startup without arguments
        if not pathList:
            oldFiles = []
            startupFolder = self.Cfg.get("startupfolder")
            # start empty
            if not startupFolder:
                self._fileList = []
                return
            pathList = [startupFolder]

        # now we know which folders to search
        doRecurse = self.Cfg.get("searchinsubfolders")
        candidates = []
        for arg in pathList:
            arg = os.path.abspath(arg)
            if os.path.isdir(arg):
                candidates.extend(glob.glob(arg+"/**", recursive=doRecurse))
            else:
                candidates.append(arg)
        self._fileList = [c for c in candidates if os.path.isfile(c)]
        # check to make sure that the file list is not excessively long
        # three times more than we can anyway show
        # probably this means the program was started in the wrong directory
        # and or recursive was set wrongly
        if len(self._fileList) > 3*self._maxThumbnails:
            # just to be safe we truncated the list
            self._fileList = self._fileList[0:3*self._maxThumbnails]

        self._fileList.extend(oldFiles)
        self._fileList = list(set(self._fileList))

        # split the _fileList into a common and a unique part
        self._filenameCommon, filenameUniqueList = HF.stringlist2commonunique(self._fileList)
        self._filenameUniqueDict = {}
        self._filenameUniqueDict.update(zip(self._fileList, filenameUniqueList))

    @longrunning
    @tellstatus(msg="Processing file list")
    def _processFilelist(self):
        """ Things to do when starting with new image(s)/path"""

        # calculate checksums in multiprocessing
        self._getChecksums()

        self._createFileobjects()
        if not self.FODict:
            self.showInStatusbar("Warning: no files containing image data found")

        # calculate thumbnails in multiprocessing
        self._setThumbnails()

    def _createFileobjects(self):
        # Make list of image file objects with all files PIL can read
        fileObjectList = []
        # dont create FOs for files that already have a FODict
        existingfiles = []
        for fol in self.FODict.values():
            existingfiles.extend([fo.fullPath for fo in fol])

        missingfilelist = list(set(self._fileList) - set(existingfiles))
        for FilePath in missingfilelist:
            ThisFileObject = FO.FileObject(
                self,
                FullPath=FilePath,
                checksumFilenameDict=self._checksumFilenameDict
            )
            if ThisFileObject.isImage:
                fileObjectList.append(ThisFileObject)
                # do checksum hash and thumbnails
                ThisFileObject.checksum()

        if not fileObjectList:
            return

        # transform into a dict based on uniq checksum
        newFODict = HF.pairlist2dict([(i.checksum(), i) for i in fileObjectList])
        self.FODict.update(newFODict)

    def _createViewWithoutConditions(self):
        "Create an overview of all images without conditions"
        self._removeAllThumbs()

        # because there are no criteria display thumbnails in order
        # calculate how many thumbs fit in the viewPort
        self.TopWindow.ThumbPane.update_idletasks()
        maxW = self.TopWindow.ThumbPane.winfo_width()
        # 2 extra for the highlight thickness
        thumbW = self.Cfg.get("thumbnailsize") + 2
        nx = maxW // thumbW

        # maximum nx*ny thumbs to show
        thumbToShow = 0
        for checksum in HF.sortChecksumsByFilename(self.FODict.keys(), self._filenameChecksumDict):
            if not self.FODict[checksum][0].active:
                continue
            X = thumbToShow % nx
            Y = thumbToShow // nx
            self._showThumbXY(checksum, X, Y)
            thumbToShow += 1
            if thumbToShow >= self._maxThumbnails:
                break

    def _getMatchingGroups(self):
        """ given the matching groups returned by each active condition module
           make a master list of image groups """

        self._matchingGroups = {}
        matchingGroupDictsList = []
        MMMatchingGroupDictsList = []
        activeChecksums = [checksum for checksum, FO in self.FODict.items() if FO[0].active]
        for cm in self._CMList:
            if not cm.active:
                continue
            thisMatchingGroupDict = cm.matchingGroups(activeChecksums)
            matchingGroupDictsList.append(thisMatchingGroupDict)
            if cm.mustMatch.get():
                MMMatchingGroupDictsList.append(thisMatchingGroupDict)

        matchingGroups = HF.mergeGroupDicts(matchingGroupDictsList)

        if MMMatchingGroupDictsList:
            matchingGroups = HF.applyMMGroupDicts(matchingGroups, MMMatchingGroupDictsList)

        matchingGroups = HF.removeRedunantSubgroups(matchingGroups)

        self._matchingGroups = matchingGroups

    def _displayMatchingGroups(self):
        # clear messages from the statusbar
        self.showInStatusbar("...")
        sortedGroupsList = HF.sortMatchingGroupsByFilename(
            self._matchingGroups,
            self._filenameChecksumDict
        )
        numThumbsShown = 0
        for Y, group in enumerate(sortedGroupsList):
            for X, checksum in enumerate(group):
                self._showThumbXY(checksum, X, Y)
                numThumbsShown += 1
                # no point showing so many
                if X > 25:
                    self.showInStatusbar(
                        "Groups found a group with too many matches: truncated to 25"
                    )
                    break
            if numThumbsShown > self._maxThumbnails:
                self.showInStatusbar(
                    f"Warning too many matches: truncated to ~{self._maxThumbnails}"
                )
                return

    @longrunning
    def onChange(self):
        # put everything to default
        self._matchingGroups = {}
        # make sure to clean the interface
        self._removeAllThumbs()

        # check for active conditions
        self._someConditionActive = False
        for cm in self._CMList:
            if cm.active:
                self._someConditionActive = True
                break
        if self._someConditionActive:
            self._getMatchingGroups()
            self._displayMatchingGroups()
        else:
            self._createViewWithoutConditions()

    @longrunning
    def onThumbElementsChanged(self):
        for thumbframe in self._TPPositionDict.values():
            thumbframe.showOptionalElements()

    @longrunning
    def onThumbParamsChanged(self):
        # the parameters changed we should regenerate the thumbnails
        self._setThumbnails()
        # if one conditions is active just change the shown thumbnails
        # otherwise recreate the whole interface
        # including the number of thumbs per line if thumbnailsize changed
        if self._someConditionActive:
            for thumbframe in self._TPPositionDict.values():
                thumbframe.createThumbContent()
                thumbframe.showOptionalElements()
        else:
            self._createViewWithoutConditions()

    def resetThumbnails(self):
        for foList in self.FODict.values():
            for fo in foList:
                fo.active = True
        self.onChange()

    # functions related to the selected thumbnails
    def _selectedFOs(self, firstFOOnly=False):
        lst = []
        for tp in self._TPPositionDict.values():
            if tp.selected:
                if firstFOOnly:
                    lst.append(self.FODict[tp.checksum][0])
                else:
                    lst.extend(self.FODict[tp.checksum])
        return lst

    def viewSelected(self):
        fileinfo = [(fo.checksum(), fo.fullPath) for fo in self._selectedFOs(firstFOOnly=True)]
        if fileinfo:
            VI.Viewer(Fileinfo=fileinfo, Controller=self)

    def hideSelected(self):
        for fo in self._selectedFOs():
            fo.active = False
        self.onChange()

    def _deleteFile(self, Filename):
        if self.Cfg.get("gzipinsteadofdelete"):
            HF.gzipfile(Filename)
        else:
            os.remove(Filename)

    def _moveFile(self, fn, dirname):
        if os.path.dirname(fn) == dirname:
            return False
        try:
            os.rename(
                fn,
                os.path.join(dirname, os.path.basename(fn))
            )
        except:
            return False
        return True

    def moveFOs(self, FOs, **kwargs):
        # check that a target folder is set
        # if not give a warning and do nothing
        targetDir = self._MovePanel.get(**kwargs)
        if not targetDir:
            self.showInStatusbar("Warning: no target folder set for moving files")
            return None
        # check that the target folder
        # if not give a warning and do nothing
        if not os.path.isdir(targetDir):
            self.showInStatusbar(
                f"Warning: target folder {targetDir} for moving files is not valid"
            )
            return None
        somethingMoved = False
        for fo in FOs:
            filename = fo.fullPath
            checksum = fo.checksum()
            if self._moveFile(filename, targetDir):
                if checksum in self.FODict:
                    del self.FODict[checksum]
                somethingMoved = True
        if somethingMoved:
            self.onChange()
        return somethingMoved

    def deleteFOs(self, FOs, Owner=None):
        if not Owner:
            Owner = self.TopWindow
        somethingDeleted = False
        mustconfirm = self.Cfg.get("confirmdelete")
        onlyOneFO = len(FOs) == 1
        for fo in FOs:
            filename = fo.fullPath
            uniqueFilename = self._filenameUniqueDict[filename]
            checksum = fo.checksum()
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
                if checksum in self.FODict:
                    del self.FODict[checksum]
                somethingDeleted = True
                self._deleteFile(filename)

        if somethingDeleted:
            self.onChange()
        return somethingDeleted

    def deleteSelected(self):
        self.deleteFOs(self._selectedFOs())

    def moveSelected(self):
        self.moveFOs(self._selectedFOs())

    def unselectThumbnails(self, *args):
        for tp in self._TPPositionDict.values():
            tp.select(False)
        self.lastSelectedXY = None

    def toggleSelectAllThumbnails(self, *args):
        isAllSelected = True
        for tp in self._TPPositionDict.values():
            if not tp.selected:
                isAllSelected = False
                break
        if isAllSelected:
            for tp in self._TPPositionDict.values():
                tp.select(False)
        else:
            for tp in self._TPPositionDict.values():
                tp.select(True)

        self.lastSelectedXY = None

    def toggleSelectRow(self, Y, value):
        for tp in self._TPPositionDict.values():
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
        toXY = (X, Y)
        if gridXYLargerOrEqual(fromXY, toXY):
            fromXY, toXY = toXY, fromXY

        for tp in self._TPPositionDict.values():
            if (
                    gridXYLargerOrEqual((tp.X, tp.Y), fromXY) and
                    gridXYLargerOrEqual(toXY, (tp.X, tp.Y))
            ):
                tp.select(True)

    # some routines related to expensive calculations done in a
    # multiprocessing pool
    @tellstatus(msg="Calculating File Hash values, please be patient")
    def _getChecksums(self):
        self._checksumFilenameDict = POOL.getChecksums(self._fileList, self._checksumFilenameDict)
        self._filenameChecksumDict = dict(map(reversed, self._checksumFilenameDict.items()))

    @tellstatus(msg="Making file thumbnails, please be patient")
    def _setThumbnails(self):
        checksumThumbDict = POOL.getThumbnails(
            self.FODict,
            Thumbsize=self.Cfg.get("thumbnailsize"),
            channel=self.Cfg.get("channeltoshow"),
            upscale=self.Cfg.get("upscalethumbnails"),
        )
        self.showInStatusbar("...")
        if not checksumThumbDict:
            return
        for checksum, thumb in checksumThumbDict.items():
            if not thumb:
                del self.FODict[checksum]
                continue

            try:
                pimage = ImageTk.PhotoImage(thumb)
            except:
                del self.FODict[checksum]
                continue

            fo = self.FODict[checksum]
            for afo in fo:
                afo._thumbnail = pimage

    @longrunning
    @tellstatus(msg="Calculating Image Hash values, please be patient")
    def setHashes(self, hashName=None):
        POOL.getHashes(self.FODict, hashName, self._DBConnection)
