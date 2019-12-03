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

    def somethingChanged(self):
        pass

    def matchingPairs(self, candidates):
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
                                    command=self.threshScaleChange,
                                    orient=tk.HORIZONTAL)
        self.hashCombo.pack()
        self.threshScale.pack()

    def hashComboMethodChange(self, event):
        oldHashMethod = self.hashMethod
        newHashMethod = self.hashCombo.get()
        if oldHashMethod != newHashMethod:
            self.hashMethod = newHashMethod
            self.somethingChanged()

    def threshScaleChange(self, event):
        self.somethingChanged()

    def somethingChanged(self):
        if self.active:
            #Call this to make sure the hash values for this method are available
            self.Ctrl.setImageHashes(hashName=self.hashMethod)
        self.Ctrl.onConditionChanged()

    def matchingPairs(self, candidates):
        matches = []
        for md5a, md5b in candidates:
            foa = self.Ctrl.FODict[md5a][0]
            fob = self.Ctrl.FODict[md5b][0]
            foaHash = getattr(foa, self.hashMethod)
            fobHash = getattr(fob, self.hashMethod)
            if abs(hex_to_hash(foaHash) - hex_to_hash(fobHash)) <= self.hashThresh.get():
                matches.append((md5a, md5b))
        return matches


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

    def somethingChanged(self):
        self.Ctrl.onConditionChanged()

    def matchingPairs(self, candidates):
        matches = []
        missKeep = self.missingMatches.get()
        for md5a, md5b in candidates:
            foaCam = self.Ctrl.FODict[md5a][0].CameraModel()
            fobCam = self.Ctrl.FODict[md5b][0].CameraModel()
            if missKeep and (foaCam == '' or fobCam == ''):
                matches.append((md5a, md5b))
                continue
            if foaCam == fobCam:
                matches.append((md5a, md5b))

        return matches


class DateCondition(ConditionFrame):
    name = 'CLOSE IN TIME'
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.missingMatchesCheck = None
        self.missingMatches = tk.BooleanVar()

        self.timeDifferenceScale = None
        self.timeDifferenceValue = tk.StringVar()
        self.scalelabels = ['1 minute','10 minutes','1 hour','1 day','1 week','1 month','1 year']

        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingMatches,
                                                  command=self.missingMatchesToggled,
                                                  anchor='w')
        self.missingMatchesCheck.pack()
        self.timeDifferenceScale = TextScale(self,
                                             textLabels=self.scalelabels,
                                             label='Maximum Difference', 
                                             variable=self.timeDifferenceValue,
                                             command=self.TDChanged,
                                             orient=tk.HORIZONTAL)
        self.timeDifferenceScale.topFrame.pack()
        
    def missingMatchesToggled(self):
        pass

    def TDChanged(self):
        print(self.timeDifferenceScale.variable)
        
    def TDS_set_label(self,val):
        self.timeDifferenceScale.config(label=self.scalelabels[int(val)])




class TextScale(tk.Scale):
    "A scale widget (slider) with text rather than numerical labels"
    def __init__(self, parent,
                 label='',
                 textLabels=None,
                 variable=None,
                 command=None,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # eventhough this is a scale widget we need a Frame to hold both
        # the label and the values. We reuse the orginal label to show the values
        self.topFrame = tk.Frame(parent)
        self.textLabelsDict = {key: value for key, value in enumerate(textLabels) }
        self.label = tk.Label(self.topFrame, text=label)
        self.label.pack()
        self.Scale = tk.Scale(self.topFrame, *args, **kwargs)
        self.NumericalValue = tk.IntVar()
        self.variable = variable
        self.command = command
        
        self.Scale = tk.Scale(self.topFrame,
                              from_=min(self.textLabelsDict),
                              to=max(self.textLabelsDict),
                              label=self.textLabelsDict[0],
                              showvalue=False,
                              command=self.TS_Set_Label,
                              variable=self.NumericalValue,
                              *args, **kwargs)
        self.Scale.pack()

    def TS_Set_Label(self,val):
        self.variable = self.textLabelsDict[int(val)]
        self.Scale.config(label=self.variable)
        self.command()
