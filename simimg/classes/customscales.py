import tkinter as tk
from tkinter import ttk


class DelayedScale(tk.Scale):
    '''A scale widget that only fires the command when the mouse is released
    if using the mouse to drag the slider'''

    def __init__(self, parent, *args, command=None, **kwargs):
        super().__init__(parent, *args, command=self._command, **kwargs)
        self.command = command
        self.bind('<ButtonPress-1>', self._scalePressed)
        self.bind('<ButtonRelease-1>', self._scaleReleased)
        self._mouseIsPressed = False

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._command()

    def _command(self, *args):
        self.mousedowncommand()
        if self._mouseIsPressed:
            return
        self.command()

    def mousedowncommand(self, *args):
        pass


class TextScale(ttk.Frame):
    'A scale widget (slider) with text rather than numerical labels'

    def __init__(self, parent, *args,
                 topLabel='',
                 textLabels=None,
                 **kwargs):
        super().__init__(parent)

        self.textLabels = textLabels

        if topLabel:
            self.TSTopLabel = ttk.Label(self, text=topLabel)
            self.TSTopLabel.pack()

        self.TSValueLabel = ttk.Label(self, text='')
        self.TSValueLabel.pack()

        self.TSScale = DelayedScale(
            self,
            from_=0,
            to=len(self.textLabels)-1,
            label='',
            showvalue=False,
            *args,
            **kwargs
        )
        self.TSScale.mousedowncommand = self._updateTextLabel
        self.TSScale.pack()
        self.TSValueLabel.config(text=self.textLabels[self.TSScale.get()])

    def _updateTextLabel(self):
        self.TSValueLabel.config(text=self.textLabels[self.TSScale.get()])

    def get(self):
        return self.textLabels[self.TSScale.get()]

    def set(self, text):
        self.TSValueLabel.config(text=text)
        self.TSScale.set(self.textLabels.index(text))

    def focus_set(self):
        self.TSScale.focus_set()

    def config(self, state=None, *args, **kwargs):
        super().config()
        if state:
            self.TSScale.config(state=state)
