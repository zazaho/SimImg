''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich (click on the name label)
    A switch to make this criterion obligatory (must match)
    A method to do something when somethingChanged
    A method to determine which imagepairs from a list of pairs match
'''

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
        self.hashCombo = None
        self.hashMethod = "ahash"
        self.threshScale = None
        self.hashThresh = tk.IntVar()
        self.make_additional_widgets()
        
    def make_additional_widgets(self):
        self.hashCombo = ttk.Combobox(
            self,
            values=["ahash","dhash","phash","whash"],
            width=8,
        )
        self.hashCombo.set(self.hashMethod)
        self.hashCombo.bind("<<ComboboxSelected>>", self.hashComboMethodChange)
        self.threshScale = tk.Scale(self,
                                    from_= 1, to=100,
                                    label='Threshold',
                                    variable=self.hashThresh,
                                    command=self.somethingChanged,
                                    orient=tk.HORIZONTAL)
        self.hashCombo.pack()
        self.threshScale.pack()

    def hashComboMethodChange(self, event):
        oldHashMethod = self.hashMethod
        newHashMethod = self.hashCombo.get()
        if oldHashMethod != newHashMethod:
            self.hashMethod = newHashMethod
            self.somethingChanged()

    def somethingChanged(self, *args):
        if self.active:
            #Call this to make sure the hash values for this method are available
            self.Ctrl.setImageHashes(hashName=self.hashMethod)
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):

        def theymatch(md5a, md5b):
            foaHash = hex_to_hash(getattr(self.Ctrl.FODict[md5a][0], self.hashMethod))
            fobHash = hex_to_hash(getattr(self.Ctrl.FODict[md5b][0], self.hashMethod))
            return abs(foaHash - fobHash) <= self.hashThresh.get()

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        matchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            matchingGroups.append(dummy)
            
        matchingGroups.sort()

        return matchingGroups

class CameraCondition(ConditionFrame):
    name = 'SAME CAMERA'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingMatchesCheck = None
        self.missingMatches = tk.BooleanVar()
        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self.missingMatches,
            command=self.somethingChanged,
            anchor='w'
        )
        self.missingMatchesCheck.pack()

    def somethingChanged(self, *args):
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
            if self.missingMatches.get() and self.Ctrl.FODict[md5b][0].CameraModel() == '':
                return True
            return False

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        matchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            matchingGroups.append(dummy)

        matchingGroups.sort()

        return matchingGroups

class DateCondition(ConditionFrame):
    name = 'CLOSE IN TIME'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingMatchesCheck = None
        self.missingMatches = tk.BooleanVar()

        self.timeDifferenceScale = None
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

        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingMatches,
                                                  command=self.somethingChanged,
                                                  anchor='w')
        self.missingMatchesCheck.pack()
        self.timeDifferenceScale = TS.TextScale(self,
                                             textLabels=self.scalelabels,
                                             label='Maximum Difference', 
                                             command=self.somethingChanged,
                                             orient=tk.HORIZONTAL)
        self.timeDifferenceScale.topFrame.pack()

    def somethingChanged(self, *args):
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
                return self.missingMatches.get()
            if abs((datetime_a - datetime_b).total_seconds()) <= maxDiff:
                return True
            return False

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        matchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            matchingGroups.append(dummy)

        matchingGroups.sort()

        return matchingGroups



class HashCondition(ConditionFrame):
    name = 'HASHING DISTANCE'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.hashCombo = None
        self.hashMethod = "ahash"
        self.threshScale = None
        self.hashThresh = tk.IntVar()
        self.make_additional_widgets()
        
    def make_additional_widgets(self):
        self.hashCombo = ttk.Combobox(
            self,
            values=["ahash","dhash","phash","whash"],
            width=8,
        )
        self.hashCombo.set(self.hashMethod)
        self.hashCombo.bind("<<ComboboxSelected>>", self.hashComboMethodChange)
        self.threshScale = tk.Scale(self,
                                    from_= 1, to=100,
                                    label='Threshold',
                                    variable=self.hashThresh,
                                    command=self.somethingChanged,
                                    orient=tk.HORIZONTAL)
        self.hashCombo.pack()
        self.threshScale.pack()

    def hashComboMethodChange(self, event):
        oldHashMethod = self.hashMethod
        newHashMethod = self.hashCombo.get()
        if oldHashMethod != newHashMethod:
            self.hashMethod = newHashMethod
            self.somethingChanged()

    def somethingChanged(self, *args):
        if self.active:
            #Call this to make sure the hash values for this method are available
            self.Ctrl.setImageHashes(hashName=self.hashMethod)
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):

        def theymatch(md5a, md5b):
            foaHash = hex_to_hash(getattr(self.Ctrl.FODict[md5a][0], self.hashMethod))
            fobHash = hex_to_hash(getattr(self.Ctrl.FODict[md5b][0], self.hashMethod))
            return abs(foaHash - fobHash) <= self.hashThresh.get()

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        matchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            matchingGroups.append(dummy)
            
        matchingGroups.sort()

        return matchingGroups

class CameraCondition(ConditionFrame):
    name = 'SAME CAMERA'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingMatchesCheck = None
        self.missingMatches = tk.BooleanVar()
        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(
            self,
            text="Missing Matches",
            variable=self.missingMatches,
            command=self.somethingChanged,
            anchor='w'
        )
        self.missingMatchesCheck.pack()

    def somethingChanged(self, *args):
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
            if self.missingMatches.get() and self.Ctrl.FODict[md5b][0].CameraModel() == '':
                return True
            return False

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        matchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            matchingGroups.append(dummy)

        matchingGroups.sort()

        return matchingGroups

class HSVCondition(ConditionFrame):
    name = 'SIMILAR COLOURS'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.hashCombo = None
        self.hashMethod = "hsvhash"
        self.threshScale = None
        self.hashThresh = tk.IntVar()
        self.make_additional_widgets()
        
    def make_additional_widgets(self):
        self.hashCombo = ttk.Combobox(
            self,
            values=["hsvhash","hsv5hash"],
            width=8,
        )
        self.hashCombo.set(self.hashMethod)
        self.hashCombo.bind("<<ComboboxSelected>>", self.hashComboMethodChange)
        self.threshScale = tk.Scale(self,
                                    from_= 1, to=100,
                                    label='Threshold',
                                    variable=self.hashThresh,
                                    command=self.somethingChanged,
                                    orient=tk.HORIZONTAL)
        self.hashCombo.pack()
        self.threshScale.pack()

    def hashComboMethodChange(self, event):
        oldHashMethod = self.hashMethod
        newHashMethod = self.hashCombo.get()
        if oldHashMethod != newHashMethod:
            self.hashMethod = newHashMethod
            self.somethingChanged()

    def somethingChanged(self, *args):
        if self.active:
            #Call this to make sure the hash values for this method are available
            self.Ctrl.setImageHashes(hashName=self.hashMethod)
        self.Ctrl.onConditionChanged()

    def matchingGroups(self, candidates):

        def theymatch(md5a, md5b):
            foaHash = HA.hexstring_to_array(getattr(self.Ctrl.FODict[md5a][0], self.hashMethod))
            fobHash = HA.hexstring_to_array(getattr(self.Ctrl.FODict[md5b][0], self.hashMethod))
            return HA.array_to_array_distance(foaHash,fobHash) <= self.hashThresh.get()

        md5s = []
        for a, b in candidates:
            md5s.append(a)
            md5s.append(b)
        md5s = list(set(md5s))
        md5s.sort()

        matches = [(md5a, md5b) for md5a, md5b in candidates if theymatch(md5a, md5b)]

        matchingGroups = []
        for thismd5 in md5s:
            # put atleast the first image in each matchingGroups
            dummy = [thismd5]
            dummy.extend([ md5b for md5a, md5b in matches if md5a == thismd5 ])
            dummy = list(set(dummy))
            dummy.sort()
            matchingGroups.append(dummy)

        matchingGroups.sort()

        return matchingGroups
