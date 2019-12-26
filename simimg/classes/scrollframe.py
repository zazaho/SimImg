import tkinter as tk

# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    ''' Frame with two scrollbars two be able to view content bigger than the window '''
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self)
        self.viewPort = tk.Frame(self.canvas)
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=self.hsb.set)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.viewPort,
            anchor="nw",
            tags="self.viewPort"
        )
        self.viewPort.bind("<Configure>", self._frameConfigure)
        parent.bind("<MouseWheel>", self._mouseScroll)
        parent.bind("<Button-4>", self._mouseScroll)
        parent.bind("<Button-5>", self._mouseScroll)
        self.hsb.pack(side="bottom", fill="x")
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

    def _frameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _mouseScroll(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return
        if event.num == 5:
            move = 1
        else:
            move = -1
        self.canvas.yview_scroll(move, "units")
