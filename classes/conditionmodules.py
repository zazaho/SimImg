''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich
    A switch to make this criterion obligatory (must match)
    A method to determine if which imagepairs from a list of pairs match
'''

import tkinter as tk

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
        self.timeDifferenceValue = tk.IntVar()
        self.timeDifferenceCustomValueLabel = None
        self.timeDifferenceCustomValueVar = tk.StringVar()
        self.make_additional_widgets()

    def make_additional_widgets(self):
        self.missingMatchesCheck = tk.Checkbutton(self,
                                                  text="Missing Matches",
                                                  variable=self.missingMatchesBool,
                                                  command=self.missingMatchesToggled,
                                                  anchor='w')
        self.missingMatchesCheck.pack()
        self.timeDifferenceValue = tk.IntVar()
        
        self.scalelabels = {
            1:'1 minute',
            2:'10 minutes',
            3:'1 hour',
            4:'1 day',
            5:'1 week',
            6:'1 month',
            7:'1 year'
        }

        label = tk.Label(self,text='Maximum Difference')
        label.pack()
        self.timeDifferenceScale = tk.Scale(self,
                                            from_=min(self.scalelabels),
                                            to=max(self.scalelabels),
                                            label=self.scalelabels[1],
                                            showvalue=False,
                                            command=self.TDS_set_label,
                                            variable=self.timeDifferenceValue,
                                            orient=tk.HORIZONTAL)
        self.timeDifferenceScale.pack()
        
    def missingMatchesToggled(self):
        pass

    def TDS_set_label(self,val):
        self.timeDifferenceScale.config(label=self.scalelabels[int(val)])
