from tkinter import ttk


class DelayedScale(ttk.Scale):
    """A ttk scale widget that only fires the command when the mouse is released
       if using the mouse to drag the slider
       We also modify the behaviour to always returns integer values"""

    def __init__(self, parent, *args, command=None, resolution=None, **kwargs):
        self.realcommand = command
        self._step = int(resolution) if resolution else 1
        super().__init__(parent, *args, command=self._command, **kwargs)
        self.bind("<ButtonPress-1>", self._scalePressed)
        self.bind("<ButtonRelease-1>", self._scaleReleased)
        self.bind("<Key-Left>", self._leftPressed)
        self.bind("<Key-Right>", self._rightPressed)
        self.bind("<ButtonPress-1>", self._scalePressed)
        self._mouseIsPressed = False

    def _leftPressed(self, *args):
        self.set(int(self.get()-self._step))
        return "break"

    def _rightPressed(self, *args):
        self.set(int(self.get()+self._step))
        return "break"

    def _scalePressed(self, *args):
        self._mouseIsPressed = True

    def _scaleReleased(self, *args):
        self._mouseIsPressed = False
        self._command()

    def _command(self, *args):
        val = self.get()
        rval = int(val)
        if val != rval:
            super().set(rval)
            return
        self.mousedowncommand()
        if self._mouseIsPressed:
            return
        if self.realcommand:
            self.realcommand()

    def get(self, *args):
        return int(super().get())

    def set(self, value):
        super().set(int(value))

    def mousedowncommand(self, *args):
        pass

class LabelScale(ttk.Frame):
    "A scale widget (slider) with a label to indicate its value"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        self._Label = ttk.Label(self, text="")
        self._Label.pack()

        self._Scale = DelayedScale(self, *args, **kwargs)
        self._Scale.pack()
        self._Scale.mousedowncommand = self._updateLabel
        self._Label.config(text=self._int2label(self._Scale.get()))

    def _int2label(self, i):
        return str(i)

    def _updateLabel(self):
        self._Label.config(text=self._int2label(self._Scale.get()))

    def get(self):
        return self._Scale.get()

    def set(self, val):
        self._Label.config(text=self._int2label(val))
        self._Scale.set(val)

    def focus_set(self):
        self._Scale.focus_set()

    def config(self, *args, **kwargs):
        self._Scale.config(*args, **kwargs)

    def bind(self, *args, **kwargs):
        self._Scale.bind(*args, **kwargs)


class TextScale(LabelScale):
    "A scale widget (slider) with text rather than numerical labels"

    def __init__(self, parent, *args, textLabels=None, **kwargs):
        self.textLabels = textLabels
        super().__init__(parent, *args, from_=0, to=len(self.textLabels)-1, **kwargs)

    def _int2label(self, i):
        return self.textLabels[i]

    def get(self):
        return self._int2label(self._Scale.get())

    def set(self, val):
        self._Label.config(text=val)
        self._Scale.set(self.textLabels.index(val))
