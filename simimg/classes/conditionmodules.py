''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich (click on the name label)
    A switch to make this criterion obligatory (must match)
    A method to do something when _somethingChanged
    A method to determine which imagepairs from a list of pairs match
'''
import math
import statistics as stats
import tkinter as tk
from tkinter import ttk
import simimg.classes.textscale as TS
import simimg.classes.tooltip as TT

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
                if widget.winfo_class() == 'TCombobox':
                    widget.config(state="readonly")
                else:
                    widget.config(state="normal")
        else:
            self.config(relief="sunken")
            for widget in self.childWidgets:
                widget.config(state="disabled")

    def _activeToggled(self, event):
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
        self.ScaleTip = None
        self.method = "ahash"
        self.limit = 14
        self.limitVar = tk.IntVar()
        self.limitVar.set(self.limit)
        self.currentConfig = {'method':'', 'limit':-1}
        self.currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self.setActive(False)
        self._mouseIsPressed = False
        
    def _makeAdditionalWidgets(self):
        self.Combo = ttk.Combobox(
            self,
            values=["ahash", "dhash", "phash", "whash"],
            width=8,
            state="readonly",
        )
        self.Combo.set(self.method)
        self.Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self.Scale = tk.Scale(self,
                              from_= 1, to=50,
                              variable=self.limitVar,
                              takefocus=1,
                              command=self._scaleChanged,
                              orient="horizontal"
        )
        self.Scale.bind("<ButtonPress-1>", self._scalePressed)
        self.Scale.bind("<ButtonRelease-1>", self._scaleReleased)
        self.Scale.bind("<Control-a>", self._doSelectAll)
        self.ScaleTip = TT.Tooltip(self.Scale, text='')
        self.Combo.pack()
        self.Scale.pack()
        self.childWidgets.extend([self.Combo, self.Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _somethingChanged(self, *args):
        self.Ctrl.onConditionChanged()

    def _comboChanged(self, *args):
        self.method = self.Combo.get()
        self.Combo.focus_set()
        self.Ctrl.onConditionChanged()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.limit = self.limitVar.get()
        self.Scale.focus_set()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b, values=None):
            absdiff = abs(
                self.Ctrl.FODict[md5a][0].hashDict[self.method] -
                self.Ctrl.FODict[md5b][0].hashDict[self.method]
            )
            values.append(absdiff)
            return absdiff <= self.limit

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

        mVals = []
        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b, values=mVals)]
        mVals.sort()
        myTip = 'min=%d; >10 pairs=%d' % (math.ceil(min(mVals)), math.ceil(mVals[9])) if len(mVals) > 9 else 'Min: %d' % (math.ceil(min(mVals)))
        self.ScaleTip.text=myTip

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
        self.ScaleTip = None
        self.method = "hsvhash"
        self.limit = 10
        self.limitVar = tk.IntVar()
        self.limitVar.set(self.limit)
        self.currentConfig = {'method':'', 'limit':-1}
        self.currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self.setActive(False)
        self._mouseIsPressed = False

    def _makeAdditionalWidgets(self):
        self.Combo = ttk.Combobox(
            self,
            values=["hsvhash", "hsv5hash"],
            width=8,
            state="readonly",
        )
        self.Combo.set(self.method)
        self.Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self.Scale = tk.Scale(self,
                              from_= 1, to=50,
                              variable=self.limitVar,
                              command=self._scaleChanged,
                              orient="horizontal"
        )
        self.Scale.bind("<ButtonPress-1>", self._scalePressed)
        self.Scale.bind("<ButtonRelease-1>", self._scaleReleased)
        self.Scale.bind("<Control-a>", self._doSelectAll)
        self.ScaleTip = TT.Tooltip(self.Scale, text='')
        self.Combo.pack()
        self.Scale.pack()
        self.childWidgets.extend([self.Combo, self.Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _somethingChanged(self, *args):
        self.Ctrl.onConditionChanged()

    def _comboChanged(self, *args):
        self.method = self.Combo.get()
        self.Combo.focus_set()
        self.Ctrl.onConditionChanged()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.limit = self.limitVar.get()
        self.Scale.focus_set()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b, values=None):
            foaHash = self.Ctrl.FODict[md5a][0].hashDict[self.method]
            fobHash = self.Ctrl.FODict[md5b][0].hashDict[self.method]
            # we need to take care of the median hue value (0, 6, .. th element)
            # when calculating distance because this is a measure that wraps at 255
            # back to 0 the correct distance is the minimum of (h1-h2) % 255 and (h2-h1) % 255
            # in all other cases use abs(v1 -v2)
            distArr = [
                abs(foaHash[i]-fobHash[i]) if i % 6
                else min((foaHash[i]-fobHash[i]) % 255, (fobHash[i]-foaHash[i]) % 255)
                for i in range(len(foaHash))
            ]
            val = stats.mean(distArr)
            values.append(val)
            return val <= self.limit

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

        mVals = []
        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b, values=mVals)]
        mVals.sort()
        myTip = 'min=%d; >10 pairs=%d' % (math.ceil(min(mVals)), math.ceil(mVals[9])) if len(mVals) > 9 else 'Min: %d' % (math.ceil(min(mVals)))
        self.ScaleTip.text=myTip

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
        self.Scale = None

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
        self._mouseIsPressed = False

    def _makeAdditionalWidgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingVar,
                                                  command=self._somethingChanged,
                                                  anchor='w')
        self.missingMatchesCheck.pack()
        self.Scale = TS.TextScale(self,
                                  textLabels=self.scalelabels,
                                  initialInt=self.initialIndex,
                                  onChange=self._scaleChanged,
                                  orient="horizontal"
        )
        self.Scale.TSScale.bind("<ButtonPress-1>", self._scalePressed)
        self.Scale.TSScale.bind("<ButtonRelease-1>", self._scaleReleased)
        self.Scale.bind("<Control-a>", self._doSelectAll)
        self.Scale.pack()
        self.childWidgets.extend([self.missingMatchesCheck, self.Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _somethingChanged(self, *args):
        self.missing = self.missingVar.get()
        self.Ctrl.onConditionChanged()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.timeDifferenceInSec = self.scaleSeconds[self.Scale.textValue]
        self.Scale.focus_set()
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

class ShapeCondition(ConditionFrame):
    name = 'PICTURE SHAPE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.Scale = None
        self.initialIndex = 0
        self.scalelabels = ['Portrait/Landscape', 'Exact', '<5%', '<10%', '<20%', '<30%', '<50%']
        self.scalevalues = {
            'Portrait/Landscape':-1,
            'Exact':0,
            '<5%':5,
            '<10%':10,
            '<20%':20,
            '<30%':30,
            '<50%':50
        }
        self.limit = self.scalevalues[self.scalelabels[self.initialIndex]]

        self.currentConfig = {'limit':-666}
        self.currentMatchingGroups = []
        self._makeAdditionalWidgets()
        self.setActive(False)
        self._mouseIsPressed = False

    def _makeAdditionalWidgets(self):
        self.Scale = TS.TextScale(self,
                                  textLabels=self.scalelabels,
                                  topLabel='',
                                  initialInt=self.initialIndex,
                                  onChange=self._scaleChanged,
                                  orient="horizontal"
        )
        self.Scale.TSScale.bind("<ButtonPress-1>", self._scalePressed)
        self.Scale.TSScale.bind("<ButtonRelease-1>", self._scaleReleased)
        self.Scale.TSScale.bind("<Control-a>", self._doSelectAll)
        self.Scale.pack()
        self.childWidgets.extend([self.Scale])

    def _doSelectAll(self, *args):
        self.Ctrl.selectAllThumbnails()
        return "break"

    def _somethingChanged(self, *args):
        self.Ctrl.onConditionChanged()

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._scaleChanged()

    def _scaleChanged(self, *args):
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.limit = self.scalevalues[self.Scale.textValue]
        self.Scale.focus_set()
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):
        def theymatch(md5a, md5b):
            foaval = self.Ctrl.FODict[md5a][0].ShapeParameter()
            fobval = self.Ctrl.FODict[md5b][0].ShapeParameter()
            if self.limit == -1:
                return foaval*fobval > 0.0 or fobval == 0.0
            return abs(foaval - fobval) <= self.limit

        # check that the widget parameters are different from before
        # if not simply return the matchingGroupsList from before
        if (
                self._candidates == set(candidates) and
                self.limit == self.currentConfig['limit']
        ):
            return self.currentMatchingGroups

        self._candidates = set(candidates)
        self.currentConfig['limit'] = self.limit

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
