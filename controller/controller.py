# all_image_files = image_filename_list()
# files1, files2, sims = image_similarity(all_image_files)

# # file1 where the maximum occurred
# _, file1_max = max(zip(sims,files1))

# frame = ImageFrame(self)
# frame.grid(row=0,column=0)
# frame.thumb_load_image(file1_max)
# top4_files2 = images_most_similar_to(file1_max,files1,files2,sims,4)
# files1,files2,sims = remove_file_from_list(file1_max,files1,files2,sims)

# for idx,f in enumerate(top4_files2):
#     frame = ImageFrame(self)
#     frame.grid(row=0,column=idx+1)
#     frame.thumb_load_image(f)
#     add_top4_files2 = images_most_similar_to(f,files1,files2,sims,3)
#     files1,files2,sims = remove_file_from_list(f,files1,files2,sims)
#     for add_idx,add_f, in enumerate(add_top4_files2):
#         frame = ImageFrame(self)
#         frame.grid(row=add_idx+1,column=idx+1)
#         frame.thumb_load_image(add_f)
#         files1,files2,sims = remove_file_from_list(add_f,files1,files2,sims)

import sys
import os
import glob
import itertools
import tkinter as tk
import classes.fileobject as FO
import classes.imageframe as IF
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
    'Controller object that initializes the program and reacts to events from widgets.'
    def __init__(self, parent, *args, **kwargs):

        self.TopWindow = parent
        # a dict of configuration values
        self.Cfg = parent.Cfg
        self.DBConnection = None

        self.fileList = []
        self.FODict = {}
        self.TPDict = {}
        self.CMList = []
        self.TPPositionDict = {}
        self.activeMD5s = []
        self.activePairs = []
        self.activeGroups = []
        
        self.getFileList()
        if not self.fileList:
            print("No files found")
            sys.exit()

        self.createFileobjects()
        if not self.FODict:
            print("No Files containing images found")
            sys.exit()

        self.getActiveMD5s()
        self.createConditionModules()
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
        for FilePath in self.fileList:
            ThisFileObject = FO.FileObject(self, FullPath=FilePath)
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
            CM.CameraCondition(self.TopWindow.ModulePane, Controller=self),
            CM.DateCondition(self.TopWindow.ModulePane, Controller=self)
        ]

    def createInitialView(self):
        'Create the initial display'
        # put the condition modules in the self.TopWindow.ModulePane
        for cm in self.CMList:
            cm.pack(side=tk.TOP)

        # because there are no criteria yet display thumbnails in order
        nx = self.Cfg.get('nx_grid')
        ny = self.Cfg.get('ny_grid')
        # maximum nx*ny thumbs to show
        thumbToShow = 0
        for md5 in self.FODict.keys():
            X = thumbToShow % nx
            Y = thumbToShow // nx
            self.showThumbXY(md5, X, Y)
            thumbToShow += 1
            if thumbToShow >= nx*ny:
                break

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
            self.TopWindow.ThumbPane,
            Ctrl=self,
            md5=md5
        )
        # show the new one
        ThisThumb.grid(column=X, row=Y)
        # add thisthumb to the TPPositionDict
        self.TPPositionDict[(X,Y)] = ThisThumb
        
    def removeThumbXY(self,X,Y):
        ThisThumb = self.ThumbXY(X,Y)
        if ThisThumb:
            del self.TPPositionDict[(X,Y)]
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

    def getMatchingPairs(self):
        'Pairs of images (mds) that fulfil the current conditions'
        # give the active pairs to each active condition module
        # the modules will return a list of pairs that match
        # results will be combined to make a list that fulfils all criteria

        # we keep track of matches en must-matches
        matchingPairListList = []
        obligatoryMatchingPairListList = []
        for CM in self.CMList:
            if not CM.active:
                continue

            thisMatchingPairList = CM.matchingPairs(self.activePairs)
            matchingPairListList.append(thisMatchingPairList)
            if CM.mustMatch:
                    obligatoryMatchingPairListList.append(thisMatchingPairList)


        # the lists are combined by union
        # this yields all pairs that match at least one condition
        finalList = []
        for MPList in matchingPairListList:
            finalList = set(finalList) | set(MPList)

        # the obligatory list are combined by intersection
        # this keeps only those pairs that match all must-match conditions
        for MPList in obligatoryMatchingPairListList:
            finalList = set(finalList) & set(MPList)

        self.matchingPairs = list(finalList)
        # keep the list sorted
        self.matchingPairs.sort()

    def getMatchingGroups(self):
        ' given the matching pairs, make matching groups'
        # the logic is to make for each md5A (pmd5) in the self.matchingPairs (md5A, md5B)
        # a list of all other md5B (omd5s) that match pmd5.
        # we keep each group (pmd5,omd5s) unless it exists in its entirety as a sublist already
        # we exploit the fact that the matchingpairlist is sorted.
        # As a result in the list of group candidates
        # any group will never be fully contained later on in the list:
        # when we process the candidate groups in order
        # we only have to check that is does not yet exist

        def existsAsSubGroup(E,GL):
            for G in GL:
                if set(E) - set(G) == set():
                    return True
            return False

        matchingGroups = []
        pmd5s = list(set([md5A for md5A, md5B in self.matchingPairs]))
        pmd5s.sort()
        for pmd5 in pmd5s:
            omd5s = [md5B for md5A, md5B  in self.matchingPairs if md5A == pmd5]
            omd5s.append(pmd5)
            omd5s.sort()
            matchingGroups.append(omd5s)

        uniqueMatchingGroups = []
        for MG in matchingGroups:
            if not existsAsSubGroup(MG, uniqueMatchingGroups):
                uniqueMatchingGroups.append(MG)

        self.matchingGroups = uniqueMatchingGroups
        self.matchingGroups.sort()

    def displayMatchingGroups(self):
        for Y, group in enumerate(self.matchingGroups):
            for X, md5 in enumerate(group):
                self.showThumbXY(md5, X+1, Y+1)

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

        self.getMatchingPairs()
        if not self.matchingPairs:
            return
        
        self.getMatchingGroups()
        if not self.matchingGroups:
            return

        self.removeAllThumbs()
        self.displayMatchingGroups()

    def onThumbnailChanged(self):
        pass

    def setImageHashes(self, hashName="ahash"):
        HA.GetImageHashes(self.FODict, hashName, self.DBConnection)
