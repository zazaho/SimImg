''' Controller module:
The main gateway between the information containted in the database,
the fileinfo objects and the display.
 '''
import sys
import os
import glob
import itertools
import tkinter as tk
import classes.fileobject as FO
import classes.imageframe as IF
import classes.toolbar as TB
import classes.conditionmodules as CM
import utils.jumbling as JU
import utils.database as DB
import utils.hashing as HA

# Upon starting the window
# we show the images
# we set some default selection options
# we show the selection panel
# we build the menu

# start hashing
# find matches
# update window with hased and selection


class Controller():
    'Controller object that initializes the program and reacts to events.'
    def __init__(self, parent, *args, **kwargs):

        # default values of
        self.TopWindow = parent
        # a dict of configuration values
        self.Cfg = parent.Cfg
        self.Statusbar = parent.Statusbar
        self.DBConnection = None

        self.fileList = []
        self.FODict = {}
        self.TPDict = {}
        self.CMList = []
        self.TPPositionDict = {}
        self.activeMD5s = []
        self.activePairs = []
        self.MD5HashesDict = {}
        # this variable keeps track of whether the thumbs have changed
        # since the last time the groups were calculated
        # initially true since groups are not yet calclulated
        self.thumbListChanged = True

        # put the toolbar in the self.TopWindow.ModulePane
        self.Toolbar = TB.Toolbar(self.TopWindow.ModulePane, Controller=self)
        self.Toolbar.pack(side=tk.TOP, fill='x')

        # put the condition modules in the self.TopWindow.ModulePane
        self.createConditionModules()
        for cm in self.CMList:
            cm.pack(side=tk.TOP, fill='x')

        # get the files from the commandline
        self.getFileList()
        if not self.fileList:
            print("No files found")
            sys.exit()

        # calculate md5s in multiprocessing
        self.getMD5Hashes()
        
        self.createFileobjects()
        if not self.FODict:
            print("No Files containing images found")
            sys.exit()

        self.getActiveMD5s()
        self.startDatabase()
        
    def startDatabase(self):
        self.DBConnection = DB.CreateDBConnection(self.Cfg.get('DATABASENAME'))
        if not self.DBConnection:
            sys.exit(1)

        if not DB.CreateDBTables(self.DBConnection):
            sys.exit(1)

    def stopDatabase(self):
        pass

    def getFileList(self):
        candidates = []
        doRecurse = self.Cfg.get('doRecurse')
        for arg in self.Cfg.get('CmdLineArguments'):
            if os.path.isdir(arg):
                candidates.extend(glob.glob(arg+'/**', recursive=doRecurse))
            else:
                candidates.append(arg)

        self.fileList = [c for c in candidates if os.path.isfile(c)]

    def createFileobjects(self):
        # Make list of image file objects with all files the installed PIL can read
        ImageFileObjectList = []
        serial=1
        for FilePath in self.fileList:
            ThisFileObject = FO.FileObject(self,
                                           FullPath=FilePath,
                                           MD5HashesDict=self.MD5HashesDict,
                                           serial=serial
            )
            serial += 1
            if ThisFileObject.IsImage():
                ImageFileObjectList.append(ThisFileObject)
                # do md5 hash and thumbnails
                ThisFileObject.md5()

        if not ImageFileObjectList:
            return
        # transform into a dict based on uniq md5
        self.FODict = JU.PairListToDict(
            [(i.md5(), i) for i in ImageFileObjectList]
        )

    def createConditionModules(self):
        self.CMList = [
            CM.HashCondition(self.TopWindow.ModulePane, Controller=self),
            CM.HSVCondition(self.TopWindow.ModulePane, Controller=self),
            CM.DateCondition(self.TopWindow.ModulePane, Controller=self),
            CM.CameraCondition(self.TopWindow.ModulePane, Controller=self)
        ]

    def createInitialView(self):
        'Create the initial display'
        self.removeAllThumbs()

        # because there are no criteria yet display thumbnails in order
        nx = self.Cfg.get('nx_grid')
        ny = self.Cfg.get('ny_grid')
        # maximum nx*ny thumbs to show
        thumbToShow = 0
        for md5 in self.FODict.keys():
            if not self.FODict[md5][0].Active:
                continue
            X = thumbToShow % nx
            Y = thumbToShow // nx
            self.showThumbXY(md5, X, Y)
            thumbToShow += 1
            # if thumbToShow >= nx*ny:
            #     break
        
    def ThumbXY(self, X, Y):
        if (X,Y) in self.TPPositionDict:
            return self.TPPositionDict[(X,Y)]
        else:
            return None

    def showThumbXY(self, md5, X, Y):
        # make sure that if a thumb is currently shown it is removed
        # and deleted
        self.removeThumbXY(X,Y)
        # create a new thumbnail
        ThisThumb = IF.ImageFrame(
            self.TopWindow.ThumbPane.viewPort,
            Ctrl=self,
            md5=md5
        )
        # show the new one
        ThisThumb.grid(column=X, row=Y)
        # add thisthumb to the TPPositionDict
        self.TPPositionDict[(X, Y)] = ThisThumb


    def removeThumbXY(self, X, Y):
        ThisThumb = self.ThumbXY(X, Y)
        if ThisThumb:
            del self.TPPositionDict[(X, Y)]
            ThisThumb.destroy()


    def removeAllThumbs(self):
        for ThisThumb in self.TPPositionDict.values():
            ThisThumb.destroy()
        self.TPPositionDict = {}

    def getActiveMD5s(self):
        self.activeMD5s = [md5 for md5, FO in self.FODict.items() if FO[0].Active]
        # keep the list sorted
        self.activeMD5s.sort()
        
    def getActivePairs(self):
        self.activePairs = list(itertools.combinations(self.activeMD5s,2))
        # keep the list sorted
        self.activePairs.sort()
        
    def md52serial(self, nestedMD5List):
        nestedSerialList = []
        for m in nestedMD5List:
            if isinstance(m, list):
                s = self.md52serial(m)
            else:
                s = self.FODict[m][0].serial
            nestedSerialList.append(s)
        return nestedSerialList


    def getMatchingGroups(self):
        ''' given the matching groups returned by each active condition module
           make a master list of image groups '''

        matchingGroupsList = []
        MMMatchingGroupsList = []
        for cm in self.CMList:
            if not cm.active:
                continue
            thisMatchingGroups = cm.matchingGroups(self.activePairs)
            matchingGroupsList.append(thisMatchingGroups)
            if cm.mustMatch.get():
                MMMatchingGroupsList.append(thisMatchingGroups)

        # nothing activated. Start-over
        if not matchingGroupsList:
            self.createInitialView()
            return

        matchingGroups = JU.mergeGroupLists(matchingGroupsList)

        if MMMatchingGroupsList:
            matchingGroups = JU.applyMMGroupLists(matchingGroups, MMMatchingGroupsList)

        if not matchingGroups:
            return

        # remove "groups" of only one image
        matchingGroups = [mg for mg in matchingGroups if len(mg) > 1]

        if not matchingGroups:
            return

        matchingGroups.sort()
        uniqueMatchingGroups = []
        for MG in matchingGroups:
            if not JU.existsAsSubGroup(MG, uniqueMatchingGroups):
                uniqueMatchingGroups.append(MG)

        self.matchingGroups = uniqueMatchingGroups
        self.matchingGroups.sort()

    def displayMatchingGroups(self):
        for Y, group in enumerate(self.matchingGroups):
            for X, md5 in enumerate(group):
                self.showThumbXY(md5, X, Y)

    def onConditionChanged(self):
        # put everything to default
        self.activeMD5s = None
        self.activePairs = None
        self.matchingPairs = None
        self.matchingGroups = None

        self.getActiveMD5s()
        if not self.activeMD5s:
            return

        self.getActivePairs()
        if not self.activePairs:
            return

        # make sure to clean the interface
        self.removeAllThumbs()

        self.getMatchingGroups()
        self.thumbListChanged = False
        if not self.matchingGroups:
            return

        self.displayMatchingGroups()

    def onThumbnailChanged(self):
        self.thumbListChanged = True
        self.onConditionChanged()

    def selectedFOs(self):
        lst = []
        for tp in self.TPPositionDict.values():
            if tp.selected:
                lst.extend(self.FODict[tp.md5])
        return lst
        
    def hideSelected(self):
        for fo in self.selectedFOs():
            fo.Active = False
        self.onThumbnailChanged()

    def getMD5Hashes(self):
        self.MD5HashesDict = HA.GetMD5Hashes(self.fileList)

    def setImageHashes(self, hashName="ahash"):
        self.Statusbar.config(text="Calculating Images Hashes, please be patient")
        HA.GetImageHashes(self.FODict, hashName, self.DBConnection)
        self.Statusbar.config(text="...")
