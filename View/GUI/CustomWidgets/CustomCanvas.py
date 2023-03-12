import tkinter as tk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget


class CustomCanvas(tk.Canvas, CustomWidget):

    def __init__(self, parent, canvas_color=None, **kwargs):
        if canvas_color is None:
            canvas_color = ThemeManager.theme["color_scale"]["inner"]
        self.canvas_color = canvas_color
        super().__init__(parent, highlightthickness=0, **kwargs)
        CustomWidget.__init__(self, parent)

    def change_widget_style(self):
        bg = self.themed_color(self.canvas_color)
        self.configure(bg=bg)

    def destroy(self):
        self.remove_tracker()
        super().destroy()

    def create_circle(self, x, y, r, **kwargs):
        """
        Used to draw a circle with certain arguments.
        :param self: NodeView
        :param x: x coordinate
        :param y: y coordinate
        :param r: radius
        :param kwargs: additional canvas item arguments (color, etc...)
        :return: a circle which can be added to the canvas
        """
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)
