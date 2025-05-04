# import numpy

from .engine import Engine
from .map import Map


class EMotor(Engine):
    """
    Class engine offers support for engine calculation and estimation.
    """

    def __init__(self, n, v, t):
        super().__init__(n, t)
        self._n = n
        self._v = v
        self._t = t
        self.t = Map(n, v, t)

    def torque(self, speed, v=750):
        """
        Return the torque at an engine speed with a max percentage torque
         ( 100% is full torque)
        :param speed: engine speed in rpm
        :param limit: maximum percent torque from curve
        :return: engine torque in Nm
        """
        return self.t.z(speed, v)
