# import numpy
import pwlf

from .curve import Curve


# TODO engine configuration from JSON file
class Engine(object):
    """
    Class engine offers support for engine calculation and estimation.
    """

    def __init__(self, n=[600, 1000, 2000, 4000, 6000], t=[100, 500, 1000, 800, 100]):
        super().__init__()
        self._n = n
        self._t = t
        self.t = Curve(n, t)

    def t_max(self):
        return max(self._t)

    def n_max(self):
        return max(self._n)

    def torque(self, speed, limit=100):
        """
        Return the torque at an engine speed with a max percentage torque
         ( 100% is full torque)
        :param speed: engine speed in rpm
        :param limit: maximum percent torque from curve
        :return: engine torque in Nm
        """
        return self.t.y(speed) * limit / 100

    def fit(self, seg):
        f = pwlf.PiecewiseLinFit(self._n, self._t, seed=123)
        x = f.fit(seg)
        y = f.predict(x)
        return x, y
