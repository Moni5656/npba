import Model
from .ATSConfiguration import ATSConfiguration

Model.register_network_configuration(ATSConfiguration, first_option="Network Calculus", second_option="Python Script",
                                     third_option="CBS-CDT-ATS")
