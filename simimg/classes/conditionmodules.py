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
from . import textscale as TS
from . import tooltip as TT

class ConditionFrame(ttk.Frame):
    name = ''
    " A frame that holds one selection criterion with options"
    def __init__(self, parent, Controller=None):
        super().__init__(parent)

        # keep a handle of the controller object
        self.Ctrl = Controller

        self.config(borderwidth=1, relief="sunken")

        self._label = None
        self.active = False
        self.mustMatch = tk.BooleanVar()
        self._mustMatchToggle = None
        self._childWidgets = []

        self._currentConfig = {}
        self._currentMatchingGroups = []

        self._makeBaseWidgets()
        self._setActive(False)
        self._md5s = {}

    def _makeBaseWidgets(self):
        self._label = ttk.Label(self, text=self.name)
        self._label.bind('<Button-1>', self._activeToggled)
        self._mustMatchToggle = ttk.Checkbutton(
            self,
            text="Must Match",
            variable=self.mustMatch,
            command=self._somethingChanged
        )

        self._childWidgets = [self._mustMatchToggle]
        self._label.pack(fill='x')
        self._mustMatchToggle.pack(fill='x')

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
        self.Ctrl.onChange()

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

    def _theymatch(self, md5a, md5b, **kwargs):
        pass

    def _getMatchingGroups(self, **kwargs):
        cand = list(itertools.combinations(self._md5s,2))
        matches = [(a, b) for a, b in cand if self._theymatch(a, b, **kwargs)]
        self._currentMatchingGroups = []
        # make a FULL SORTED group list for EACH MD5 ONE ENTRY
        # this is important for the merging of groups later
        md5s = list(self._md5s)
        md5s.sort()
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            self._currentMatchingGroups.append(dummy)

    def matchingGroups(self, md5s):
        #if nothing changed _updateFromPrevious will return False
        if not self._updateFromPrevious(md5s):
            return self._currentMatchingGroups
        self._getMatchingGroups()
        return self._currentMatchingGroups

class GradientCondition(ConditionFrame):
    name = 'GRADIENTS'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._Combo = None
        self._Scale = None
        self._ScaleTip = None
        self.method = "Horizontal"
        self.limit = 14
        self._limitVar = tk.IntVar()
        self._limitVar.set(self.limit)
        self._currentConfig = {'method':'', 'limit':-1}
        self._currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self._setActive(False)
        self._mouseIsPressed = False
        
    def _makeAdditionalWidgets(self):
        self._Combo = ttk.Combobox(
            self,
            values=["Horizontal", "Vertical"],
            width=15,
            state="readonly",
        )
        self._Combo.set(self.method)
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Scale = tk.Scale(self,
                               from_= 1, to=50,
                               variable=self._limitVar,
                               takefocus=1,
                               command=self._scaleChanged,
                               orient="horizontal",
        )
        self._Scale.bind("<ButtonPress-1>", self._scalePressed)
        self._Scale.bind("<ButtonRelease-1>", self._scaleReleased)
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._ScaleTip = TT.Tooltip(self._Scale, text='')
        self._Combo.pack()
        self._Scale.pack()
        self._childWidgets.extend([self._Combo, self._Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _comboChanged(self, *args):
        self.method = self._Combo.get()
        self._Combo.focus_set()
        self.Ctrl.onChange()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.limit = self._limitVar.get()
        self._Scale.focus_set()
        self.Ctrl.onChange()

    def _theymatch(self, md5a, md5b, values=None):
        hashA = self.Ctrl.FODict[md5a][0].hashDict[self.method]
        hashB = self.Ctrl.FODict[md5b][0].hashDict[self.method]
        dist = functools.reduce(
            add,
            [format(hashA[i]^hashB[i], 'b').count('1') for i in range(len(hashA))]
        )
        values.append(dist)
        return dist <= self.limit

    def matchingGroups(self, md5s):
        # if nothing changed _updateFromPrevious will return False
        if not self._updateFromPrevious(md5s):
            return self._currentMatchingGroups

        # Call this to make sure the hash values for this method are available
        self.Ctrl.setImageHashes(hashName=self.method)

        mVals = []
        self._getMatchingGroups(values=mVals)
        if not mVals:
            self._ScaleTip.text = ''
        elif len(mVals) < 10:
            self._ScaleTip.text = 'Min: %d' % (math.ceil(min(mVals)))
        else:
            mVals.sort()
            self._ScaleTip.text = 'min=%d; >10 pairs=%d' % (math.ceil(min(mVals)), math.ceil(mVals[9]))

        return self._currentMatchingGroups

class ColorCondition(ConditionFrame):
    name = 'COLOR DISTANCE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._Combo = None
        self._Scale = None
        self._ScaleTip = None
        self.method = "HSV (5 regions)"
        self.limit = 10
        self._limitVar = tk.IntVar()
        self._limitVar.set(self.limit)
        self._currentConfig = {'method':'', 'limit':-1}
        self._currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self._setActive(False)
        self._mouseIsPressed = False

    def _makeAdditionalWidgets(self):
        self._Combo = ttk.Combobox(
            self,
            values=["HSV", "HSV (5 regions)","RGB", "RGB (5 regions)", "Luminosity", "Luminosity (5 regions)"],
            width=15,
            state="readonly",
        )
        self._Combo.set(self.method)
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Scale = tk.Scale(self,
                              from_= 1, to=50,
                              variable=self._limitVar,
                              command=self._scaleChanged,
                              orient="horizontal"
        )
        self._Scale.bind("<ButtonPress-1>", self._scalePressed)
        self._Scale.bind("<ButtonRelease-1>", self._scaleReleased)
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._ScaleTip = TT.Tooltip(self._Scale, text='')
        self._Combo.pack()
        self._Scale.pack()
        self._childWidgets.extend([self._Combo, self._Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _comboChanged(self, *args):
        self.method = self._Combo.get()
        self._Combo.focus_set()
        self.Ctrl.onChange()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.limit = self._limitVar.get()
        self._Scale.focus_set()
        self.Ctrl.onChange()

    def _theymatch(self, md5a, md5b, values=None):
        hashA = self.Ctrl.FODict[md5a][0].hashDict[self.method]
        hashB = self.Ctrl.FODict[md5b][0].hashDict[self.method]
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
        values.append(val)
        return val <= self.limit

    def matchingGroups(self, md5s):
        #if nothing changed _updateFromPrevious will return False
        if not self._updateFromPrevious(md5s):
            return self._currentMatchingGroups

        #Call this to make sure the hash values for this method are available
        self.Ctrl.setImageHashes(hashName=self.method)

        mVals = []
        self._getMatchingGroups(values=mVals)
        if not mVals:
            self._ScaleTip.text = ''
        elif len(mVals) < 10:
            self._ScaleTip.text = 'Min: %d' % (math.ceil(min(mVals)))
        else:
            mVals.sort()
            self._ScaleTip.text = 'min=%d; >10 pairs=%d' % (math.ceil(min(mVals)), math.ceil(mVals[9]))

        return self._currentMatchingGroups

class CameraCondition(ConditionFrame):
    name = 'SAME CAMERA'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._missingMatchesCheck = None
        self._missingVar = tk.BooleanVar()
        self.missingmatches = False
        self._currentConfig = {'missingmatches':None}
        self._currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self._setActive(False)

    def _makeAdditionalWidgets(self):
        self._missingMatchesCheck = ttk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self._missingVar,
            command=self._somethingChanged,
        )
        self._missingMatchesCheck.pack(fill='x')
        self._childWidgets.extend([self._missingMatchesCheck])

    def _somethingChanged(self, *args):
        self.missingmatches = self._missingVar.get()
        self.Ctrl.onChange()

    def _theymatch(self, md5a, md5b):
        if self.Ctrl.FODict[md5a][0].CameraModel() == '':
            return False
        if self.Ctrl.FODict[md5a][0].CameraModel() == self.Ctrl.FODict[md5b][0].CameraModel():
            return True
        if self.missingmatches and self.Ctrl.FODict[md5b][0].CameraModel() == '':
            return True
        return False

class DateCondition(ConditionFrame):
    name = 'CLOSE IN TIME'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._missingMatchesCheck = None
        self._missingVar = tk.BooleanVar()
        self.missingmatches = False
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
        self._currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self._setActive(False)
        self._mouseIsPressed = False

    def _makeAdditionalWidgets(self):
        self._missingMatchesCheck = ttk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self._missingVar,
            command=self._somethingChanged
        )
        self._missingMatchesCheck.pack(fill='x')
        self._Scale = TS.TextScale(
            self,
            textLabels=self._scalelabels,
            initialInt=self._initialIndex,
            onChange=self._scaleChanged,
            orient="horizontal"
        )
        self._Scale.TSScale.bind("<ButtonPress-1>", self._scalePressed)
        self._Scale.TSScale.bind("<ButtonRelease-1>", self._scaleReleased)
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._childWidgets.extend([self._missingMatchesCheck, self._Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _somethingChanged(self, *args):
        self.missingmatches = self._missingVar.get()
        self.Ctrl.onChange()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.timedifference = self._scaleSeconds[self._Scale.textValue]
        self._Scale.focus_set()
        self.Ctrl.onChange()

    def _theymatch(self, md5a, md5b):
        datetime_a = self.Ctrl.FODict[md5a][0].DateTime()
        datetime_b = self.Ctrl.FODict[md5b][0].DateTime()
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
        self._initialIndex = 0
        self._scalelabels = ['Portrait/Landscape', 'Exact', '<5%', '<10%', '<20%', '<30%', '<50%']
        self._scalevalues = {
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
        self._currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self._setActive(False)
        self._mouseIsPressed = False

    def _makeAdditionalWidgets(self):
        self._Scale = TS.TextScale(self,
                                  textLabels=self._scalelabels,
                                  topLabel='',
                                  initialInt=self._initialIndex,
                                  onChange=self._scaleChanged,
                                  orient="horizontal"
        )
        self._Scale.TSScale.bind("<ButtonPress-1>", self._scalePressed)
        self._Scale.TSScale.bind("<ButtonRelease-1>", self._scaleReleased)
        self._Scale.TSScale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._childWidgets.extend([self._Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.limit = self._scalevalues[self._Scale.textValue]
        self._Scale.focus_set()
        self.Ctrl.onChange()

    def _theymatch(self, md5a, md5b):
        foaval = self.Ctrl.FODict[md5a][0].ShapeParameter()
        fobval = self.Ctrl.FODict[md5b][0].ShapeParameter()
        if self.limit == -1:
            return foaval*fobval > 0.0 or fobval == 0.0
        return abs(foaval - fobval) <= self.limit
