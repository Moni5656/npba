from View.GUI.Windows.ParameterWindow.ComponentSections.AbstractParameterSection import AbstractParameterSection
from View.GUI.Windows.ParameterWindow.ComponentSections.TkParameterSection import TkParameterSection


class NetworkParameterSection(AbstractParameterSection):
    def __init__(self, root, controller, observed_subject):
        super().__init__(root, controller, observed_subject, TkParameterSection.ParameterType.Network)

    def update_value_dictionary(self):
        super().update_value_dictionary()
        self.value_dictionary["name"] = self.observed_subject.name
