import inspect
from typing import Type, Callable

import networkx

from Model.Computation import Computation
from Model.Result import Result
from Model.Subject import Subject

_available_network_configurations = {}
_graph_generator_functions = inspect.getmembers(networkx.generators, inspect.isfunction)


def get_networkx_generator_functions() -> list[tuple[str, Callable[..., networkx.Graph]]]:
    """
    Returns a list of available networkX generator functions.

    :return: a list of generator functions
    """
    return _graph_generator_functions


def register_network_configuration(network_configuration: Type['AbstractNetworkConfiguration'],
                                   first_option: str = "Default Name",
                                   second_option: str = "Default Name",
                                   third_option: str = "Default Name"):
    """
    Adds a network configuration to the application.

    :param network_configuration: name of the network configuration
    :param first_option: option for the first drop-down menu
    :param second_option: option for the second drop-down menu
    :param third_option: option for the third drop-down menu
    """
    _available_network_configurations[first_option, second_option, third_option] = network_configuration


def get_available_network_configurations() -> dict[tuple[str, str, str], Type['AbstractNetworkConfiguration']]:
    """
    Returns a dictionary of available network configurations.

    :return: dictionary of network configurations
    """
    return _available_network_configurations


def get_network_configuration_from_options(first_option, second_option, third_option):
    """
    Returns a network configuration based on the options chosen in the drop-down menus.

    :param first_option: option of the first drop-down menu
    :param second_option: option of the second drop-down menu
    :param third_option: option of the third drop-down menu
    :return: network configuration object
    """
    network_configuration = get_available_network_configurations()[first_option, second_option, third_option]
    return network_configuration


import Model.ComputationConfigurations
import Model.Network
from .ModelFacade import ModelFacade
