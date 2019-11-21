''' Classes that implement different criteria for selecting matching images.
    It should have at least:
    A name label
    A active swtich
    A switch to make this criterion obligatory (must match)
    A method to determine if which imagepairs from a list of pairs match
'''

import tkinter as tk

class ConditionFrame(tk.Frame):
    " A frame that holds one selection criterion with options"
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config(relief="groove",borderwidth=3)
        self.width = 150

        self.label = None

        self.activeToggle = None
        self.active = "normal"

        self.mustMatchToggle = None
        self.mustMatch = "normal"

        self.SetMyName()
        self.make_base_widgets()
        self.make_additional_widgets()
        
    def Matches(self, listofpairs, listoffileobjects):
        pass

    def SetMyName(self):
        self.name = ''
        
    def make_base_widgets(self):
        self.label = tk.Label(self, text=self.name, anchor='w')
        self.activeToggle = tk.Checkbutton(self,
                                           text="Active",
                                           state=self.active,
                                           anchor='w',
                                           command=self.activeToggled
        )
        self.mustMatchToggle = tk.Checkbutton(self,
                                              text="Must Match",
                                              state=self.mustMatch,
                                              anchor='w',
                                              command=self.mustMatchToggled
        )

        self.label.pack(fill='x')
        self.activeToggle.pack(fill='x' )
        self.mustMatchToggle.pack(fill='x' )

    def make_additional_widgets(self):
        pass
    
    def activeToggled(self):
        self.active = not self.active

    def mustMatchToggled(self):
        self.mustMatch = not self.mustMatch

class HashCondition(ConditionFrame):
    def SetMyName(self):
        self.name = 'Hash distance'

    def make_additional_widgets(self):
        self.extra = tk.Checkbutton(self,
                                    text="Wow",
                                    state=self.active,
                                    anchor='w')
        self.extra.pack()
