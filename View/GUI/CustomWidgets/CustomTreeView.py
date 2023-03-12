import tkinter.ttk as ttk

from customtkinter import ThemeManager

from View.GUI.CustomWidgets.CustomWidget import CustomWidget


class CustomTreeView(ttk.Treeview, CustomWidget):

    def __init__(self, parent, **kwargs):
        self.style = ttk.Style()
        super().__init__(parent, style="Custom.Treeview", **kwargs)
        CustomWidget.__init__(self, parent)
        self.bind("<MouseWheel>", lambda _: self.focus_set())

    def change_widget_style(self):
        treeview_dict = ThemeManager.theme["CustomTreeView"]
        background = self.themed_color(treeview_dict["background_color"])
        text_color = self.themed_color(treeview_dict["text_color"])
        field_background = self.themed_color(treeview_dict["entry_background_color"])
        selected_field_background = self.themed_color(treeview_dict["entry_selected_background_color"])
        selected_text_color = self.themed_color(treeview_dict["text_selected_color"])

        self.style.configure("Custom.Treeview",
                             background=background,
                             foreground=text_color,
                             rowheight=25,
                             borderwidth=0,
                             fieldbackground=field_background)
        self.style.map('Custom.Treeview', background=[('selected', selected_field_background)],
                       foreground=[('selected', selected_text_color)])
        self.configure(style="Custom.Treeview")

    def destroy(self):
        self.remove_tracker()
        super().destroy()
