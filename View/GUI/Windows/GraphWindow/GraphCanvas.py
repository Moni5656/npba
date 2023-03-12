import os
import subprocess
import sys
import tkinter as tk
import tkinter.font as tkfont
from multiprocessing import Process
from tkinter.filedialog import *

import numpy as np

from Model.Network.Edge import Edge
from View.GUI.CustomWidgets.CustomCanvas import CustomCanvas
from View.GUI.CustomWidgets.CustomScrollbar import CustomScrollbar
from View.GUI.Windows.GraphWindow.NodeView import NodeView
from View.Observer import Observer
from utils import utils
from utils.utils import OS


class GraphCanvas(CustomCanvas, Observer):
    ZOOM_FACTOR_IN = 1.5
    ZOOM_FACTOR_OUT = 1 / ZOOM_FACTOR_IN
    TEXT_INCREASE = 3

    def __init__(self, parent, controller, network, move_to_center=True, **kwargs):
        super().__init__(parent, **kwargs)

        def v_geometry_command(s):
            s.pack(side="right", fill="y", padx=(0, 3), pady=3)

        def h_geometry_command(s):
            s.pack(side="bottom", fill="x", padx=3, pady=(0, 3))

        vscrollbar = CustomScrollbar(self, geometry_command=v_geometry_command)
        hscrollbar = CustomScrollbar(self, geometry_command=h_geometry_command, orientation="horizontal")
        vscrollbar.configure(command=self.yview)
        hscrollbar.configure(command=self.xview)
        self.configure(xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
        Observer.__init__(self, network)
        self.scale_factor = 1
        self.origin = None
        self.node_views = {}
        self.edge_views = {}
        self.flow_views = {}
        self.build_origin()
        self.button_bar = None
        self.controller = controller

        if move_to_center:
            self.after(400, self.move_to_center)

        self.bind(OS.left_mouse_button, self.on_left_click)
        self.bind(OS.right_mouse_button, self.move_canvas_start)
        self.bind(OS.right_mouse_button_motion, self.move_canvas)
        self.bind("<Configure>", lambda e: self.reset_scroll_region())

        self.bind('<Enter>', self._bind_to_mousewheel)
        self.bind('<Leave>', self._unbind_to_mousewheel)

    def _bind_to_mousewheel(self, _):
        """
        Binds methods to the mousewheel.

        :param _:
        """
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.bind_all("<Control-MouseWheel>", self._on_control_mousewheel)

    def _unbind_to_mousewheel(self, _):
        """
        Unbinds methods from the mousewheel.

        :param _:
        """
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")
        self.unbind_all("<Control-MouseWheel>")

    def _on_mousewheel(self, event):
        """
        Handles a scroll event.

        :param event: scroll event
        """
        delta = (event.delta // 120) if OS.Windows else event.delta
        self.yview_scroll(-1 * delta, "units")

    def _on_shift_mousewheel(self, event):
        """
        Handles a Shift+Scroll event.

        :param event: Shift+Scroll event
        """
        delta = (event.delta // 120) if OS.Windows else event.delta
        self.xview_scroll(-1 * delta, "units")

    def _on_control_mousewheel(self, event):
        """
        Handles a Control+Scroll event.

        :param event: Control+Scroll event
        """
        delta = (event.delta // 120) if OS.Windows else event.delta
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def initial_setup(self):
        """
        Adds existing components to the canvas.
        """
        self.add_initial_nodes()
        self.add_initial_edges()
        self.add_initial_flows()

    def add_initial_nodes(self):
        """
        Adds existing nodes to the canvas.
        """
        for node_id in self.observed_subject.nodes:
            node = self.observed_subject.nodes[node_id]
            self.add_node(node)

    def add_initial_edges(self):
        """
        Adds existing edges to the canvas.
        """
        for edge_id in self.observed_subject.edges:
            edge = self.observed_subject.edges[edge_id]
            self.add_edge(edge)

    def add_initial_flows(self):
        """
        Adds existing flows to the canvas.
        """
        for flow_id in self.observed_subject.flows:
            flow = self.observed_subject.flows[flow_id]
            self.add_flow(flow)

    def update_(self, updated_component):
        """
        Triggered when the observed network is updated in the model. Handles any resulting changes.

        :param updated_component: information about the updated network
        """
        update = False
        if updated_component[1] == "add_node":
            self.add_node(updated_component[0])
            update = True
        elif updated_component[1] == "delete_node":
            self.delete_node(updated_component[0])
            update = True
        elif updated_component[1] == "add_edge":
            self.add_edge(updated_component[0])
            update = True
        elif updated_component[1] == "delete_edge":
            self.delete_edge(updated_component[0])
            update = True
        elif updated_component[1] == "add_flow":
            self.add_flow(updated_component[0])
            update = True
        elif updated_component[1] == "delete_flow":
            self.delete_flow(updated_component[0])
            update = True

        if update:
            self.update_idletasks()
            self.reset_scroll_region()

    def reset_scroll_region(self):
        """
        Resets the scroll region according to the canvas content.
        """
        bbox = self.bbox("node||edge||flow")
        if bbox is None:
            self.configure(scrollregion=(0, 0, 0, 0))
            return
        width = self.winfo_width() - self.scale_factor * 70
        height = self.winfo_height() - self.scale_factor * 70
        bigger_bbox = bbox[0] - width, bbox[1] - height, bbox[2] + width, bbox[3] + height
        self.configure(scrollregion=bigger_bbox)

    def add_node(self, node):
        """
        Adds a node to the canvas.

        :param node: node object
        """
        node_view = NodeView(node, self.button_bar, self)
        self.node_views[node] = node_view

    def add_edge(self, edge: Edge):
        """
        Adds an edge to the canvas.

        :param edge: edge object
        """
        from View.GUI.Windows.GraphWindow.EdgeView import EdgeView
        edge_view = EdgeView(self, edge)
        self.edge_views[edge] = edge_view

    def add_flow(self, flow):
        """
        Adds a flow to the canvas.

        :param flow: flow object
        """
        from View.GUI.Windows.GraphWindow.FlowView.FlowView import FlowView
        flow_view = FlowView(self, flow)
        FlowView.current_flow = flow
        self.flow_views[flow] = flow_view

    def delete_node(self, node):
        """
        Deletes a node from the canvas.

        :param node: node object
        """
        self.node_views[node].destroy()
        del self.node_views[node]

    def delete_edge(self, edge):
        """
        Deletes an edge from the canvas.

        :param edge: edge object
        """
        self.edge_views[edge].destroy()
        del self.edge_views[edge]

    def delete_flow(self, flow):
        """
        Deletes a flow from the canvas.

        :param flow: flow object
        """
        self.flow_views[flow].destroy()
        del self.flow_views[flow]

    def on_left_click(self, event):
        """
        Handles left click events.

        :param event: left click event
        """
        if self.button_bar is None:
            return
        if self.button_bar.node_button_pressed:
            canvas_x, canvas_y = self.coords_event_to_canvas(event)
            model_x, model_y = self.coords_canvas_to_model(canvas_x, canvas_y)
            self.controller.model_facade.unselect_all_components()
            self.controller.add_node(model_x, model_y)

    def coords_event_to_canvas(self, event):
        """
        Translates event coordinates to the actual canvas coordinates.

        :param event: arbitrary event
        :return: canvas coordinates
        """
        return self.canvasx(event.x), self.canvasy(event.y)

    def coords_canvas_to_model(self, x: int, y: int) -> (int, int):
        """
        Translates canvas coordinates to model coordinates.

        :param x: x coordinate
        :param y: y coordinate
        :return: model coordinates
        """
        m_x = (x - self.origin_offset_x()) / self.scale_factor
        m_y = (y - self.origin_offset_y()) / self.scale_factor
        return round(m_x), round(m_y)

    def coords_model_to_canvas(self, x: int, y: int) -> (int, int):
        """
        Translates model coordinates to canvas coordinates.

        :param x: x coordinate
        :param y: y coordinate
        :return: canvas coordinates
        """
        c_x = self.origin_offset_x() + x * self.scale_factor
        c_y = self.origin_offset_y() + y * self.scale_factor
        return round(c_x), round(c_y)

    def build_origin(self) -> None:
        """
        Marks the origin of the canvas.
        """
        self.origin = self.create_line(0, 0, 0, 0, fill="")

    def origin_offset_x(self) -> int:
        """
        Computes the offset from the original origin to the current canvas origin.

        :return: x offset
        """
        return round(self.coords(self.origin)[0])

    def origin_offset_y(self) -> int:
        """
        Computes the offset from the original origin to the current canvas origin.

        :return: y offset
        """
        return round(self.coords(self.origin)[1])

    def move_canvas_start(self, event):
        """
        Marks the start of the drag movement (position of the click).

        :param event: click event
        """
        self.scan_mark(event.x, event.y)

    def move_canvas(self, event):
        """
        Drags the canvas according to the motion direction.

        :param event: motion event
        """
        self.scan_dragto(event.x, event.y, gain=1)

    def move_canvas_to(self, target_x, target_y, screen_mid_x=None, screen_mid_y=None, is_model_coords=True):
        """
        Moves canvas so that the target coordinates are in the center of the screen.

        :param target_x: target x coordinate
        :param target_y: target y coordinate
        :param screen_mid_x: x coordinate of the center of the screen
        :param screen_mid_y: y coordinates of the center of the screen
        :param is_model_coords: whether coordinates are model or canvas coordinates
        """
        if screen_mid_x is None:
            screen_mid_x = int(self.canvasx(self.winfo_width() / 2))
        if screen_mid_y is None:
            screen_mid_y = int(self.canvasy(self.winfo_height() / 2))
        if is_model_coords:
            target_x, target_y = self.coords_model_to_canvas(target_x, target_y)
        self.scan_mark(target_x, target_y)
        self.scan_dragto(screen_mid_x, screen_mid_y, gain=1)

    def move_to_center(self):
        """
        Moves the canvas to the center of the network bounding box.
        """
        x0, y0, width, height = self.get_export_bbox()
        x_middle, y_middle = x0 + width // 2, y0 + height // 2
        self.move_canvas_to(x_middle, y_middle, is_model_coords=False)

    def winfo_width(self) -> int:
        width = super().winfo_width()
        if width == 1:
            estimated_width = self.winfo_screenwidth() * 0.45
            width = estimated_width
        return width

    def winfo_height(self) -> int:
        height = super().winfo_height()
        if height == 1:
            estimated_height = self.winfo_screenheight() * 0.45
            height = estimated_height
        return height

    def zoom_out(self) -> None:
        """
        Scales down every item in the canvas.
        """
        zoom_x = self.canvasx(self.winfo_width() / 2)
        zoom_y = self.canvasy(self.winfo_height() / 2)
        self.scale_factor *= GraphCanvas.ZOOM_FACTOR_OUT
        self.scale("all", zoom_x, zoom_y, GraphCanvas.ZOOM_FACTOR_OUT, GraphCanvas.ZOOM_FACTOR_OUT)

    def zoom_in(self) -> None:
        """
        Scales up every item in the canvas.
        """
        zoom_x = self.canvasx(self.winfo_width() / 2)
        zoom_y = self.canvasy(self.winfo_height() / 2)
        self.scale_factor *= GraphCanvas.ZOOM_FACTOR_IN
        self.scale("all", zoom_x, zoom_y, GraphCanvas.ZOOM_FACTOR_IN, GraphCanvas.ZOOM_FACTOR_IN)

    def zoom_to(self, target_scale_factor: float) -> None:
        """
        Zooms the canvas to a specific scale factor

        :param target_scale_factor: the targeted scale factor
        """
        zoom_x = self.canvasx(self.winfo_width() / 2)
        zoom_y = self.canvasy(self.winfo_height() / 2)
        scale_factor = target_scale_factor / self.scale_factor
        self.scale_factor *= scale_factor
        self.scale("all", zoom_x, zoom_y, scale_factor, scale_factor)

    def scale(self, *args) -> None:
        """
        Scales items which cannot be scaled with the default scale method.

        :param args: passed to super().scale
        """
        font = tkfont.nametofont("TkTextFont")
        family = font.cget("family")
        size = font.cget("size") + self.TEXT_INCREASE
        super().scale(*args)

        from View.GUI.Windows.GraphWindow.EdgeView import EdgeView
        from View.GUI.Windows.GraphWindow.FlowView.FlowPartView import FlowPartView
        from View.GUI.Windows.GraphWindow.FlowView.GroupedFlowPartView import GroupedFlowPartView

        for child_widget in self.find_withtag("text"):
            self.itemconfigure(child_widget, font=(family, int(size * self.scale_factor)))
        for child_widget in self.find_withtag("edge"):
            self.itemconfigure(child_widget, width=EdgeView.EDGE_THICKNESS * self.scale_factor,
                               arrowshape=(8 * self.scale_factor, 10 * self.scale_factor, 3 * self.scale_factor))
        for child_widget in self.find_withtag("flow"):
            self.itemconfigure(child_widget, width=int(FlowPartView.FLOW_THICKNESS * self.scale_factor),
                               arrowshape=(8 * self.scale_factor, 10 * self.scale_factor, 3 * self.scale_factor))
        for child_widget in self.find_withtag("grouped_flow"):
            self.itemconfigure(child_widget, width=int(GroupedFlowPartView.FLOW_THICKNESS * self.scale_factor),
                               arrowshape=(8 * self.scale_factor, 10 * self.scale_factor, 3 * self.scale_factor))
        self.reset_scroll_region()

    def create_text(self, *args, **kwargs):
        font = tkfont.nametofont("TkTextFont")
        family = font.cget("family")
        size = font.cget("size") + self.TEXT_INCREASE
        kwargs["font"] = (family, int(size * self.scale_factor))
        kwargs["tags"] = "text"
        return super().create_text(*args, **kwargs)

    def draw_advanced_line(self, x1, y1, x2, y2, r=0, shorten_start=0, shorten_end=0, side=tk.LEFT, is_curved=True,
                           **kwargs):
        """
        Provides advanced attributes to, e.g., draw a shortened or curved line.

        :param x1: start x coordinate
        :param y1: start y coordinate
        :param x2: end x coordinate
        :param y2: end y coordinate
        :param r: curvature radius, set to -1 for straight line
        :param shorten_start: units to shorten the start
        :param shorten_end: units to shorten the end
        :param side: curvature side
        :param is_curved: whether line is curved
        :param kwargs: additional attributes to pass to create_line
        :return: line ID
        """
        # compute curvature scale
        distance_to_straight_line = 100
        distance_between_curved_lines = 50
        scale = distance_to_straight_line + (r - 1) * distance_between_curved_lines
        if r == -1:
            scale = 0
        scale *= self.scale_factor

        # compute curvature offset
        point_a = np.array([x1, y1])
        point_b = np.array([x2, y2])
        vector_ab = point_b - point_a
        x, y = vector_ab
        if side == tk.LEFT:
            vector_ab_orthogonal = y, -x
        else:
            vector_ab_orthogonal = -y, x

        vector_ab_orthonormal = vector_ab_orthogonal / np.linalg.norm(vector_ab_orthogonal)
        point_ab_mid = (point_a + point_b) / 2
        point_c = point_ab_mid + scale * vector_ab_orthonormal
        c_x, c_y = point_c

        # shorten start of line
        vector_ac = point_c - point_a
        vector_ac_orthonormal = vector_ac / np.linalg.norm(vector_ac)
        start_x, start_y = point_a + vector_ac_orthonormal * shorten_start

        # shorten end of line
        vector_bc = point_c - point_b
        vector_bc_orthonormal = vector_bc / np.linalg.norm(vector_bc)
        end_x, end_y = point_b + vector_bc_orthonormal * shorten_end

        kwargs["smooth"] = is_curved
        return self.create_line([start_x, start_y, c_x, c_y, end_x, end_y], **kwargs)

    def destroy(self):
        for _, node in self.node_views.items():
            node.destroy()
        self.node_views = {}
        for _, edge in self.edge_views.items():
            edge.destroy()
        self.edge_views = {}
        for _, flow in self.flow_views.items():
            flow.destroy()
        self.flow_views = {}

        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
        self.delete(self.origin)
        super().destroy()
        super().destroy()

    def export(self):
        """
        Exports the canvas by displaying a file chooser.
        """
        filetypes = [("Portable Document Format", "*.pdf"), ("Scalable Vector Graphics", "*.svg"),
                     ("Postscript", "*.ps"), ("Portable Network Graphics", "*.png"),
                     ("Joint Photographic Experts Group", "*.jpeg"), ("Tagged Image File Format", "*.tiff"),
                     ("Bitmap", "*.bmp"), ("Photoshop Document", "*.psd"), ("Encapsulated Postscript", "*.eps")]
        output_file = asksaveasfilename(parent=self, title="Export Graph", initialfile=self.observed_subject.name,
                                        filetypes=filetypes, defaultextension=filetypes[0][1])
        if output_file == "":
            return

        filename, filetype = output_file.rsplit(".", maxsplit=1)
        if filetype == "ps":
            self.make_postscript_from_canvas(output_file)
            return

        tmp_ps_file = filename + "_tmp_.ps"
        self.make_postscript_from_canvas(tmp_ps_file)
        try:
            utils.is_program_installed(GraphCanvas.get_ghostscript_name())
            if filetype == "svg":
                utils.is_program_installed("inkscape")
        except FileNotFoundError as error:
            self.controller.model_facade.notify_error(error)
            return
        Process(
            target=GraphCanvas.convert_to_correct_file,
            args=(tmp_ps_file, output_file, filetype)
        ).start()

    @staticmethod
    def convert_to_correct_file(input_ps_file, output_file, filetype):
        """
        Converts a postscript file to a given file type.

        :param input_ps_file: input postscript path
        :param output_file: output file path
        :param filetype: filetype
        """
        ghostscript_devices = {"pdf": "pdfwrite", "svg": "pdfwrite", "ps": "ps2write", "png": "pngalpha",
                               "jpeg": "jpeg", "tiff": "tiff32nc", "psd": "psdrgb", "eps": "eps2write", "bmp": "bmp16m"}
        if filetype not in ghostscript_devices:
            raise ValueError(f"Filetype: '{filetype}' not available")

        gs_filetype = ghostscript_devices[filetype]
        if filetype == "svg":
            temp_pdf = "_tmp.pdf"
            GraphCanvas.ghostscript_convert(input_ps_file, temp_pdf, gs_filetype)
            subprocess.call(["inkscape", "--export-type=svg", "--export-filename", output_file, temp_pdf])
            GraphCanvas.silent_remove(temp_pdf)
        else:
            GraphCanvas.ghostscript_convert(input_ps_file, output_file, gs_filetype)
        GraphCanvas.silent_remove(input_ps_file)

    @staticmethod
    def ghostscript_convert(input_ps_file, output_file, device_type, resolution=300):
        """
        Converts a postscript file to the requested filetype using Ghostscript.

        :param input_ps_file: input postscript path
        :param output_file: output path
        :param device_type: Ghostscript filetype device
        :param resolution: image resolution
        """
        subprocess.call(
            [f"{GraphCanvas.get_ghostscript_name()}", f"-sDEVICE={device_type}", f"-r{resolution}", "-dEPSCrop",
             "-dBATCH",
             "-dNOPAUSE", "-dQUIET", f"-sOutputFile={output_file}", input_ps_file])

    @staticmethod
    def get_ghostscript_name():
        """
        Returns the name of the Ghostscript executable.

        :return: name of the Ghostscript executable
        """
        if OS.Windows:
            if sys.maxsize > 2 ** 32:
                return "gswin64c"
            else:
                return "gswin32c"
        else:
            return "gs"

    @staticmethod
    def silent_remove(filepath):
        """
        Removes a file without throwing errors.

        :param filepath: path to the file
        """
        try:
            os.remove(filepath)
        except OSError:
            pass

    def get_export_bbox(self):
        """
        Computes the export bounding box to crop the image to the content size.

        :return: bounding box coordinates
        """
        bbox = self.bbox("node||flow||grouped_flow")
        if bbox is None:
            return 0, 0, 0, 0
        f_x0, f_y0, f_x1, f_y1 = bbox
        n_x0, n_y0, n_x1, n_y1 = self.bbox("node")
        flow_leftover = 0.5
        if f_x0 < n_x0:
            n_x0 -= int((n_x0 - f_x0) * flow_leftover)
        if f_y0 < n_y0:
            n_y0 -= int((n_y0 - f_y0) * flow_leftover)
        if f_x1 > n_x1:
            n_x1 += int((f_x1 - n_x1) * flow_leftover)
        if f_y1 > n_y1:
            n_y1 += int((f_y1 - n_y1) * flow_leftover)

        width = n_x1 - n_x0
        height = n_y1 - n_y0
        return n_x0 - 1, n_y0 - 1, width + 2, height + 2

    def make_postscript_from_canvas(self, ps_file):
        """
        Creates a postscript file of the current canvas state.

        :param ps_file: path to the postscript file
        """
        old_factor = self.scale_factor
        self.zoom_to(1)
        x, y, width, height = self.get_export_bbox()
        self.postscript(
            file=ps_file,
            colormode="color",
            x=x, y=y, width=width, height=height,
        )
        self.zoom_to(old_factor)

        with open(ps_file, 'r+') as file:
            content = file.read().replace(f"%%Title: Window {str(self)}", "% title got deleted", 1)
            file.seek(0)
            file.write(content)
            file.truncate()
