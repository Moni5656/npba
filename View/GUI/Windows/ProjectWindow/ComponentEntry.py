import tkinter as tk

from Controller.GUI.GUIController import GUIController
from View.Observer import Observer


class ComponentEntry(Observer):

    def __init__(self, project_window, controller: GUIController, parent_id, component):
        super().__init__(component)
        self.tree = project_window.treeview
        self.project_window = project_window
        self.controller = controller

        self.entry = self.tree.insert(parent_id, tk.END, text=component.name, tags=(str(component.id), "all"))

        if component.is_selected:
            self.tree.focus(self.entry)
            self.tree.selection_add(self.entry)

    def delete(self) -> None:
        """
        Deletes the current entry from the treeview and unsubscribes from observed component.
        """
        self.tree.delete(self.entry)
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None

    def set_active(self) -> None:
        """
        Sets activity of the current component in the model.
        """
        self.controller.on_component_click(self.observed_subject)

    def set_shift_active(self) -> None:
        """
        Activates multiple entries in the model.
        """
        self.controller.on_component_shift_click(self.observed_subject)

    def update_(self, updated_component) -> None:
        if self.project_window.is_user_click:
            return

        focus_entry = False
        if updated_component[1] == "set_selection":
            if self.observed_subject.is_selected:
                self.tree.selection_add(self.entry)
                focus_entry = True
            else:
                self.tree.selection_remove(self.entry)
        elif updated_component[1] == "set_parameter":
            self.tree.item(self.entry, text=self.observed_subject.name)

        if focus_entry:
            self.tree.focus(self.entry)
            self.tree.see(self.entry)
