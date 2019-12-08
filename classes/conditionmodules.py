''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich (click on the name label)
    A switch to make this criterion obligatory (must match)
    A method to do something when somethingChanged
    A method to determine which imagepairs from a list of pairs match
'''

import math
import statistics as stats
import tkinter as tk
from tkinter import ttk
from imagehash import hex_to_hash
import classes.textscale as TS
import utils.hashing as HA

class ConditionFrame(tk.Frame):
    name = ''
    " A frame that holds one selection criterion with options"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)

        # keep a handle of the controller object
        self.Ctrl = Controller

        self.config(borderwidth=3,relief="sunken")
        self.width = 150

        self.label = None
        self.active = False
        self.mustMatch = tk.BooleanVar()

        self.currentConfig = {}
        self.currentMatchingGroups = []
        
        self.make_base_widgets()


    def make_base_widgets(self):
        self.label = tk.Label(self, text=self.name, anchor='w')
        self.label.bind('<Button-1>', self.activeToggled)
        self.mustMatchToggle = tk.Checkbutton(self,
                                              text="Must Match",
                                              anchor='w',
                                              variable=self.mustMatch,
                                              command=self.mustMatchToggled
        )

        self.label.pack(fill='x')
        self.mustMatchToggle.pack(fill='x')

    def activeToggled(self,event):
        self.active = not self.active
        if self.active:
            self.config(relief="raised")
        else:
            self.config(relief="sunken")
        self.somethingChanged()
        
    def mustMatchToggled(self):
        self.somethingChanged()

    def somethingChanged(self, *args):
        pass

    def matchingGroups(self, candidates):
        pass


class HashCondition(ConditionFrame):
    name = 'HASHING DISTANCE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.Combo = None
        self.Scale = None
        self.method = "ahash"
        self.limit = 14
        self.limitVar = tk.IntVar()
        self.currentConfig = {'method':'', 'limit':0}
        self.currentMatchingGroups = []
        self.make_additional_widgets()
        
    def make_additional_widgets(self):
        self.Combo = ttk.Combobox(
            self,
            values=["ahash","dhash","phash","whash"],
            width=8,
        )
        self.Combo.set(self.method)
        self.Combo.bind("<<ComboboxSelected>>", self.somethingChanged)
        self.Scale = tk.Scale(self,
                              from_= 1, to=50,
                              label='Limit',
                              variable=self.limitVar,
                              orient=tk.HORIZONTAL
        )
        self.Scale.bind("<ButtonRelease-1>", self.somethingChanged)
        self.Scale.set(self.limit)
        self.Combo.pack()
        self.Scale.pack()

    def somethingChanged(self, *args):
        self.method = self.Combo.get()
        self.limit = self.limitVar.get()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b):
            foaHash = getattr(self.Ctrl.FODict[md5a][0], self.method)
            fobHash = getattr(self.Ctrl.FODict[md5b][0], self.method)
            return abs(foaHash - fobHash) <= self.limit

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self.Ctrl.thumbListChanged == False and
                self.method == self.currentConfig['method'] and
                self.limit == self.currentConfig['limit']
        ):
            return self.currentMatchingGroups

        self.currentConfig['method'] = self.method
        self.currentConfig['limit'] = self.limit
        
        #Call this to make sure the hash values for this method are available
        self.Ctrl.setImageHashes(hashName=self.method)

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        self.currentMatchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            self.currentMatchingGroups.append(dummy)

        self.currentMatchingGroups.sort()
        return self.currentMatchingGroups

class HSVCondition(ConditionFrame):
    name = 'COLOR DISTANCE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.Combo = None
        self.Scale = None
        self.method = "hsvhash"
        self.limit = 10
        self.limitVar = tk.IntVar()
        self.currentConfig = {'method':'', 'limit':-1}
        self.currentMatchingGroups = []
        self.make_additional_widgets()
        
    def make_additional_widgets(self):
        self.Combo = ttk.Combobox(
            self,
            values=["hsvhash","hsv5hash"],
            width=8,
        )
        self.Combo.set(self.method)
        self.Combo.bind("<<ComboboxSelected>>", self.somethingChanged)
        self.Scale = tk.Scale(self,
                              from_= 1, to=50,
                              label='Limit',
                              variable=self.limitVar,
                              orient=tk.HORIZONTAL
        )
        self.Scale.bind("<ButtonRelease-1>", self.somethingChanged)
        self.Scale.set(self.limit)
        self.Combo.pack()
        self.Scale.pack()

    def somethingChanged(self, *args):
        self.method = self.Combo.get()
        self.limit = self.limitVar.get()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b):
            foaHash = getattr(self.Ctrl.FODict[md5a][0], self.method)
            fobHash = getattr(self.Ctrl.FODict[md5b][0], self.method)
            #return sum(abs(foaHash-fobHash))/256.*100./len(foaHash) <= self.limit
            return stats.mean(
                [abs(foaHash[i]-fobHash[i]) for i,_ in enumerate(foaHash)]
            )/2.56 <= self.limit

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self.Ctrl.thumbListChanged == False and
                self.method == self.currentConfig['method'] and
                self.limit == self.currentConfig['limit']
        ):
            return self.currentMatchingGroups

        self.currentConfig['method'] = self.method
        self.currentConfig['limit'] = self.limit
        
        #Call this to make sure the hash values for this method are available
        self.Ctrl.setImageHashes(hashName=self.method)

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        self.currentMatchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            self.currentMatchingGroups.append(dummy)

        self.currentMatchingGroups.sort()
        return self.currentMatchingGroups

class CameraCondition(ConditionFrame):
    name = 'SAME CAMERA'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingMatchesCheck = None
        self.missingVar = tk.BooleanVar()
        self.missing = False
        self.currentConfig = {'missingmatches':None}
        self.currentMatchingGroups = []
        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self.missingVar,
            command=self.somethingChanged,
            anchor='w'
        )
        self.missingMatchesCheck.pack()

    def somethingChanged(self, *args):
        self.missing = self.missingVar.get()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        ''' make groups of images that have the same camera model
        Optionally include the images without info about cameras as a match all
        '''
        def theymatch(md5a, md5b):
            if self.Ctrl.FODict[md5a][0].CameraModel() == '':
                return False
            if self.Ctrl.FODict[md5a][0].CameraModel() == self.Ctrl.FODict[md5b][0].CameraModel():
                return True
            if self.missing and self.Ctrl.FODict[md5b][0].CameraModel() == '':
                return True
            return False

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self.Ctrl.thumbListChanged == False and
                self.missing == self.currentConfig['missingmatches']
        ):
            return self.currentMatchingGroups

        self.currentConfig['missingmatches'] = self.missingVar.get()

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        self.currentMatchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            self.currentMatchingGroups.append(dummy)

        self.currentMatchingGroups.sort()
        return self.currentMatchingGroups

class DateCondition(ConditionFrame):
    name = 'CLOSE IN TIME'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingMatchesCheck = None
        self.missingVar = tk.BooleanVar()
        self.missing = False
        self.timeDifferenceScale = None
        self.timeDifferenceVar = tk.IntVar()
        self.scalelabels = ['1 minute','10 minutes','1 hour','1 day','1 week','4 weeks','1 year']
        self.scaleSeconds = {
            '1 minute':60,
            '10 minutes':600,
            '1 hour':3600,
            '1 day':24*3600,
            '1 week':7*24*3600,
            '4 weeks':4*7*24*3600,
            '1 year':365*24*3600
        }
        self.currentConfig = {'missingmatches':None, 'timedifference':''}
        self.currentMatchingGroups = []
        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingVar,
                                                  command=self.somethingChanged,
                                                  anchor='w')
        self.missingMatchesCheck.pack()
        self.timeDifferenceScale = TS.TextScale(self,
                                                textLabels=self.scalelabels,
                                                label='Maximum Difference', 
                                                command=self.somethingChanged,
                                                variable=self.timeDifferenceVar,
                                                orient=tk.HORIZONTAL)
        self.timeDifferenceVar.set(1)
        self.timeDifferenceScale.TS_Set_Label(1)
        self.timeDifferenceScale.topFrame.pack()

    def somethingChanged(self, *args):
        self.missing = self.missingVar.get()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        ''' make groups of images that have the their date close enough together,
        Optionally include the images without info about date as a match to all.
        '''
        def theymatch(md5a, md5b):
            maxDiff = self.scaleSeconds[self.timeDifferenceScale.textValue]
            # deal with missings:
            datetime_a = self.Ctrl.FODict[md5a][0].DateTime()
            datetime_b = self.Ctrl.FODict[md5b][0].DateTime()
            if datetime_a == 'Missing':
                return False
            if datetime_b == 'Missing':
                return self.missing
            if abs((datetime_a - datetime_b).total_seconds()) <= maxDiff:
                return True
            return False

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self.Ctrl.thumbListChanged == False and
                self.missing == self.currentConfig['missingmatches'] and
                self.timeDifferenceScale.textValue == self.currentConfig['timedifference']
        ):
            return self.currentMatchingGroups

        self.currentConfig['missingmatches'] = self.missing
        self.currentConfig['timedifference'] = self.timeDifferenceScale.textValue

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        self.currentMatchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            self.currentMatchingGroups.append(dummy)

        self.currentMatchingGroups.sort()
        return self.currentMatchingGroups
