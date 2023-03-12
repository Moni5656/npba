from View.GUI.Windows.ParameterWindow.ComponentSections.AbstractParameterSection import AbstractParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.TkParameterSection import TkParameterSection


class FlowParameterSection(AbstractParameterSection):
    def __init__(self, root, flow, controller):
        super().__init__(root, controller, flow, TkParameterSection.ParameterType.Flow)

    def update_value_dictionary(self):
        super().update_value_dictionary()
        self.value_dictionary["name"] = self.observed_subject.name
        path = [n.name for n in self.observed_subject.path]
        self.value_dictionary["path"] = ", ".join(path)
        self.value_dictionary["color"] = self.observed_subject.color
        self.value_dictionary["highlight color"] = self.observed_subject.highlight_color
