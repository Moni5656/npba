import Model
from .RTCToolboxCBSNetworkConfiguration import RTCToolboxCBSNetworkConfiguration

Model.register_network_configuration(
    RTCToolboxCBSNetworkConfiguration, first_option="Network Calculus", second_option="RTCToolbox", third_option="CBS")
