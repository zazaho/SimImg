""" Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active switch (click on the name label)
    A switch to make this criterion obligatory (must match)
    A method to do something when _somethingChanged
    A method to determine which imagepairs from a list of pairs match
"""
import functools
import itertools
import math
import tkinter as tk
from operator import add
from tkinter import ttk

import simimg.classes.customscales as CS
import simimg.classes.tooltip as TT


class ConditionModule(ttk.Frame):
    "A frame that holds one selection criterion with options"
    name = ""
    _conditionName = ""
    _currentConfig = {}

    def __init__(self, parent, Controller=None):
        super().__init__(parent)

        self.config(borderwidth=1, relief="sunken")

        # keep a handle of the controller object
        self._Ctrl = Controller
        self.active = False
        self.mustMatch = tk.BooleanVar()

        self._currentMatchingGroups = {}
        self._matchingInfo = []
        self._checksums = {}

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x")

        self._label = ttk.Label(header_frame, text=self._conditionName)
        self._label.bind("<Button-1>", self._activeToggled)
        self._label.pack(side="left", fill="x")

        self._fold_button = ttk.Label(header_frame, text="^")
        self._fold_button.bind("<Button-1>", self.toggleFolding)
        self._fold_button.pack(side="right", fill="x")
        self.is_folded = False

        self._options_frame = ttk.Frame(self)
        self._options_frame.pack(fill="x")
        self._mustMatchToggle = ttk.Checkbutton(
            self._options_frame,
            text="Must Match",
            variable=self.mustMatch,
            command=self._somethingChanged
        )
        self._mustMatchToggle.pack(fill="x")
        self._childWidgets = [self._mustMatchToggle]
        self._makeAdditionalWidgets()
        self._setActive(False)

        self.missingmatches = None
        self.scalevalue = None

    def _makeAdditionalWidgets(self):
        pass

    def _setActive(self, value):
        self.active = value
        if self.active:
            self.config(relief="raised")
            for widget in self._childWidgets:
                if widget.winfo_class() == "TCombobox":
                    widget.config(state="readonly")
                else:
                    widget.config(state="normal")
        else:
            self.config(relief="sunken")
            for widget in self._childWidgets:
                widget.config(state="disabled")

    def toggleFolding(self, *args):
        self.is_folded = not self.is_folded
        if self.is_folded:
            self._fold_button.config(text="v")
            self._options_frame.pack_forget()
        else:
            self._fold_button.config(text="^")
            self._options_frame.pack()

    def _activeToggled(self, *args):
        self._setActive(not self.active)
        self._somethingChanged()

    def _somethingChanged(self, *args):
        self._Ctrl.onChange()

    def _updateFromPrevious(self, checksums):
        # check that the checksums or the widget parameters changed from before
        # if not simply return false to indicate that nothing is updated
        foundADifference = self._checksums != set(checksums)
        for param, value in self._currentConfig.items():
            if foundADifference:
                # one difference is enough
                break
            if getattr(self, param) != value:
                foundADifference = True

        if not foundADifference:
            return False

        # store the current values for posterity
        self._checksums = set(checksums)
        for param in self._currentConfig:
            self._currentConfig[param] = getattr(self, param)
        return True

    def _theymatch(self, checksumA, checksumB):
        pass

    def _preMatching(self):
        pass

    def _postMatching(self):
        pass

    def _getMatchingGroups(self):
        cand = list(itertools.combinations(self._checksums, 2))
        matches = [(a, b) for a, b in cand if self._theymatch(a, b)]
        # make a dict with:
        # for each checksum that has matches the set of matching checksums
        # we include the checksum itself
        matchingGroupsDict = {}
        for a, b in matches:
            if a not in matchingGroupsDict:
                matchingGroupsDict[a] = {a}
            matchingGroupsDict[a].add(b)
            if b not in matchingGroupsDict:
                matchingGroupsDict[b] = {b}
            matchingGroupsDict[b].add(a)
        self._currentMatchingGroups = matchingGroupsDict

    def matchingGroups(self, checksums):
        # if nothing changed _updateFromPrevious will return False
        if not self._updateFromPrevious(checksums):
            return self._currentMatchingGroups
        self._preMatching()
        self._getMatchingGroups()
        self._postMatching()
        return self._currentMatchingGroups

    # this is a trick to make sure that ctrl-a works on the thumbnails
    # even if the Scale has foocus
    def _doSelectAll(self, *args):
        self._Ctrl.toggleSelectAllThumbnails()
        return "break"


class HashingCondition(ConditionModule):
    _currentConfig = {"method": None, "limit": None}
    _methods = [""]
    method = ""
    limit = 1

    def _makeAdditionalWidgets(self):
        self._Combo = ttk.Combobox(
            self._options_frame,
            values=self._methods,
            width=15,
            state="readonly",
        )
        self._Combo.set(self.method)
        self._Combo.bind("<<ComboboxSelected>>", self._comboChanged)
        self._Combo.pack()
        limitVar = tk.IntVar()
        limitVar.set(self.limit)
        self._Scale = CS.LabelScale(
            self._options_frame,
            from_=1,
            to=50,
            takefocus=1,
            command=self._scaleChanged,
            variable=limitVar,
            orient="horizontal",
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._ScaleTip = TT.Tooltip(self._Scale, text="")
        self._childWidgets.extend([self._Combo, self._Scale])

    def _comboChanged(self, *args):
        self.method = self._Combo.get()
        self._Combo.focus_set()
        self._somethingChanged()

    def _scaleChanged(self, *args):
        self.limit = self._Scale.get()
        self._Scale.focus_set()
        self._somethingChanged()

    def _preMatching(self):
        # Call this to make sure the hash values for this method are available
        self._Ctrl.setHashes(hashName=self.method)
        self._matchingInfo = []

    def _postMatching(self):
        if not self._matchingInfo:
            self._ScaleTip.text = ""
        elif len(self._matchingInfo) < 10:
            self._ScaleTip.text = f"Min: {math.ceil(min(self._matchingInfo))}"
        else:
            self._matchingInfo.sort()
            self._ScaleTip.text = (
                f"min={math.ceil(min(self._matchingInfo))}; "
                f">10 pairs={math.ceil(self._matchingInfo[9])}"
            )


class GradientCondition(HashingCondition):
    name = "gradients"
    _conditionName = "GRADIENTS"
    _methods = ["Horizontal", "Vertical"]
    method = "Horizontal"
    limit = 14

    def _theymatch(self, checksumA, checksumB):
        hashA = self._Ctrl.FODict[checksumA][0].hashDict[self.method]
        hashB = self._Ctrl.FODict[checksumB][0].hashDict[self.method]
        dist = functools.reduce(
            add,
            [format(hashA[i] ^ hashB[i], "b").count("1") for i in range(len(hashA))]
        )
        self._matchingInfo.append(dist)
        return dist <= self.limit


class ColorCondition(HashingCondition):
    name = "colordistance"
    _conditionName = "COLOR DISTANCE"
    _methods = [
        "HSV",
        "HSV (5 regions)",
        "RGB",
        "RGB (5 regions)",
        "Luminosity",
        "Luminosity (5 regions)"
    ]
    method = "HSV (5 regions)"
    limit = 10

    def _theymatch(self, checksumA, checksumB):
        hashA = self._Ctrl.FODict[checksumA][0].hashDict[self.method]
        hashB = self._Ctrl.FODict[checksumB][0].hashDict[self.method]
        # we need to take care of the median hue value (0, 6, .. th element)
        # when calculating distance because this is a measure that wraps at 255
        # back to 0. The correct distance is the minimum of:
        # (h1-h2) % 255 and (h2-h1) % 255
        # in all other cases use abs(v1 -v2)
        if self.method in ["HSV", "HSV (5 regions)"]:
            distArr = [
                abs(hashA[i]-hashB[i]) if i % 6
                else min((hashA[i]-hashB[i]) % 255, (hashB[i]-hashA[i]) % 255)
                for i in range(len(hashA))
            ]
        else:
            distArr = [abs(hashA[i]-hashB[i]) for i in range(len(hashA))]
        val = sum(distArr)/len(distArr)
        self._matchingInfo.append(val)
        return val <= self.limit


class ExifCondition(ConditionModule):
    _currentConfig = {"missingmatches": None, "scalevalue": None}
    _scaleDict = {"": 0}
    _initialScaleVal = ""
    _showMissingMatches = True

    def _makeAdditionalWidgets(self):
        self.missingmatches = False
        self.scalevalue = self._scaleDict[self._initialScaleVal]
        self._missingVar = tk.BooleanVar()
        self._missingMatchesCheck = ttk.Checkbutton(
            self._options_frame,
            text="Missing Matches",
            variable=self._missingVar,
            command=self._toggleChanged,
        )
        if self._showMissingMatches:
            self._missingMatchesCheck.pack(fill="x")

        labels = list(self._scaleDict)
        scaleVar = tk.IntVar()
        scaleVar.set(labels.index(self._initialScaleVal))
        self._Scale = CS.TextScale(
            self._options_frame,
            textLabels=labels,
            command=self._scaleChanged,
            variable=scaleVar,
            orient="horizontal"
        )
        self._Scale.bind("<Control-a>", self._doSelectAll)
        self._Scale.pack()
        self._childWidgets.extend([self._missingMatchesCheck, self._Scale])

    def _toggleChanged(self, *args):
        self.missingmatches = self._missingVar.get()
        self._somethingChanged()

    def _scaleChanged(self, *args):
        self.scalevalue = self._scaleDict[self._Scale.get()]
        self._Scale.focus_set()
        self._somethingChanged()


class CameraCondition(ExifCondition):
    name = "cameramodel"
    _conditionName = "CAMERA MODEL"
    _scaleDict = {"Same": True, "Different": False}
    _initialScaleVal = "Same"

    def _theymatch(self, checksumA, checksumB):
        camA = self._Ctrl.FODict[checksumA][0].cameraModel()
        camB = self._Ctrl.FODict[checksumB][0].cameraModel()
        if camA == "":
            return False
        if self.missingmatches and camB == "":
            return True
        return (camA == camB) == self.scalevalue


class DateCondition(ExifCondition):
    name = "closeintime"
    _conditionName = "CLOSE IN TIME"
    _scaleDict = {
        "1 minute": 60,
        "10 minutes": 600,
        "1 hour": 3600,
        "1 day": 24*3600,
        "1 week": 7*24*3600,
        "4 weeks": 4*7*24*3600,
        "1 year": 365*24*3600
    }
    _initialScaleVal = "10 minutes"

    def _theymatch(self, checksumA, checksumB):
        dateA = self._Ctrl.FODict[checksumA][0].dateTime()
        dateB = self._Ctrl.FODict[checksumB][0].dateTime()
        if dateA == "Missing":
            return False
        if dateB == "Missing":
            return self.missingmatches
        return abs((dateA - dateB).total_seconds()) <= self.scalevalue


class ShapeCondition(ExifCondition):
    name = "pictureshape"
    _conditionName = "PICTURE SHAPE"
    _scaleDict = {
        "Different Size": -2,
        "Portrait/Landscape": -1,
        "Exact": 0,
        "<5%": 5,
        "<10%": 10,
        "<20%": 20,
        "<30%": 30,
        "<50%": 50
    }
    _initialScaleVal = "Portrait/Landscape"
    _showMissingMatches = False

    def _theymatch(self, checksumA, checksumB):
        if self.scalevalue == -2:
            sizeA = self._Ctrl.FODict[checksumA][0].size()
            sizeB = self._Ctrl.FODict[checksumB][0].size()
            return set(sizeA) != set(sizeB)
        shapeA = self._Ctrl.FODict[checksumA][0].shapeParameter()
        shapeB = self._Ctrl.FODict[checksumB][0].shapeParameter()
        if self.scalevalue == -1:
            return shapeA*shapeB > 0.0 or (shapeA == shapeB == 0.0)
        return abs(shapeA - shapeB) <= self.scalevalue
