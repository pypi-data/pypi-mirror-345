# import numpy

from .curve import Curve

# from scipy.interpolate import interp1d


class Gearbox(object):
    """
    Gearbox class
    Class provide interface to get the gear ratio on a given gear
    """

    def __init__(self, g=[1, 2, 3, 4, 5], r=[10, 9, 8, 7, 6]):
        """
        :param g: list of gears
        :param r: list of ratios
        """
        super().__init__()
        self._g = g
        self._r = r
        self._ratio = Curve(g, r)
        # self._ratio=interp1d(n,r)

    def ratio(self, gear):
        """
        Return the gear ratio for a given gear
        :param gear: gear number
        :return: gear ratio
        """
        return self._ratio.y(gear)
