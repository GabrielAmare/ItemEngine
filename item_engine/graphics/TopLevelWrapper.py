from __future__ import annotations

from tkinter import *
from typing import Optional, TypeVar, Type

__all__ = ["TopLevelWrapper"]

W = TypeVar("W", bound=Widget)


class TopLevelWrapper(Toplevel):
    def __init__(self, root, **cfg):
        super().__init__(root, **cfg)
        self.widget: Optional[Widget] = None

    def of(self, cls: Type[W], **kwargs) -> W:
        if self.widget:
            self.widget.destroy()

        self.widget = cls(self, **kwargs)
        self.widget.pack(side=TOP, fill=BOTH, expand=True)

        return self.widget
