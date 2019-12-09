import tkinter as tk

class TextScale(tk.Frame):
    "A scale widget (slider) with text rather than numerical labels"
    def __init__(self, parent,
                 topLabel='',
                 textLabels=None,
                 onChange=None,
                 initialInt=None,
                 *args, **kwargs):
        super().__init__(parent)

        # eventhough this is a scale widget we need a Frame to hold both
        # the label and the values. We reuse the orginal label to show the values
        if not initialInt:
            initialInt=0
            
        self.textValue = textLabels[initialInt]
        self.textLabelsDict = {key: value for key, value in enumerate(textLabels) }
        self.onChange = onChange
        self.TSScaleIntVar = tk.IntVar()
        self.TSlabel = tk.Label(self, text=topLabel)
        self.TSScale = tk.Scale(self,
                                from_=min(self.textLabelsDict),
                                to=max(self.textLabelsDict),
                                label=self.textValue,
                                showvalue=False,
                                variable=self.TSScaleIntVar,
                                command=self.TScommand,
                                *args, **kwargs
        )
        self.TSScale.set(initialInt)
        self.TSlabel.pack()
        self.TSScale.pack()

    def TScommand(self, val):
        self.textValue = self.textLabelsDict[int(val)]
        self.TSScale.config(label=self.textValue)
        self.onChange()
