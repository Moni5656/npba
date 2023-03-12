from abc import ABC, abstractmethod

from View.GUI.Windows.ParameterWindow.ComponentSections.TkParameterSection import TkParameterSection
from View.Observer import Observer


class AbstractParameterSection(Observer, ABC):
    def __init__(self, root, controller, observed_subject, parameter_type):
        super().__init__(observed_subject)
        self.type = parameter_type
        self.root = root
        self.controller = controller
        self.tk_section = None
        self.is_displayed = False
        self.value_dictionary = {}

        if observed_subject.is_selected:
            self.show_tk_section()

    def update_(self, updated_component):
        update = updated_component[0]
        update_text = updated_component[1]
        if update_text == "set_selection" and self.observed_subject.is_selected:
            self.show_tk_section()
        elif update_text == "set_selection" and not self.observed_subject.is_selected:
            self.hide_tk_section()
        elif self.tk_section is None:
            return
        elif update_text == "add_configuration" and update.associated_component == self.observed_subject:
            self.tk_section.add_configuration(update)
        elif update_text == "delete_configuration":
            self.tk_section.remove_configuration(update)
        elif self.is_displayed:
            self.update_tk_section()
        else:
            return

    def make_tk_section(self):
        """
        Creates a parameter section.
        """
        self.update_value_dictionary()
        self.tk_section = TkParameterSection(self.root, self.controller, self.observed_subject,
                                             self.type, self.value_dictionary)

    def update_tk_section(self, force: bool = False):
        """
        Updates the parameter values of the parameter section.

        :param force: forces updates even if section is not visible
        """
        if self.tk_section is not None and (self.is_displayed or force):
            self.update_value_dictionary()
            self.tk_section.update_values(self.value_dictionary)

    def show_tk_section(self):
        """
        Displays the parameter section.
        """
        if self.tk_section is None:
            self.make_tk_section()
        else:
            self.update_tk_section(force=True)
        self._pack_section()

    def hide_tk_section(self):
        """
        Hides the parameter section.
        """
        if self.tk_section is None:
            return
        if self.is_displayed:
            self.tk_section.pack_forget()
            self.is_displayed = False

    @abstractmethod
    def update_value_dictionary(self):
        """
        Updates the value dictionary used to display the parameter names and values.
        """
        self.value_dictionary["ID"] = str(self.observed_subject.id)

    def _pack_section(self):
        """
        Packs the parameter section into another widget.
        """
        if not self.is_displayed:
            self.tk_section.pack(fill="both", anchor='center')
            self.is_displayed = True

    def destroy(self):
        """
        Deletes the section from the parameter configuration window.
        """
        if self.tk_section is not None:
            self.tk_section.destroy()
            self.tk_section = None
            self.is_displayed = False
        self.observed_subject.unsubscribe(self)
        self.observed_subject = None
