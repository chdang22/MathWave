import contextlib
from abc import abstractmethod, ABC

from neurosdk.__cmn_types import *
from neurosdk.cmn_types import *
from neurosdk.sensor import Sensor


class ElectrodeSensor(Sensor, ABC):
    def __init__(self, ptr):
        super().__init__(ptr)
        self.electrodeStateChanged = None
        self.set_electrode_callbacks()
        self.__closed = False

    def __del__(self):
        with contextlib.suppress(Exception):
            if not self.__closed:
                self.__closed = True
                self.electrodeStateChanged = None
                self.unset_electrode_callbacks()
        super().__del__()

    @abstractmethod
    def set_electrode_callbacks(self):
        pass

    @abstractmethod
    def unset_electrode_callbacks(self):
        pass
