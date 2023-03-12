from tkinter import font as tkfont

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomCanvas import CustomCanvas
from View.GUI.DragNDrop import DraggableContainer, DropTarget
from utils.utils import OS


class SelectionBarButton(CustomCanvas, DropTarget):
    def __init__(self, parent, name, command, angle):
        font = tkfont.nametofont("TkTextFont")
        # default values for horizontal text
        str_length = font.measure(name) + 10
        str_height = font.metrics()["linespace"] + 2
        x = 5
        y = 1
        # set values for vertical text
        if angle != 0:
            tmp = str_length
            str_length = str_height
            str_height = tmp
            x = 18
            y = 7

        self.is_selected = True
        self.selection_bar = parent
        super().__init__(parent, width=str_length, height=str_height)
        self.bind(OS.left_mouse_button, command)
        self.text = self.create_text(x, y, anchor="nw", angle=angle, text=name)

    def set_selected(self):
        """
        Sets the button to selected.
        """
        self.is_selected = True
        text_color = self.themed_color(ThemeManager.theme["SelectionBar"]["button_active_text"])
        bg_color = self.themed_color(ThemeManager.theme["SelectionBar"]["button_active"])
        self.itemconfig(self.text, fill=text_color)
        self.configure(bg=bg_color, highlightthickness=0)

    def set_inactive(self):
        """
        Deselects the button.
        """
        self.is_selected = False
        text_color = self.themed_color(ThemeManager.theme["SelectionBar"]["button_inactive_text"])
        bg_color = self.themed_color(ThemeManager.theme["SelectionBar"]["button_inactive"])
        self.itemconfig(self.text, fill=text_color)
        self.configure(bg=bg_color, highlightthickness=0)

    def set_appearance_mode(self, mode: str):
        super().set_appearance_mode(mode)
        if self.is_selected:
            self.set_selected()
        else:
            self.set_inactive()

    def get_container(self) -> DraggableContainer:
        return self.selection_bar.get_container()
