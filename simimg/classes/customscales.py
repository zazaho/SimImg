import tkinter as tk
from tkinter import ttk

class DelayedScale(tk.Scale):
    '''A scale widget that only fires the command when the mouse is released
    if using the mouse to drag the slider'''
    def __init__(self, parent, *args, command=None, **kwargs):
        super().__init__(parent, *args, command=self._command, **kwargs)
        self.command = command
        self.bind("<ButtonPress-1>", self._scalePressed)
        self.bind("<ButtonRelease-1>", self._scaleReleased)
        self._mouseIsPressed = False

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._command()

    def _command(self, *args):
        if self._mouseIsPressed:
            return
        self.command()

class TextScale(ttk.Frame):
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
        self.TSValueLabel = ttk.Label(self, text=self.textValue)
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
            self.TSTopLabel = ttk.Label(self, text=topLabel)
            self.TSTopLabel.pack()
        self.TSValueLabel.pack()
        self.TSScale.pack()
        self.TSScale.bind("<ButtonPress-1>", self._scalePressed)
        self.TSScale.bind("<ButtonRelease-1>", self._scaleReleased)
        self._mouseIsPressed = False

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._command(self.TSScaleIntVar.get())

    def _command(self, val):
        self.textValue = self.textLabelsDict[int(val)]
        self.TSValueLabel.config(text=self.textValue)
        # do nothing while the mouse is down
        if self._mouseIsPressed:
            return
        self.onChange()

    def focus_set(self):
        self.TSScale.focus_set()

    def config(self, state=None, *args, **kwargs):
        super().config()
        if state:
            self.TSScale.config(state=state)
