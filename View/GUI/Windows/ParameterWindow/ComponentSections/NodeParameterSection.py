from View.GUI.Windows.ParameterWindow.ComponentSections.AbstractParameterSection import AbstractParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.TkParameterSection import TkParameterSection


class NodeParameterSection(AbstractParameterSection):
    def __init__(self, root, node, controller):
        super().__init__(root, controller, node, TkParameterSection.ParameterType.Node)

    def update_value_dictionary(self):
        super().update_value_dictionary()
        self.value_dictionary["name"] = self.observed_subject.name
        self.value_dictionary["x"] = self.observed_subject.x
        self.value_dictionary["y"] = self.observed_subject.y
        self.value_dictionary["outgoing edges"] = ", ".join(
            sorted([edge.name for edge in self.observed_subject.edges.values()]))
