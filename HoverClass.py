from tkinter import *
import re

class HoverInfo(Menu):
    def __init__(self, parent, text, command=None):
        self._com = command
        Menu.__init__(self,parent, tearoff=0)
        if not isinstance(text, str):
            raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
        toktext=re.split('\n', text)
        for t in toktext:
            self.add_command(label = t)
        self._displayed=False
        self.master.bind("<Enter>",self.Display )
        self.master.bind("<Leave>",self.Remove )

    def __del__(self):
       self.master.unbind("<Enter>")
       self.master.unbind("<Leave>")

    def Display(self,event):
       if not self._displayed:
          self._displayed=True
          self.post(event.x_root, event.y_root)
       if self._com != None:
          self.master.unbind_all("<Return>")
          self.master.bind_all("<Return>", self.Click)

    def Remove(self, event):
     if self._displayed:
       self._displayed=False