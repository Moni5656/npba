import uuid
from abc import abstractmethod
from typing import Type

from Model.ComputationConfigurations.ConfigurationTemplate.AbstractConfiguration import AbstractConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultEdgeConfiguration import \
    DefaultEdgeConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultFlowConfiguration import \
    DefaultFlowConfiguration
from Model.ComputationConfigurations.ConfigurationTemplate.DefaultNodeConfiguration import \
    DefaultNodeConfiguration
from Model.ModelFacade import ModelFacade
from Model.Result import Result


class AbstractNetworkConfiguration(AbstractConfiguration):

    def __init__(self, group_id=None, is_active=True, flow_ids_of_interest=None, name="", **kwargs):
        if group_id is None:
            group_id = uuid.uuid4()
        super().__init__(group_id=group_id, **kwargs)
        if flow_ids_of_interest is None:
            flow_ids_of_interest = []

        self.is_active = is_active
        self.flow_ids_of_interest = flow_ids_of_interest
        self.name = name

        self._compute_args = {}

    @staticmethod
    @abstractmethod
    def get_configuration_name() -> str:
        """
        Returns the name of a configuration.

        :return: configuration name
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_configuration_information() -> str:
        """
        Returns the configuration information.

        :return: configuration information
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_configuration_identifier() -> str:
        """
        Returns a unique string, used to identify the correct configuration when deserializing.
        Changing this string invalidates previously exported save files.

        :return: configuration ID
        """
        raise NotImplementedError()

    @abstractmethod
    def compute(self, network, result: Result) -> None:
        """
        Computes the current configuration. Runs in a separate process.

        :param network: network object
        :param result: a result object for storing results and plots
        """
        raise NotImplementedError()

    @staticmethod
    def get_node_configuration_class() -> Type[DefaultNodeConfiguration]:
        """
        Returns a reference to the node configuration class.

        :return: node configuration class reference
        """
        return DefaultNodeConfiguration

    @staticmethod
    def get_edge_configuration_class() -> Type[DefaultEdgeConfiguration]:
        """
        Returns a reference to the edge configuration class.

        :return: edge configuration class reference
        """
        return DefaultEdgeConfiguration

    @staticmethod
    def get_flow_configuration_class() -> Type[DefaultFlowConfiguration]:
        """
        Returns a reference to the flow configuration class.

        :return: flow configuration class reference
        """
        return DefaultFlowConfiguration

    def make_parameter_dict(self):
        names = []
        for flow_id in self.flow_ids_of_interest:
            names.append(self.model.network.flows[flow_id].name)
        own_dict = {"name": self.name, "pause configuration": not self.is_active, "flows of interest": ", ".join(names)}
        return super().make_parameter_dict() | own_dict

    def update_parameter_dict(self, dictionary):
        new_value = dictionary["name"]
        if new_value != self.name:
            self.model.update_configuration_name(self.group_id, new_value)

        true_values = ['true', '1', 't', 'y', 'yes']
        false_values = ['false', '0', 'f', 'n', 'no']
        new_value = str(dictionary["pause configuration"]).lower()
        if new_value in true_values:
            new_value = True
        elif new_value in false_values:
            new_value = False
        else:
            raise ValueError(f"Wrong input, allowed are: {true_values} or {false_values}")
        self.is_active = not new_value

        return super().update_parameter_dict(dictionary)

    def to_serializable_dict(self) -> dict:
        super_dict = super().to_serializable_dict()
        own_dict = {"name": self.name, "_configuration_class": self.get_configuration_identifier(),
                    "is_active": self.is_active, "flow_ids_of_interest": []}
        for flow_id in self.flow_ids_of_interest:
            own_dict["flow_ids_of_interest"].append(str(flow_id))
        return super_dict | own_dict

    @staticmethod
    def to_constructor_dict(json_dict, model: ModelFacade, network) -> dict:
        super_dict = AbstractConfiguration.to_constructor_dict(json_dict, model, network)
        flows = []
        for flow_id in json_dict["flow_ids_of_interest"]:
            flows.append(uuid.UUID(flow_id))
        name = json_dict["name"]
        return super_dict | {"name": name, "flow_ids_of_interest": flows, "is_active": json_dict["is_active"]}

    def __getstate__(self):
        attributes = super().__getstate__()
        if "_compute_args" in attributes:
            attributes["_compute_args"] = {}
        return attributes
