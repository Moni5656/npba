import tkinter as tk
from tkinter import Widget

import matplotlib.pyplot as plt
from customtkinter import ThemeManager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from View.GUI.CustomWidgets.CustomFrame import CustomFrame
from View.GUI.CustomWidgets.NotebookCloseableTabs import NotebookCloseableTabs


class ResultNotebook(NotebookCloseableTabs):

    def __init__(self, root_window, result):
        self.results = []
        self.contained_plots = {}
        super().__init__(root_window, color_notebook_bg=ThemeManager.theme["color_scale"]["inner"])
        self.display(result)

    def display(self, result):
        """
        Adds a result object into the notebook.

        :param result: result object
        """
        for name, plot in result.plots:
            self.add_plot(name, plot)

    def add_plot(self, name, fig: plt.Figure, is_toolbar_on_top=True):
        """
        Adds and displays a plot into the notebook.

        :param name: plot name
        :param fig: plot figure
        :param is_toolbar_on_top: whether the toolbar is supposed to be beneath the plot or on top of the plot
        """
        plot = CustomFrame(self)
        plot.columnconfigure(0, weight=1)
        plot.rowconfigure(0, weight=1)
        canvas = FigureCanvasTkAgg(fig, master=plot)
        toolbar = NavigationToolbar2Tk(canvas, plot, pack_toolbar=False)
        toolbar.update()
        if is_toolbar_on_top:
            canvas.get_tk_widget().grid(row=0, column=0, sticky="news")
            toolbar.grid(row=0, column=0, sticky="ws")
        else:
            toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.adjust_figure_look(fig, canvas, toolbar, name)

        self.contained_plots[plot] = (name, fig, toolbar)
        self.add_widget(plot, name)
        self.select(plot)

    def adjust_figure_look(self, figure, canvas, toolbar, display_name):
        """
        Removes non-functional buttons and labels. Adjusts the color of the plot depending on the appearance mode.

        :param figure: plot
        :param canvas: plot canvas object
        :param toolbar: plot toolbar
        :param display_name: name of the plot
        """
        self.recolor_figure(figure, toolbar)
        canvas.get_default_filename = lambda: display_name
        canvas.get_default_filetype = lambda: "svg"
        if "Save" in toolbar._buttons:
            toolbar._buttons["Save"].configure(
                command=lambda *args: self.save_light_color_plot(fig=figure, toolbar=toolbar, *args))
        if "Subplots" in toolbar._buttons:
            # remove subplot button as it is not working
            toolbar._buttons["Subplots"].pack_forget()

        no_break_label = None
        for child in toolbar.children.values():
            config = child.configure()
            if "text" in config and child.cget("text") == '\N{NO-BREAK SPACE}\n\N{NO-BREAK SPACE}':
                no_break_label = child
                break
        if no_break_label is not None:
            no_break_label.pack_forget()

    def recolor_figure(self, fig, toolbar):
        """
        Adjusts the color of the plot depending on the appearance mode.

        :param fig: plot
        :param toolbar: plot toolbar
        """
        bg_color = self.themed_color(ThemeManager.theme["PlotWindow"]["plot_background_color"])
        text_color = self.themed_color(ThemeManager.theme["PlotWindow"]["plot_text_color"])
        toolbar.config(background=bg_color)
        toolbar._message_label.config(background=bg_color, foreground=text_color)
        fig.set_facecolor(bg_color)
        for axe in fig.get_axes():
            axe.set_facecolor(bg_color)
            axe.xaxis.label.set_color(text_color)
            axe.yaxis.label.set_color(text_color)
            axe.spines["bottom"].set_color(text_color)
            axe.spines["top"].set_color(text_color)
            axe.spines["left"].set_color(text_color)
            axe.spines["right"].set_color(text_color)
            axe.tick_params(which="both", colors=text_color)
            legend = axe.get_legend()
            if legend is not None:
                for text in legend.get_texts():
                    text.set_color(text_color)
        fig.canvas.draw()

    def remove(self, widget: Widget) -> None:
        if widget in self.contained_plots:
            del self.contained_plots[widget]
        super().remove(widget)

    def save_light_color_plot(self, fig, toolbar, *args):
        """
        Changes the color mode of the plot window to light, exports the plot, and restores the previous color mode.

        :param fig: plot
        :param toolbar: plot toolbar
        :param args: export arguments
        """
        old_mode = self.appearance_mode
        if old_mode == 1:
            self.appearance_mode = 0
            self.recolor_figure(fig, toolbar)

        toolbar.save_figure(*args)

        if old_mode == 1:
            self.appearance_mode = 1
            self.recolor_figure(fig, toolbar)

    def change_widget_style(self):
        super().change_widget_style()
        for _, figure, toolbar in self.contained_plots.values():
            self.recolor_figure(figure, toolbar)
