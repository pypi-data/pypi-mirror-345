#  Copyright (c) 2017-2023 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import numpy

from .axis import Axis

"""
Curve Class
"""


class Curve(object):
    """
    Curve allow the defintion and extroplation of data of a curve

    This class is usually returned by the DCM class after importing a file.
    """

    def __init__(self, x, y, name="curve"):
        if isinstance(x, Axis):
            self._x = x
        else:
            self._x = Axis(x, name+'_x')

        self._y = y  # array of values
        self.name = name

    def update(self, x, y, y_min, y_max, weight=1):
        """
        update the curve using the x,y supplied
        """

        # TODO set weight based on std dev
        delta = (y - self.y(x)) / weight
        _x = self._x
        if isinstance(_x, Axis):
            _x = self._x.values

        # TODO update only the value when on an x point
        # TODO update up and down points only when between points

        for i in range(len(_x)):
            _xi = _x[i]
            alpha = numpy.arctan((_xi - x) / delta)
            self._y[i] += numpy.cos(alpha) * delta
            self._y[i] = max(self._y[i], y_min)
            self._y[i] = min(self._y[i], y_max)

    def y(self, x):
        x_table = self._x.values
        z_table = self._y
        if x <= x_table[0]:
            return z_table[0]
        if x >= x_table[len(x_table) - 1]:
            return z_table[len(z_table) - 1]

        # Linear search
        i = 1
        while x > x_table[i]:
            i += 1

        Aux_ = z_table[i - 1]
        Aux__a = z_table[i]

        # Interpolation
        Aux__b = x - x_table[i - 1]
        Aux__c = x_table[i] - x_table[i - 1]

        if Aux_ <= Aux__a:
            # Positive slope
            Aux_ += ((Aux__a - Aux_) * Aux__b) / Aux__c
        else:
            # Negative slope
            Aux_ -= ((Aux_ - Aux__a) * Aux__b) / Aux__c

        return Aux_

    """
    param x_table: table
    param N : length of array
    param x: value to search for

    return irx, fraction
    irx index of x
    fraction of position between irx and irx+1
    """

    def fraction(x_table, N, x):
        # Saturation
        if x <= x_table[0]:
            irx = 0
            fraction = 0
        elif x >= x_table[N - 1]:
            irx = N - 1
            fraction = 0
        else:
            Aux_ = 0

            # Linear search, start low
            x_table_index = 0
            while x >= x_table[x_table_index]:
                Aux_ += 1
                x_table_index += 1

            # Backtrack one step
            x_table_index -= 1

            irx = Aux_
            fraction = int(
                ((x - x_table[x_table_index]) << 8)
                / (x_table[x_table_index + 1] - x_table[x_table_index])
            )
        return irx, fraction
