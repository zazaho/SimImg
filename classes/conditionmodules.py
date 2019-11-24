''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich
    A switch to make this criterion obligatory (must match)
    A method to determine if which imagepairs from a list of pairs match
'''

import tkinter as tk


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

class ConditionFrame(tk.Frame):
    name = ''
    " A frame that holds one selection criterion with options"
    def __init__(self, parent):
        super().__init__(parent)

        self.config(relief="groove",borderwidth=3)
        self.width = 150

        self.label = None
        self.activeBool = tk.BooleanVar()
        self.mustMatchBool = tk.BooleanVar()

        self.make_base_widgets()


    def make_base_widgets(self):
        self.label = tk.Label(self, text=self.name, anchor='w')
        self.activeToggle = tk.Checkbutton(self,
                                           text="Active",
                                           anchor='w',
                                           variable=self.activeBool,
                                           command=self.activeToggled
        )
        self.mustMatchToggle = tk.Checkbutton(self,
                                              text="Must Match",
                                              anchor='w',
                                              variable=self.mustMatchBool,
                                              command=self.mustMatchToggled
        )

        self.label.pack(fill='x')
        self.activeToggle.pack(fill='x')
        self.mustMatchToggle.pack(fill='x')

    def activeToggled(self):
        pass

    def mustMatchToggled(self):
        pass

class HashCondition(ConditionFrame):
    name = 'HASHING DISTANCE'
    def __init__(self, parent):
        super().__init__(parent)
        self.make_additional_widgets()
        
    def make_additional_widgets(self):
        self.extra = tk.Scale(self,
                              from_= 1, to=100,
                              label='Threshold',
                              orient=tk.HORIZONTAL)
        self.extra.pack()

class CameraCondition(ConditionFrame):
    name = 'SAME CAMERA'
    def __init__(self, parent):
        super().__init__(parent)
        self.missingMatchesCheck = None
        self.missingMatchesBool = tk.BooleanVar()
        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingMatchesBool,
                                                  command=self.missingMatchesToggled,
                                                  anchor='w')
        self.missingMatchesCheck.pack()

    def missingMatchesToggled(self):
        pass

class DateCondition(ConditionFrame):
    name = 'Close in time'
    def __init__(self, parent):
        super().__init__(parent)
        self.missingMatchesCheck = None
        self.missingMatchesBool = tk.BooleanVar()

        self.timeDifferenceScale = None
        self.timeDifferenceValue = tk.StringVar()
        self.scalelabels = ['1 minute','10 minutes','1 hour','1 day','1 week','1 month','1 year']

        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingMatchesBool,
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
