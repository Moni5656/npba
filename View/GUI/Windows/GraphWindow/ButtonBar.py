from idlelib.tooltip import Hovertip

import PIL.Image
import customtkinter as ctk
from customtkinter import ThemeManager

from View.GUI.Windows.GraphWindow.EdgeView import EdgeView
from View.GUI.Windows.GraphWindow.FlowView.FlowView import FlowView


class ButtonBar(ctk.CTkFrame):
    IMG_PATH = "View/GUI/Windows/GraphWindow/ButtonBarImages/"

    def __init__(self, parent, canvas, **kwargs):
        fg_color = ThemeManager.theme["color_scale"]["inner"]
        super().__init__(parent, fg_color=fg_color, **kwargs)

        size = 50
        size = (size, size)
        self.add_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'add_button.png'), size=size)
        self.add_button_pressed_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'add_button_pressed.png'),
                                                   size=size)
        self.flow_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'curved_arrow_button.png'), size=size)
        self.flow_button_pressed_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'curved_arrow_button_pressed.png'),
                                                    size=size)
        self.edge_button_pressed_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'arrow_button_pressed.png'),
                                                    size=size)
        self.edge_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'arrow_button.png'), size=size)
        self.delete_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'delete_button.png'), size=size)
        self.delete_button_pressed_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'delete_button_pressed.png'),
                                                      size=size)
        self.zoom_in_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'zoom_in_button.png'), size=size)
        self.zoom_out_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'zoom_out_button.png'), size=size)
        self.export_button_img = ctk.CTkImage(PIL.Image.open(self.IMG_PATH + 'export_button.png'), size=size)
        self.run_button_img = ctk.CTkImage(PIL.Image.open("View/GUI/images/" + 'run_button.png'), size=size)

        self.buttons = []
        self.graph_canvas = canvas
        self.add_buttons()
        self.node_button_pressed = False
        self.edge_button_pressed = False
        self.flow_button_pressed = False
        self.delete_button_pressed = False

    def add_buttons(self):
        """
        Adds buttons to the button bar.
        """
        buttons = {"Add Node": [self.toggle_add_button, self.add_button_img],
                   "Add Edge": [self.toggle_edge_button, self.edge_button_img],
                   "Add Flow": [self.toggle_flow_button, self.flow_button_img],
                   "Delete": [self.toggle_delete_button, self.delete_button_img],
                   "Zoom In": [self.graph_canvas.zoom_in, self.zoom_in_button_img],
                   "Zoom Out": [self.graph_canvas.zoom_out, self.zoom_out_button_img],
                   "Export Graph as ...": [self.graph_canvas.export, self.export_button_img],
                   "Run": [self.run, self.run_button_img],
                   }
        color = ThemeManager.theme["color_scale"]["inner"]
        for button_text, (command, img) in buttons.items():
            bt = ctk.CTkButton(self, text=" ", width=10, image=img, fg_color=color,
                               command=command)
            self.buttons.append(bt)
            bt.pack(side="left")
            Hovertip(bt, text=button_text, hover_delay=500)

    def toggle_add_button(self):
        """
        Toggles the add node button and other pressed buttons.
        """
        if self.delete_button_pressed:
            self.toggle_delete_button()
        if self.flow_button_pressed:
            self.toggle_flow_button()
        if self.edge_button_pressed:
            self.toggle_edge_button()
        self.node_button_pressed = not self.node_button_pressed

        if self.node_button_pressed:
            self.buttons[0].configure(image=self.add_button_pressed_img)
        else:
            self.buttons[0].configure(image=self.add_button_img)

    def toggle_edge_button(self):
        """
        Toggles the add edge button and other pressed buttons.
        """
        if self.delete_button_pressed:
            self.toggle_delete_button()
        if self.flow_button_pressed:
            self.toggle_flow_button()
        if self.node_button_pressed:
            self.toggle_add_button()
        self.edge_button_pressed = not self.edge_button_pressed

        self.graph_canvas.unbind("<Motion>")
        self.graph_canvas.delete("preview")
        EdgeView.start_node = None

        if self.edge_button_pressed:
            self.buttons[1].configure(image=self.edge_button_pressed_img)
        else:
            self.buttons[1].configure(image=self.edge_button_img)

    def toggle_flow_button(self):
        """
        Toggles the add flow button and other pressed buttons.
        """
        if self.edge_button_pressed:
            self.toggle_edge_button()
        if self.delete_button_pressed:
            self.toggle_delete_button()
        if self.node_button_pressed:
            self.toggle_add_button()
        self.flow_button_pressed = not self.flow_button_pressed

        self.graph_canvas.unbind("<Motion>")
        self.graph_canvas.delete("preview")
        FlowView.start_node = None
        FlowView.current_flow = None

        if self.flow_button_pressed:
            self.buttons[2].configure(image=self.flow_button_pressed_img)
        else:
            self.buttons[2].configure(image=self.flow_button_img)

    def toggle_delete_button(self):
        """
        Toggles the delete button and other pressed buttons.
        """
        if self.node_button_pressed:
            self.toggle_add_button()
        if self.flow_button_pressed:
            self.toggle_flow_button()
        if self.edge_button_pressed:
            self.toggle_edge_button()
        self.delete_button_pressed = not self.delete_button_pressed

        if self.delete_button_pressed:
            self.buttons[3].configure(image=self.delete_button_pressed_img)
        else:
            self.buttons[3].configure(image=self.delete_button_img)

    def run(self):
        """
        Runs the computation.
        """
        self.graph_canvas.controller.run_computation()
