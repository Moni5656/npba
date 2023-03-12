import Model
from .NancyCBSNetworkConfiguration import NancyCBSNetworkConfiguration as Nancy

Model.register_network_configuration(Nancy, first_option="Network Calculus", second_option="Nancy", third_option="CBS")
