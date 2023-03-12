import tkinter as tk
from uuid import UUID

import customtkinter as ctk
from customtkinter import ThemeManager

from Model.Network.Edge import Edge
from Model.Network.Flow import Flow
from Model.Network.Network import Network
from Model.Network.Node import Node
from View.GUI.BaseApplication.Position import Position
from View.GUI.CustomWidgets.CustomScrollbar import CustomScrollbar
from View.GUI.CustomWidgets.CustomTreeView import CustomTreeView
from View.GUI.CustomWidgets.EntryPopup import EntryPopup
from View.GUI.Windows import WindowInterface
from View.GUI.Windows.ProjectWindow.ComponentEntry import ComponentEntry
from View.Observer import Observer
from utils.utils import OS


class ProjectWindow(WindowInterface, ctk.CTkFrame, Observer):

    @staticmethod
    def get_title() -> str:
        return "Project"

    @staticmethod
    def get_start_position() -> Position:
        return Position.TopLeft

    @staticmethod
    def get_importance():
        return 5

    def __init__(self, parent, controller, network):
        WindowInterface.__init__(self, parent, controller, network)
        bg_color = ThemeManager.theme["color_scale"]["outer"]
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        ctk.CTkFrame.__init__(self, parent, fg_color=fg_color, bg_color=bg_color)
        Observer.__init__(self, network)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        def v_geometry_command(s): s.grid(sticky="ns", column=1, row=0, padx=(0, 3), pady=3)

        def h_geometry_command(s): s.grid(sticky="ew", column=0, row=1, padx=3, pady=(0, 3))

        vscrollbar = CustomScrollbar(self, geometry_command=v_geometry_command)
        hscrollbar = CustomScrollbar(self, geometry_command=h_geometry_command, orientation="horizontal")
        self.treeview = CustomTreeView(self, show="tree", selectmode="extended", xscrollcommand=hscrollbar.set,
                                       yscrollcommand=vscrollbar.set)
        self.treeview.grid(column=0, row=0, sticky="news", padx=5, pady=5)
        vscrollbar.configure(command=self.treeview.yview)
        hscrollbar.configure(command=self.treeview.xview)

        self.controller = controller
        self.bind_listeners()
        self.is_user_click = False

        self.network_id = None
        self.node_section = None
        self.node_entries = {}
        self.edge_section = None
        self.edge_entries = {}
        self.flow_section = None
        self.flow_entries = {}

        self.create_tree_view()

    def bind_listeners(self):
        """
        Bind all required listeners to the treeview.
        """
        self.treeview.tag_bind("heading", OS.left_mouse_button, self.set_click)
        self.treeview.tag_bind("all", OS.left_mouse_button, self.set_click)
        self.treeview.bind("<<TreeviewSelect>>", self.select_items)
        self.treeview.bind("<Up>", self.set_click)
        self.treeview.bind("<Down>", self.set_click)
        self.treeview.tag_bind("all", "<Double-Button-1>", self.on_double_click)
        self.treeview.tag_bind("all", "<Return>", self.on_double_click)
        self.treeview.tag_bind("all", "<space>", self.on_double_click)

    def on_double_click(self, event):
        """
        Opens entry popup above the item's column to edit the entry
        """
        if event.type == tk.EventType.KeyPress:
            clicked_entry_id = self.treeview.selection()[0]
        else:
            clicked_entry_id = self.treeview.identify("item", event.x, event.y)
        component_uid = UUID(self.treeview.item(clicked_entry_id, "tag")[0])
        clicked_component = None
        if component_uid in self.node_entries:
            clicked_component = self.node_entries[component_uid].observed_subject
        elif component_uid in self.edge_entries:
            clicked_component = self.edge_entries[component_uid].observed_subject
        elif component_uid in self.flow_entries:
            clicked_component = self.flow_entries[component_uid].observed_subject

        column = "#0"
        x, y, width, height = self.treeview.bbox(clicked_entry_id, column)
        y_offset = height // 2

        text = self.treeview.item(clicked_entry_id, 'text')
        entry = EntryPopup(self.treeview, text, lambda name: self.rename_callback(clicked_component, name))
        entry.place(x=0, y=y + y_offset, anchor="w", relwidth=True)

    def rename_callback(self, component, name):
        """
        Renames components in the model.

        :param component: component object (node, edge, or flow)
        :param name: new name
        """
        if isinstance(component, Node):
            self.controller.model_facade.update_node_name(component, name)
        elif isinstance(component, Edge):
            self.controller.model_facade.update_edge_name(component, name)
        elif isinstance(component, Flow):
            self.controller.model_facade.update_flow_name(component, name)

    def set_click(self, _) -> None:
        """
        Sets self.clicked when an entry was clicked.

        :param _: click event
        """
        self.is_user_click = True

    def select_items(self, _) -> None:
        """
        Is called when selecting/deselecting entries in the treeview. Sets the activity of those nodes in the model.

        :param _: treeview selection event
        """
        if not self.is_user_click:
            return
        self.controller.model_facade.unselect_all_components()
        selected_items = self.treeview.selection()
        for item in selected_items:
            try:
                uid = UUID(self.treeview.item(item, "tag")[0])
            except (IndexError, ValueError):
                continue
            if uid in self.node_entries:
                entry = self.node_entries[uid]
            elif uid in self.edge_entries:
                entry = self.edge_entries[uid]
            elif uid in self.flow_entries:
                entry = self.flow_entries[uid]
            else:
                continue
            entry.set_shift_active()
        self.is_user_click = False

    def create_tree_view(self):
        """
        Inserts all initial entries of the treeview.
        """
        self.network_id = self.treeview.insert('', tk.END, text=self.observed_subject.name, open=True,
                                               tags="heading")
        self.node_section = self.treeview.insert(self.network_id, text="Nodes", index=1, open=True, tags="heading")
        self.edge_section = self.treeview.insert(self.network_id, text="Edges", index=2, open=True, tags="heading")
        self.flow_section = self.treeview.insert(self.network_id, text="Flows", index=3, open=True, tags="heading")

        for node_id, node in self.observed_subject.nodes.items():
            self.node_entries[node_id] = ComponentEntry(self, self.controller, self.node_section, node)

        for edge_id, edge in self.observed_subject.edges.items():
            self.edge_entries[edge_id] = ComponentEntry(self, self.controller, self.edge_section, edge)

        for flow_id, flow in self.observed_subject.flows.items():
            self.flow_entries[flow_id] = ComponentEntry(self, self.controller, self.flow_section, flow)

    def update_(self, updated_component):
        if isinstance(updated_component[0], Node):
            node = updated_component[0]
            if updated_component[1] == "add_node":
                self.node_entries[node.id] = ComponentEntry(self, self.controller, self.node_section, node)
            if updated_component[1] == "delete_node":
                self.node_entries[node.id].delete()
                del self.node_entries[node.id]
        elif isinstance(updated_component[0], Edge):
            edge = updated_component[0]
            if updated_component[1] == "add_edge":
                self.edge_entries[edge.id] = ComponentEntry(self, self.controller, self.edge_section, edge)
            if updated_component[1] == "delete_edge":
                self.edge_entries[edge.id].delete()
                del self.edge_entries[edge.id]
        elif isinstance(updated_component[0], Flow):
            flow = updated_component[0]
            if updated_component[1] == "add_flow":
                self.flow_entries[flow.id] = ComponentEntry(self, self.controller, self.flow_section, flow)
            if updated_component[1] == "delete_flow":
                self.flow_entries[flow.id].delete()
                del self.flow_entries[flow.id]
        elif isinstance(updated_component[0], Network):
            if updated_component[1] == "name":
                self.treeview.item(self.network_id, text=self.observed_subject.name)

    def destroy(self):
        for node in self.node_entries:
            self.node_entries[node].delete()
        self.node_entries = {}
        for edge in self.edge_entries:
            self.edge_entries[edge].delete()
        self.edge_entries = {}
        for flow in self.flow_entries:
            self.flow_entries[flow].delete()
        self.flow_entries = {}

        self.observed_subject.unsubscribe(self)
        self.observed_subject = None

        super().destroy()
