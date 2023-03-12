import customtkinter as ctk
from customtkinter import ThemeManager


# based on https://stackoverflow.com/questions/41095385/autohide-tkinter-canvas-scrollbar-with-pack-geometry
class CustomScrollbar(ctk.CTkScrollbar):

    def __init__(self, parent, geometry_command=None, bg_color=None, fg_color=None,
                 **kwargs):
        if geometry_command is None:
            def geometry_command(_): print(self, "missing")
        self.geometry_command = geometry_command
        if bg_color is None:
            bg_color = ThemeManager.theme["color_scale"]["inner"]
        if fg_color is None:
            fg_color = ThemeManager.theme["color_scale"]["inner"]
        super().__init__(parent, bg_color=bg_color, fg_color=fg_color, **kwargs)

    def set(self, lo, hi):
        """
        Overrides the set method such that the scrollbar only shows up when it is required.
        :param lo: start point of the widget
        :param hi: end point of the widget
        """
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.unmap()
        else:
            self.geometry_command(self)
        super().set(lo, hi)

    def unmap(self):
        """
        Hides the scrollbar.
        """
        manager = self.winfo_manager()
        if manager == "pack":
            self.pack_forget()
        elif manager == "grid":
            self.grid_forget()
        elif manager == "place":
            self.place_forget()
