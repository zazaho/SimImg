import tkinter as tk

class TextScale(tk.Scale):
    "A scale widget (slider) with text rather than numerical labels"
    def __init__(self, parent,
                 label='',
                 textLabels=None,
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
        self.textValue = textLabels[0]
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

    def TS_Set_Label(self, val):
        self.textValue = self.textLabelsDict[int(val)]
        self.Scale.config(label=self.textValue)
        self.command()
