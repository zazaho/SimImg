''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active switch (click on the name label)
    A switch to make this criterion obligatory (must match)
    A method to do something when _somethingChanged
    A method to determine which imagepairs from a list of pairs match
'''
import math
import statistics as stats
from operator import add
import itertools
import functools
import tkinter as tk
from tkinter import ttk
from . import customscales as CS
from . import tooltip as TT

class ConditionFrame(ttk.Frame):
    name = ''
    " A frame that holds one selection criterion with options"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)
        self.config(borderwidth=1, relief="sunken")

        # keep a handle of the controller object
        self._Ctrl = Controller
        self.active = False
        self.mustMatch = tk.BooleanVar()

        self._currentConfig = {}
        self._currentMatchingGroups = {}
        self._matchingInfo = []
        self._md5s = {}

        self._label = ttk.Label(self, text=self.name)
        self._label.bind('<Button-1>', self._activeToggled)
        self._label.pack(fill='x')

        self._mustMatchToggle = ttk.Checkbutton(
            self,
            text="Must Match",
            variable=self.mustMatch,
            command=self._somethingChanged
        )
        self._mustMatchToggle.pack(fill='x')
        self._childWidgets = [self._mustMatchToggle]

    def _setActive(self, value):
        self.active = value
        if self.active:
            self.config(relief="raised")
            for widget in self._childWidgets:
                if widget.winfo_class() == 'TCombobox':
                    widget.config(state="readonly")
                else:
                    widget.config(state="normal")
        else:
            self.config(relief="sunken")
            for widget in self._childWidgets:
                widget.config(state="disabled")

    def _activeToggled(self, *args):
        self._setActive(not self.active)
        self._somethingChanged()

    def _somethingChanged(self, *args):
        self._Ctrl.onChange()

    def _updateFromPrevious(self, md5s):
        # check that the md5s or the widget parameters are different from before
        # if not simply return false to indicate that nothing is updated
        foundADifference = (self._md5s != set(md5s))
        for param in self._currentConfig:
            if foundADifference:
                # one difference is enough
                break
            if getattr(self, param) != self._currentConfig[param]:
                foundADifference = True

        if not foundADifference:
            return False

        # store the current values for posterity
        self._md5s = set(md5s)
        for param in self._currentConfig:
            self._currentConfig[param] = getattr(self, param)
        return True

    def _theymatch(self, md5a, md5b):
        pass

    def _preMatching(self):
        pass
    
    def _postMatching(self):
        pass
    
    def _getMatchingGroups(self):
        cand = list(itertools.combinations(self._md5s,2))
        matches = [(a, b) for a, b in cand if self._theymatch(a, b)]
        # make a dict with for each md5 that has matches the set of md5s that matches
        # we include the md5 itself
        matchingGroupsDict = {}
        for a, b in matches:
            if not a in matchingGroupsDict:
                matchingGroupsDict[a] = {a}
            matchingGroupsDict[a].add(b)
            if not b in matchingGroupsDict:
                matchingGroupsDict[b] = {b}
            matchingGroupsDict[b].add(a)
        self._currentMatchingGroups = matchingGroupsDict

    def matchingGroups(self, md5s):
        #if nothing changed _updateFromPrevious will return False
        if not self._updateFromPrevious(md5s):
            return self._currentMatchingGroups
        self._preMatching()
        self._getMatchingGroups()
        self._postMatching()
        return self._currentMatchingGroups

    # this is a trick to make sure that ctrl-a works on the thumbnails
    # even if the Scale has foocus
    def _doSelectAll(self, *args):
        self._Ctrl.selectAllThumbnails()
        return "break"

class GradientCondition(ConditionFrame):
    name = 'GRADIENTS'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.method = "Horizontal"
        self.limit = 14

        self._Combo = None
        self._Scale = None
        self._ScaleTip = None
        self._limitVar = tk.IntVar()
        self._limitVar.set(self.limit)
        self._currentConfig = {'method':'', 'limit':-1}
        self._makeAdditionalWidgets()
        self._setActive(False)

    def _makeAdditionalWidgets(self):
        self._Combo = ttk.Combobox(
            self,
            values=["Horizontal", "Vertical"],
            width=15,
            state="readonly",
        )
        self._Combo.set(self.method)
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Scale = CS.DelayedScale(self,
                                      from_= 1, to=50,
                                      variable=self._limitVar,
                                      takefocus=1,
                                      command=self._scaleChanged,
                                      orient="horizontal",
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._ScaleTip = TT.Tooltip(self._Scale, text='')
        self._Combo.pack()
        self._Scale.pack()
        self._childWidgets.extend([self._Combo, self._Scale])

    def _comboChanged(self, *args):
        self.method = self._Combo.get()
        self._Combo.focus_set()
        self._somethingChanged()

    def _scaleChanged(self, *args):
        self.limit = self._limitVar.get()
        self._Scale.focus_set()
        self._somethingChanged()

    def _preMatching(self):
        # Call this to make sure the hash values for this method are available
        self._Ctrl.setImageHashes(hashName=self.method)
        self._matchingInfo = []

    def _postMatching(self):
        if not self._matchingInfo:
            self._ScaleTip.text = ''
        elif len(self._matchingInfo) < 10:
            self._ScaleTip.text = 'Min: %d' % (math.ceil(min(self._matchingInfo)))
        else:
            self._matchingInfo.sort()
            self._ScaleTip.text = 'min=%d; >10 pairs=%d' % (math.ceil(min(self._matchingInfo)), math.ceil(self._matchingInfo[9]))

    def _theymatch(self, md5a, md5b):
        hashA = self._Ctrl.FODict[md5a][0].hashDict[self.method]
        hashB = self._Ctrl.FODict[md5b][0].hashDict[self.method]
        dist = functools.reduce(
            add,
            [format(hashA[i]^hashB[i], 'b').count('1') for i in range(len(hashA))]
        )
        self._matchingInfo.append(dist)
        return dist <= self.limit

class ColorCondition(ConditionFrame):
    name = 'COLOR DISTANCE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.method = "HSV (5 regions)"
        self.limit = 10

        self._Combo = None
        self._Scale = None
        self._ScaleTip = None
        self._limitVar = tk.IntVar()
        self._limitVar.set(self.limit)
        self._currentConfig = {'method':'', 'limit':-1}
        self._makeAdditionalWidgets()
        self._setActive(False)

    def _makeAdditionalWidgets(self):
        self._Combo = ttk.Combobox(
            self,
            values=["HSV", "HSV (5 regions)","RGB", "RGB (5 regions)", "Luminosity", "Luminosity (5 regions)"],
            width=15,
            state="readonly",
        )
        self._Combo.set(self.method)
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Scale = CS.DelayedScale(self,
                                      from_= 1, to=50,
                                      variable=self._limitVar,
                                      command=self._scaleChanged,
                                      orient="horizontal"
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._ScaleTip = TT.Tooltip(self._Scale, text='')
        self._Combo.pack()
        self._Scale.pack()
        self._childWidgets.extend([self._Combo, self._Scale])

    def _comboChanged(self, *args):
        self.method = self._Combo.get()
        self._Combo.focus_set()
        self._somethingChanged()

    def _scaleChanged(self, *args):
        self.limit = self._limitVar.get()
        self._Scale.focus_set()
        self._somethingChanged()

    def _preMatching(self):
        # Call this to make sure the hash values for this method are available
        self._Ctrl.setImageHashes(hashName=self.method)
        self._matchingInfo = []

    def _postMatching(self):
        if not self._matchingInfo:
            self._ScaleTip.text = ''
        elif len(self._matchingInfo) < 10:
            self._ScaleTip.text = 'Min: %d' % (math.ceil(min(self._matchingInfo)))
        else:
            self._matchingInfo.sort()
            self._ScaleTip.text = 'min=%d; >10 pairs=%d' % (math.ceil(min(self._matchingInfo)), math.ceil(self._matchingInfo[9]))

    def _theymatch(self, md5a, md5b):
        hashA = self._Ctrl.FODict[md5a][0].hashDict[self.method]
        hashB = self._Ctrl.FODict[md5b][0].hashDict[self.method]
        # we need to take care of the median hue value (0, 6, .. th element)
        # when calculating distance because this is a measure that wraps at 255
        # back to 0 the correct distance is the minimum of (h1-h2) % 255 and (h2-h1) % 255
        # in all other cases use abs(v1 -v2)
        if self.method in ['HSV', 'HSV (5 regions)']:
            distArr = [
                abs(hashA[i]-hashB[i]) if i % 6
                else min((hashA[i]-hashB[i]) % 255, (hashB[i]-hashA[i]) % 255)
                for i in range(len(hashA))
            ]
        else:
            distArr = [abs(hashA[i]-hashB[i]) for i in range(len(hashA))]
        val = stats.mean(distArr)
        self._matchingInfo.append(val)
        return val <= self.limit

class CameraCondition(ConditionFrame):
    name = 'CAMERA MODEL'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingmatches = False

        self._missingMatchesCheck = None
        self._missingVar = tk.BooleanVar()
        self._Scale = None
        self._initialIndex = 0
        self._scalelabels = ['Same', 'Different']
        self._scaleSameMatches = {
            'Same':True,
            'Different':False,
        }
        self.samematches = self._scaleSameMatches[self._scalelabels[self._initialIndex]]
        self._currentConfig = {'missingmatches':None, 'samematches':None}
        self._makeAdditionalWidgets()
        self._setActive(False)

    def _makeAdditionalWidgets(self):
        self._missingMatchesCheck = ttk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self._missingVar,
            command=self._toggleChanged,
        )
        self._missingMatchesCheck.pack(fill='x')
        self._Scale = CS.TextScale(
            self,
            textLabels=self._scalelabels,
            initialInt=self._initialIndex,
            onChange=self._scaleChanged,
            orient="horizontal"
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._childWidgets.extend([self._missingMatchesCheck, self._Scale])

    def _toggleChanged(self, *args):
        self.missingmatches = self._missingVar.get()
        self._somethingChanged()

    def _scaleChanged(self, *args):
        self.samematches = self._scaleSameMatches[self._Scale.textValue]
        self._Scale.focus_set()
        self._somethingChanged()

    def _theymatch(self, md5a, md5b):
        if self._Ctrl.FODict[md5a][0].CameraModel() == '':
            return False
        if self.missingmatches and self._Ctrl.FODict[md5b][0].CameraModel() == '':
            return True
        isSame = self._Ctrl.FODict[md5a][0].CameraModel() == self._Ctrl.FODict[md5b][0].CameraModel() 
        return isSame == self.samematches

class DateCondition(ConditionFrame):
    name = 'CLOSE IN TIME'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingmatches = False

        self._missingMatchesCheck = None
        self._missingVar = tk.BooleanVar()
        self._Scale = None
        self._initialIndex = 1
        self._scalelabels = ['1 minute','10 minutes','1 hour','1 day','1 week','4 weeks','1 year']
        self._scaleSeconds = {
            '1 minute':60,
            '10 minutes':600,
            '1 hour':3600,
            '1 day':24*3600,
            '1 week':7*24*3600,
            '4 weeks':4*7*24*3600,
            '1 year':365*24*3600
        }
        self.timedifference = self._scaleSeconds[self._scalelabels[self._initialIndex]]
        self._currentConfig = {'missingmatches':None, 'timedifference':''}
        self._makeAdditionalWidgets()
        self._setActive(False)

    def _makeAdditionalWidgets(self):
        self._missingMatchesCheck = ttk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self._missingVar,
            command=self._toggleChanged
        )
        self._missingMatchesCheck.pack(fill='x')
        self._Scale = CS.TextScale(
            self,
            textLabels=self._scalelabels,
            initialInt=self._initialIndex,
            onChange=self._scaleChanged,
            orient="horizontal"
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._childWidgets.extend([self._missingMatchesCheck, self._Scale])

    def _toggleChanged(self, *args):
        self.missingmatches = self._missingVar.get()
        self._somethingChanged()

    def _scaleChanged(self, *args):
        self.timedifference = self._scaleSeconds[self._Scale.textValue]
        self._Scale.focus_set()
        self._somethingChanged()

    def _theymatch(self, md5a, md5b):
        datetime_a = self._Ctrl.FODict[md5a][0].DateTime()
        datetime_b = self._Ctrl.FODict[md5b][0].DateTime()
        # deal with missings:
        if datetime_a == 'Missing':
            return False
        if datetime_b == 'Missing':
            return self.missingmatches
        if abs((datetime_a - datetime_b).total_seconds()) <= self.timedifference:
            return True
        return False

class ShapeCondition(ConditionFrame):
    name = 'PICTURE SHAPE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._Scale = None
        self._initialIndex = 1
        self._scalelabels = ['Different Size', 'Portrait/Landscape', 'Exact', '<5%', '<10%', '<20%', '<30%', '<50%']
        self._scalevalues = {
            'Different Size':-2,
            'Portrait/Landscape':-1,
            'Exact':0,
            '<5%':5,
            '<10%':10,
            '<20%':20,
            '<30%':30,
            '<50%':50
        }
        self.limit = self._scalevalues[self._scalelabels[self._initialIndex]]
        self._currentConfig = {'limit':-666}
        self._makeAdditionalWidgets()
        self._setActive(False)

    def _makeAdditionalWidgets(self):
        self._Scale = CS.TextScale(self,
                                   textLabels=self._scalelabels,
                                   topLabel='',
                                   initialInt=self._initialIndex,
                                   onChange=self._scaleChanged,
                                   orient="horizontal"
        )
        self._Scale.TSScale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._childWidgets.extend([self._Scale])

    def _scaleChanged(self, *args):
        self.limit = self._scalevalues[self._Scale.textValue]
        self._Scale.focus_set()
        self._somethingChanged()

    def _theymatch(self, md5a, md5b):
        foaval = self._Ctrl.FODict[md5a][0].ShapeParameter()
        fobval = self._Ctrl.FODict[md5b][0].ShapeParameter()
        if self.limit == -2:
            return set(self._Ctrl.FODict[md5a][0].Size()) != set(self._Ctrl.FODict[md5b][0].Size())
        if self.limit == -1:
            return foaval*fobval > 0.0 or fobval == 0.0
        return abs(foaval - fobval) <= self.limit
