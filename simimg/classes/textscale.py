import tkinter as tk

class TextScale(tk.Frame):
    "A scale widget (slider) with text rather than numerical labels"
    def __init__(self, parent, *args,
                 topLabel='',
                 textLabels=None,
                 onChange=None,
                 initialInt=None,
                 **kwargs):
        super().__init__(parent)

        # eventhough this is a scale widget we need a Frame to hold both
        # the label and the values. We reuse the orginal label to show the values
        if not initialInt:
            initialInt=0

        self.textValue = textLabels[initialInt]
        self.textLabelsDict = {key: value for key, value in enumerate(textLabels) }
        self.onChange = onChange
        self.TSScaleIntVar = tk.IntVar()
        self.TSScaleIntVar.set(initialInt)
        self.TSValueLabel = tk.Label(self, text=self.textValue)
        self.TSScale = tk.Scale(self,
                                from_=min(self.textLabelsDict),
                                to=max(self.textLabelsDict),
                                label='',
                                showvalue=False,
                                variable=self.TSScaleIntVar,
                                command=self._command,
                                *args, **kwargs
        )
        if topLabel:
            self.TSTopLabel = tk.Label(self, text=topLabel)
            self.TSTopLabel.pack()
        self.TSValueLabel.pack()
        self.TSScale.pack()

    def _command(self, val):
        self.textValue = self.textLabelsDict[int(val)]
        self.TSValueLabel.config(text=self.textValue)
        self.onChange()

    def focus_set(self):
        self.TSScale.focus_set()

    def config(self, state=None, *args, **kwargs):
        super().config()
        if state:
            self.TSScale.config(state=state)
