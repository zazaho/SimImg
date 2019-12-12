''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich (click on the name label)
    A switch to make this criterion obligatory (must match)
    A method to do something when _somethingChanged
    A method to determine which imagepairs from a list of pairs match
'''
import statistics as stats
import tkinter as tk
from tkinter import ttk
import classes.textscale as TS

class ConditionFrame(tk.Frame):
    name = ''
    " A frame that holds one selection criterion with options"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)

        # keep a handle of the controller object
        self.Ctrl = Controller

        self.config(borderwidth=1,relief="sunken")

        self.label = None
        self.active = False
        self.mustMatch = tk.BooleanVar()

        self.currentConfig = {}
        self.currentMatchingGroups = []
        
        self._makeBaseWidgets()
        self.setActive(False)
        self._candidates = {}
        
    def _makeBaseWidgets(self):
        self.label = tk.Label(self, text=self.name, anchor='w')
        self.label.bind('<Button-1>', self._activeToggled)
        self.mustMatchToggle = tk.Checkbutton(self,
                                              text="Must Match",
                                              anchor='w',
                                              variable=self.mustMatch,
                                              command=self._mustMatchToggled
        )

        self.childWidgets = [self.mustMatchToggle]
        self.label.pack(fill='x')
        self.mustMatchToggle.pack(fill='x')

    def setActive(self, value):
        self.active = value
        if self.active:
            self.config(relief="raised")
            for widget in self.childWidgets:
                widget.config(state=tk.NORMAL)
        else:
            self.config(relief="sunken")
            for widget in self.childWidgets:
                widget.config(state=tk.DISABLED)
                
    def _activeToggled(self,event):
        self.setActive(not self.active)
        self._somethingChanged()
        
    def _mustMatchToggled(self):
        self._somethingChanged()

    def _somethingChanged(self, *args):
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
        self.limitVar.set(self.limit)
        self.currentConfig = {'method':'', 'limit':0}
        self.currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self.setActive(False)
        
    def _makeAdditionalWidgets(self):
        self.Combo = ttk.Combobox(
            self,
            values=["ahash","dhash","phash","whash"],
            state=tk.DISABLED,
            width=8,
        )
        self.Combo.set(self.method)
        self.Combo.bind("<<ComboboxSelected>>", self._somethingChanged)
        self.Scale = tk.Scale(self,
                              from_= 1, to=50,
                              label='Limit',
                              variable=self.limitVar,
                              orient=tk.HORIZONTAL
        )
        self.Scale.bind("<ButtonRelease-1>", self._somethingChanged)
        self.Combo.pack()
        self.Scale.pack()
        self.childWidgets.extend([self.Combo, self.Scale])
        
    def _somethingChanged(self, *args):
        self.method = self.Combo.get()
        self.limit = self.limitVar.get()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b):
            foa = self.Ctrl.FODict[md5a][0]
            if not self.method in foa.hashDict:
                print('Warning: requested a hash that is not available')
                return False
            foaHash = foa.hashDict[self.method]
            fob = self.Ctrl.FODict[md5b][0]
            if not self.method in fob.hashDict:
                print('Warning: requested a hash that is not available')
                return False
            fobHash = fob.hashDict[self.method]
            return abs(foaHash - fobHash) <= self.limit

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self._candidates == set(candidates) and
                self.method == self.currentConfig['method'] and
                self.limit == self.currentConfig['limit']
        ):
            return self.currentMatchingGroups

        self._candidates = set(candidates)
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
        self.limitVar.set(self.limit)
        self.currentConfig = {'method':'', 'limit':-1}
        self.currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self.setActive(False)

    def _makeAdditionalWidgets(self):
        self.Combo = ttk.Combobox(
            self,
            values=["hsvhash","hsv5hash"],
            state=tk.DISABLED,
            width=8,
        )
        self.Combo.set(self.method)
        self.Combo.bind("<<ComboboxSelected>>", self._somethingChanged)
        self.Scale = tk.Scale(self,
                              from_= 1, to=50,
                              label='Limit',
                              variable=self.limitVar,
                              orient=tk.HORIZONTAL
        )
        self.Scale.bind("<ButtonRelease-1>", self._somethingChanged)
        self.Combo.pack()
        self.Scale.pack()
        self.childWidgets.extend([self.Combo, self.Scale])

    def _somethingChanged(self, *args):
        self.method = self.Combo.get()
        self.limit = self.limitVar.get()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b):
            foa = self.Ctrl.FODict[md5a][0]
            if not self.method in foa.hashDict:
                print('Warning: requested a hash that is not available')
                return False
            foaHash = foa.hashDict[self.method]
            fob = self.Ctrl.FODict[md5b][0]
            if not self.method in fob.hashDict:
                print('Warning: requested a hash that is not available')
                return False
            fobHash = fob.hashDict[self.method]
            return stats.mean(
                [abs(foaHash[i]-fobHash[i]) for i,_ in enumerate(foaHash)]
            )/2.56 <= self.limit

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self._candidates == set(candidates) and
                self.method == self.currentConfig['method'] and
                self.limit == self.currentConfig['limit']
        ):
            return self.currentMatchingGroups

        self._candidates = set(candidates)
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
        self._makeAdditionalWidgets()
        self.setActive(False)

    def _makeAdditionalWidgets(self):
        self.missingMatchesCheck = tk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self.missingVar,
            command=self._somethingChanged,
            anchor='w'
        )
        self.missingMatchesCheck.pack()
        self.childWidgets.extend([self.missingMatchesCheck])

    def _somethingChanged(self, *args):
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
                self._candidates == set(candidates) and
                self.missing == self.currentConfig['missingmatches']
        ):
            return self.currentMatchingGroups

        self._candidates = set(candidates)
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
        
        self.initialIndex = 1
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
        self.timeDifferenceInSec = self.scaleSeconds[self.scalelabels[self.initialIndex]]

        self.currentConfig = {'missingmatches':None, 'timedifference':''}
        self.currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self.setActive(False)

    def _makeAdditionalWidgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingVar,
                                                  command=self._somethingChanged,
                                                  anchor='w')
        self.missingMatchesCheck.pack()
        self.timeDifferenceScale = TS.TextScale(self,
                                                textLabels=self.scalelabels,
                                                topLabel='Maximum Difference',
                                                initialInt=self.initialIndex,
                                                onChange=self._somethingChanged,
                                                orient=tk.HORIZONTAL
        )
        self.timeDifferenceScale.pack()
        self.childWidgets.extend([self.missingMatchesCheck, self.timeDifferenceScale])

    def _somethingChanged(self, *args):
        self.missing = self.missingVar.get()
        self.timeDifferenceInSec = self.scaleSeconds[self.timeDifferenceScale.textValue]
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        ''' make groups of images that have the their date close enough together,
        Optionally include the images without info about date as a match to all.
        '''
        def theymatch(md5a, md5b):
            # deal with missings:
            datetime_a = self.Ctrl.FODict[md5a][0].DateTime()
            datetime_b = self.Ctrl.FODict[md5b][0].DateTime()
            if datetime_a == 'Missing':
                return False
            if datetime_b == 'Missing':
                return self.missing
            if abs((datetime_a - datetime_b).total_seconds()) <= self.timeDifferenceInSec:
                return True
            return False

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self._candidates == set(candidates) and
                self.missing == self.currentConfig['missingmatches'] and
                self.timeDifferenceInSec == self.currentConfig['timedifference']
        ):
            return self.currentMatchingGroups

        self._candidates = set(candidates)
        self.currentConfig['missingmatches'] = self.missing
        self.currentConfig['timedifference'] = self.timeDifferenceInSec

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
            dummy.extend([md5b for md5a, md5b in matches if md5a == thismd5])
            dummy = list(set(dummy))
            dummy.sort()
            self.currentMatchingGroups.append(dummy)

        self.currentMatchingGroups.sort()
        return self.currentMatchingGroups
