import tkinter as tk
from idlelib.tooltip import Hovertip

from View.GUI.CustomWidgets.CustomTreeView import CustomTreeView
from View.GUI.CustomWidgets.EntryPopup import EntryPopup
from View.Observer import Observer
from utils.utils import OS


class ConfigurationTreeView(CustomTreeView, Observer):

    def __init__(self, parent, controller, configurations):
        super().__init__(parent, selectmode="extended",
                         columns="value",
                         height=0,
                         show="tree"
                         )
        self.controller = controller
        self.configurations = {}
        self.subscribed_configurations = {}
        for configuration in configurations:
            self.add(configuration)
        self.bind("<<TreeviewOpen>>", lambda _: self.on_height_change())
        self.bind("<<TreeviewClose>>", lambda _: self.on_height_change())
        Hovertip(self, text="Click to edit the parameter values", hover_delay=500)

    def update_(self, updated_component):
        if updated_component[1] == "set_parameter":
            new_values = updated_component[0].make_parameter_dict()
            group_id = updated_component[0].group_id
            entry_id = self.configurations[group_id]
            name = self.controller.model_facade.network.configurations[updated_component[0].group_id].name
            self.item(entry_id, text=name)
            for child in self.get_children(entry_id):
                parameter_name = self.item(child, "text")
                new_value = new_values[parameter_name]
                self.item(child, values=[new_value])

    def add(self, configuration):
        """
        Adds a new configuration to the configuration treeview.

        :param configuration: configuration object
        """
        configuration.subscribe(self)
        self.subscribed_configurations[configuration.group_id] = configuration
        name = self.controller.model_facade.network.configurations[configuration.group_id].name
        entry_id = self.insert("", text=name, index=tk.END)
        self.configurations[configuration.group_id] = entry_id

        for parameter, value in configuration.make_parameter_dict().items():
            self.insert(entry_id, text=parameter, values=[value], index=tk.END, tags=configuration.group_id)
        self.tag_bind(configuration.group_id, OS.left_mouse_button,
                      lambda e: self.on_edit_click(e, configuration))
        self.tag_bind(configuration.group_id, "<Return>",
                      lambda e: self.on_edit_click(e, configuration))
        self.tag_bind(configuration.group_id, "<space>",
                      lambda e: self.on_edit_click(e, configuration))
        self.on_height_change()

    def remove(self, group_id):
        """
        Removes a configuration from the configuration treeview.

        :param group_id: group ID of the configuration
        """
        if group_id not in self.subscribed_configurations:
            return
        config = self.subscribed_configurations[group_id]
        config.unsubscribe(self)
        if group_id in self.subscribed_configurations:
            del self.subscribed_configurations[group_id]
        entry_id = self.configurations[group_id]
        self.delete(entry_id)
        self.on_height_change()

    def update_configuration(self, configuration, parameter_name, new_value):
        """
        Updates the value of a configuration's parameter in the model.

        :param configuration: configuration object
        :param parameter_name: name of the parameter
        :param new_value: new value
        """
        old_config = configuration.make_parameter_dict()
        old_config[parameter_name] = new_value
        self.controller.update_configuration_parameters(configuration, old_config)

    def on_edit_click(self, event, configuration):
        """
        Opens an entry popup above the item's column and row to edit the entry.
        """
        if event.type == tk.EventType.KeyPress:
            row_id = self.selection()[0]
        else:
            row_id = self.identify_row(event.y)

        column = "#1"
        x, y, width, height = self.bbox(row_id, column)
        y_offset = height // 2

        value = self.item(row_id, "values")[0]
        parameter_name = self.item(row_id, "text")
        entry = EntryPopup(self, value,
                           lambda new_value: self.update_configuration(configuration, parameter_name, new_value))
        entry.place(x=x, y=y + y_offset, anchor="w", width=width)

    def destroy(self):
        for configuration in self.subscribed_configurations.values():
            configuration.unsubscribe(self)
        self.observed_subject = None
        self.subscribed_configurations = {}
        super().destroy()

    def on_height_change(self):
        """
        Adjusts the height of the treeview according to the number of rows to avoid scrolling.
        """
        self.after(100, lambda: self.configure(height=self.get_current_height()))

    def get_current_height(self) -> int:
        """
        Returns the current height of the treeview.

        :return: number of rows
        """
        height = 0
        for child in self.get_children():
            height += self._get_height(child)
        return height

    def _get_height(self, row_id):
        """
        Helper method for get_current_height.

        :param row_id: ID of the row
        """
        if self.item(row_id, "open"):
            height = 1
            for child in self.get_children(row_id):
                height += self._get_height(child)
            return height
        else:
            return 1
