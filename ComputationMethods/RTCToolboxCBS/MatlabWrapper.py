import pathlib
from typing import Any

import matlab.engine

from ComputationMethods.RTCToolboxCBS.CBSInterface import CBSInterface


class MatlabWrapper(CBSInterface):

    def __init__(self, matlab_files: pathlib.Path = pathlib.Path("ComputationMethods/RTCToolboxCBS")):
        """
        Prepares a MATLAB engine in the background.

        :param matlab_files: the path to the .m files
        """
        m_flag_show_plots = "-noFigureWindows"
        m_flag_show_conv_warnings = " -r 'warning(\"off\",\"CUSTOM:Convolution\")'"
        matlab_flags = m_flag_show_plots + m_flag_show_conv_warnings
        self._future_engine = matlab.engine.start_matlab(option=matlab_flags, background=True)
        self._matlab_files = matlab_files
        self._engine = None

    def _get_engine(self):
        """
        Returns the MATLAB engine. Waits until the engine is fully instantiated.

        :return: MATLAB engine
        """
        if self._engine is None:
            self._engine = self._future_engine.result()
            self._future_engine = None
            self._engine.addpath(str(self._matlab_files.absolute()), nargout=0)
        return self._engine

    def exit(self):
        """
        Shuts down the engine.
        """
        self._get_engine().exit()

    def __getattr__(self, item):
        """
        Passes calls not included in this wrapper to the engine.

        :param item: call
        :return: reference to the attribute
        """
        return getattr(self._get_engine(), item)

    def __getattribute__(self, name: str) -> Any:
        """
        Passes calls defined in the interface to the MATLAB engine.

        :param name: call
        :return: reference to the attribute
        """
        if name in CBSInterface.__dict__:
            return getattr(self._get_engine(), name)
        else:
            return super().__getattribute__(name)
