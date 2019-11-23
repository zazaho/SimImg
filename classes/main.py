''' Main Window of SimImg program '''
# import sys
import os
import glob
# # import hashlib
# import sqlite3
# from multiprocessing import Pool
import tkinter as tk
#from tkinter import ttk
#from PIL import ImageTk, Image
import classes.fileobject as FO
import classes.imageframe as IF
import classes.conditionmodules as CM
import utils.jumbling as JU
import utils.hashing as HA
import utils.database as DB
import utils.filecomparison as FC


class simim_app(tk.Tk):
    ''' Main window for sorting and managing pictures'''

    def __init__(self, arguments=None, *args, **kwargs):
        # do what any TK app does
        super().__init__()

        # for parsing the input arguments
        self.arguments = arguments
        self.doRecurse = True

        ## this will hold the handle of the md5,hashtype, hashvalue database
        self.DATABASENAME = os.path.expanduser('~/.config/SimImg/SimImg.db')
        self.HashDBConnection = None

        self.ImageFileObjectDict = None

        self.ModulePane = SelectionPaneFrame(self)
        self.ThumbPane = ThumbPaneFrame(self)
        self.ModulePane.pack(side=tk.LEFT)
        self.ThumbPane.pack(side=tk.RIGHT)
        
        self.createfileobjects()
        #self.showinitialthumbnails()

        for fo in self.ImageFileObjectDict.values():
            print(fo[0].CameraMake(), fo[0].CameraModel())

        self.connectdatabase()
        HA.GetImageHashes(self.ImageFileObjectDict, 'phash', db_connection=self.HashDBConnection)
        distances = FC.HashDistances(self.ImageFileObjectDict,'phash')

        ImgObj1 = self.ImageFileObjectDict[distances[0][0]][0]
        ImgObj1.ThumbFrame.grid_forget()
        ImgObj1.ThumbFrame.grid(column=1,row=1)
        ImgObj2 = self.ImageFileObjectDict[distances[0][1]][0]
        ImgObj2.ThumbFrame.grid_forget()
        ImgObj2.ThumbFrame.grid(column=2,row=1)

        ImgObj3 = self.ImageFileObjectDict[distances[3][0]][0]
        ImgObj4 = self.ImageFileObjectDict[distances[3][1]][0]
        ImgObj3.ThumbFrame.grid(column=1,row=2)
        ImgObj4.ThumbFrame.grid(column=2,row=2)

        ImgObj5 = self.ImageFileObjectDict[distances[9][0]][0]
        ImgObj6 = self.ImageFileObjectDict[distances[9][1]][0]
        ImgObj5.ThumbFrame.grid(column=1,row=3)
        ImgObj6.ThumbFrame.grid(column=2,row=3)

        thiscm1 = CM.HashCondition(self.ModulePane)
        thiscm1.pack(side=tk.TOP)
        thiscm2 = CM.CameraCondition(self.ModulePane)
        thiscm2.pack(side=tk.TOP)
        thiscm3 = CM.DateCondition(self.ModulePane)
        thiscm3.pack(side=tk.TOP)

    def createfileobjects(self):

        ## create candidate file list
        ##  arguments: files/dirs
        ## in dirs default recurse?
        AllFilePaths = self.AllFilesFromArgs()
        if not AllFilePaths:
            print("No files found")
            exit()

        ## Make list of image file objects with all files the installed PIL can read
        ImageFileObjectList = []
        for FilePath in AllFilePaths:
            ThisFileObject = FO.FileObject(self, FullPath = FilePath)
            if ThisFileObject.IsImage():
                ImageFileObjectList.append(ThisFileObject)
                # create an associated imageframe
                ThisImageFrame = IF.ImageFrame(self.ThumbPane)
                #make that the two object know about each-other
                ThisImageFrame.FileObject = ThisFileObject
                ThisFileObject.ThumbFrame = ThisImageFrame
                #do md5 hash and thumbnails
                ThisFileObject.md5()
                ThisFileObject.MakeThumbnail()
                
        if not ImageFileObjectList:
            print("No Files containing images found")
            exit()

        # transform into a dict based on uniq md5
        self.ImageFileObjectDict = JU.PairListToDict( [ (i.md5(), i) for i in ImageFileObjectList ] )
        
    def connectdatabase(self):
        self.HashDBConnection = DB.CreateDBConnection(self.DATABASENAME)
        if not self.HashDBConnection:
            sys.exit(1)
            
        if not DB.CreateDBTables(self.HashDBConnection):
            sys.exit(1)

    def disconnectdatabase(self):
        pass
        
        '''Upon starting the window
        we show the images
        we set some default selection options
        we show the selection panel
        we build the menu
        
        start hashing
        find matches
        update window with hased and selection
        '''
    def showinitialthumbnails(self):
        UniqFileObjects = [folist[0] for folist in self.ImageFileObjectDict.values()]
        for idx, ImgObj in enumerate(UniqFileObjects[:self.nx_grid*self.ny_grid]):
            this_x = idx % self.nx_grid
            this_y = idx // self.nx_grid
            ImgObj.ThumbFrameHidden = False
            ImgObj.ThumbFramePosition = (this_x,this_y)
            ImgObj.ThumbFrame.grid(column=this_x,row=this_y)

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

    def AllFilesFromArgs(self):
        ''' find all files using the command line arguments '''

        candidates = []
        for arg in self.arguments:
            if os.path.isdir(arg):
                candidates.extend(glob.glob(arg+'/**', recursive=self.doRecurse))
            else:
                candidates.append(arg)

        filelist = [c for c in candidates if os.path.isfile(c)]
        return filelist

class ThumbPaneFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # do what any TK Frame does
        super().__init__(*args, **kwargs)
        # keep a trace of the top-level
        self.App = parent
        #how many thumbnails (should be options not hardcoded)
        self.nx_grid = 5
        self.ny_grid = 4
        self.GridSize = (self.nx_grid+1,self.ny_grid+1)
        self.ThumbImageSize = (150, 150)
        self.ThumbBorderWidth = 3


class SelectionPaneFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # do what any TK Frame does
        super().__init__(*args, **kwargs)
        # keep a trace of the top-level
        self.App = parent
