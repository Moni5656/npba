import tkinter as tk

import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomCanvas import CustomCanvas
from View.GUI.CustomWidgets.CustomFrame import CustomFrame
from View.GUI.CustomWidgets.CustomScrollbar import CustomScrollbar
from utils.utils import OS


# Taken and modified from https://gist.github.com/JackTheEngineer/81df334f3dcff09fd19e4169dd560c59

class ScrolledFrame(ctk.CTkFrame):

    def __init__(self, parent, fg_color=None, bg_color=None, *args, **kw):
        if fg_color is None:
            fg_color = ThemeManager.theme["color_scale"]["inner"]
        if bg_color is None:
            bg_color = ThemeManager.theme["color_scale"]["outer"]
        super().__init__(parent, fg_color=fg_color, bg_color=bg_color, *args, **kw)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        def v_geometry_command(s):
            s.grid(sticky="ns", column=1, row=0, padx=(0, 3), pady=3)

        def h_geometry_command(s):
            s.grid(sticky="ew", column=0, row=1, padx=3, pady=(0, 3))

        vscrollbar = CustomScrollbar(self, geometry_command=v_geometry_command)
        hscrollbar = CustomScrollbar(self, geometry_command=h_geometry_command, orientation="horizontal")
        self._scroll_canvas = CustomCanvas(self, bd=0, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
        self._scroll_canvas.grid(column=0, row=0, sticky="news", padx=3, pady=3)
        vscrollbar.configure(command=self._scroll_canvas.yview)
        hscrollbar.configure(command=self._scroll_canvas.xview)

        self.scrolled_frame = CustomFrame(self._scroll_canvas)
        self._interior_id = self._scroll_canvas.create_window(0, 0, window=self.scrolled_frame, anchor=tk.NW)
        self._scroll_canvas.config(scrollregion=(0, 0, 0, 0))

        self._scroll_canvas.bind('<Configure>', self._resize_viewport)
        self.scrolled_frame.bind('<Configure>', self._reset_scroll_region, add=True)

        self._scroll_canvas.bind('<Enter>', self._bind_to_mousewheel)
        self._scroll_canvas.bind('<Leave>', self._unbind_to_mousewheel)

    def _bind_to_mousewheel(self, _):
        """
        Binds methods to the mousewheel.

        :param _:
        """
        self._scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._scroll_canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _unbind_to_mousewheel(self, _):
        """
        Unbind methods from the mousewheel.

        :param _:
        :return:
        """
        self._scroll_canvas.unbind_all("<MouseWheel>")
        self._scroll_canvas.unbind_all("<Shift-MouseWheel>")

    def _on_mousewheel(self, event):
        """
        Handles mousewheel events.

        :param event: event
        """
        if self.scrolled_frame.winfo_height() <= self._scroll_canvas.winfo_height():
            return
        delta = (event.delta // 120) if OS.Windows else event.delta
        self._scroll_canvas.yview_scroll(-1 * delta, "units")

    def _on_shift_mousewheel(self, event):
        """
        Handles Shift+Mousewheel events.

        :param event: event
        """
        if self.scrolled_frame.winfo_width() <= self._scroll_canvas.winfo_width():
            return
        delta = (event.delta // 120) if OS.Windows else event.delta
        self._scroll_canvas.xview_scroll(-1 * delta, "units")

    def _on_scrollbar(self, _, units, _2):
        """
        Handles scrollbar events.

        :param _:
        :param units: scrollbar units
        :param _2:
        """
        if self.scrolled_frame.winfo_height() <= self._scroll_canvas.winfo_height():
            return
        self._scroll_canvas.yview_scroll(units, "units")

    def _reset_scroll_region(self, _):
        """
        Resets the scroll region.
        :param _:
        """
        size = self._scroll_canvas.bbox("all")
        self._scroll_canvas.configure(scrollregion=size)

    def _resize_viewport(self, _):
        """
        Resizes the viewport to the maximum width.

        :param _:
        """
        width = max(self._scroll_canvas.winfo_width(), self.scrolled_frame.winfo_reqwidth())
        self._scroll_canvas.itemconfigure(self._interior_id, width=width)
