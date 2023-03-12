from View.GUI.Windows.ParameterWindow.ComponentSections.AbstractParameterSection import AbstractParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.TkParameterSection import TkParameterSection


class EdgeParameterSection(AbstractParameterSection):
    def __init__(self, root, edge, controller):
        super().__init__(root, controller, edge, TkParameterSection.ParameterType.Edge)
        edge.start.subscribe(self)
        edge.end.subscribe(self)

    def update_value_dictionary(self):
        super().update_value_dictionary()
        self.value_dictionary["name"] = self.observed_subject.name
        self.value_dictionary["start node"] = self.observed_subject.start.name
        self.value_dictionary["end node"] = self.observed_subject.end.name

    def destroy(self):
        self.observed_subject.start.unsubscribe(self)
        self.observed_subject.end.unsubscribe(self)
        super().destroy()
