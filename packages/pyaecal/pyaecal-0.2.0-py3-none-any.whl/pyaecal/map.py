#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import logging

import numpy
import polars
from scipy.interpolate import LinearNDInterpolator

from .axis import Axis
from .curve import Curve

"""
map Class
"""
# import itertools


class Map(object):
    """
    Map allow the defintion and extroplation of data of a map

    This class is usually returned by the DCM class after importing a file.
    """

    def __init__(self, x, y, z, name="map", log=logging.INFO):
        self.name = name
        if isinstance(x, Axis):
            self._x = x
        else:
            self._x = Axis(x, name + "_x")

        if isinstance(y, Axis):
            self._y = y
        else:
            self._y = Axis(y, name + "_y")
        self._z = z

        self._points()
        self._interp()
        self.log = logging.getLogger(self.__class__.__module__)
        self.log.setLevel(log)

    def z(self, x, y):
        """
        return the y value of a curve given the x value.
        Values are interpolated between the points given
        """
        return self.f(x, y)

    def table(self, x, y):
        """
        Generate a table based on x and y axis
        """
        z = []
        for vy in y:
            ys = []
            for vx in x:
                ys.append(self.z(x, y))
            z.append(ys)

        return z

    def xz(self, y):
        ys = []
        for x in self._x:
            ys.append(self.z(x, y))
        return Curve(self._x, ys)

    # TODO def zx

    def yz(self, x):
        xs = []
        for y in self._y:
            xs.append(self.z(x, y))
        return Curve(xs, self._y)

    # TODO def zy

    def update(self, x, y, z, z_min, z_max, weight=1):
        """
        update z value at x,y position. The table size is not
        changed but the points are refitted to match the change.
        """
        # TODO generate warning / error when points are outise the table boundaries
        delta = (z - self.z(x, y)) / weight

        for iy in range(len(self._y.values)):
            dy = y - self._y.values[iy]
            for ix in range(len(self._x.values)):
                dx = x - self._x.values[ix]
                dist = (dx**2 + dy**2) ** 0.5
                alpha = numpy.arctan(dist / delta)
                self._z[iy][ix] += numpy.cos(alpha) * delta
                self._z[iy][ix] = max(self._z[iy][ix], z_min)
                self._z[iy][ix] = min(self._z[iy][ix], z_max)

        self._points()
        self._interp()

    def _interp(self):
        points = self.points[["x", "y"]].values
        values = self.points["z"]
        self.f = LinearNDInterpolator(points, values)

    def _points(self):
        self.points = polars.DataFrame()
        xs = []
        ys = []
        zs = []
        for ix in range(0, len(self._x.values), 1):
            for iy in range(0, len(self._y.values), 1):
                xs.append(self._x.values[ix])
                ys.append(self._y.values[iy])
                zs.append(self._z[iy][ix])

        self.points["x"] = xs
        self.points["y"] = ys
        self.points["z"] = zs

    def Tab2DS0I2T16641_AGSia(map, x, y):
        x_table = map.x_table
        y_table = map.y_table
        z_table = map.z_table
        Aux_ = map.Ny

        # Saturation for x
        if x < x_table[0]:
            x = x_table[0]
        Aux__a = x_table[-1]
        if x > Aux__a:
            x = Aux__a

        # Linear search for row axis
        i = 0
        while x > x_table[i]:
            i += 1
        z_table += Aux_ * i

        # Saturation for y
        if y < y_table[0]:
            y = y_table[0]
        Aux__b = y_table[-1]
        if y > Aux__b:
            y = Aux__b

        # Linear search for column axis
        j = 0
        while y > y_table[j]:
            j += 1

        # Differences in column axis
        Aux__b = y - y_table[0]
        Aux__c = y_table[1] - y_table[0]

        # Interpolation
        if Aux__b == 0:
            Aux__d = z_table[0]
            Aux__e = z_table[Aux_]
        else:
            Aux__f = z_table[0]

            # 1. Y-Interpolation
            Aux__g = z_table[1]
            if Aux__f < Aux__g:
                # Positive slope
                Aux__d = Aux__f + ((Aux__g - Aux__f) * Aux__b) // Aux__c
            else:
                # Negative slope
                Aux__d = Aux__f - ((Aux__f - Aux__g) * Aux__b) // Aux__c
            z_table += Aux_
            Aux__f = z_table[0]

            # 2. Y-Interpolation
            Aux__g = z_table[1]
            if Aux__f < Aux__g:
                # Positive slope
                Aux__e = Aux__f + ((Aux__g - Aux__f) * Aux__b) // Aux__c
            else:
                # Negative slope
                Aux__e = Aux__f - ((Aux__f - Aux__g) * Aux__b) // Aux__c

        # Differences in row axis
        Aux__a = x - x_table[0]
        Aux__h = x_table[1] - x_table[0]
        if Aux__h != 0:
            if Aux__d < Aux__e:
                # Positive slope
                Aux__d += ((Aux__e - Aux__d) * Aux__a) // Aux__h
            else:
                # Negative slope
                Aux__d -= ((Aux__d - Aux__e) * Aux__a) // Aux__h

        return Aux__d

    def Tab2DS34I2T16665_AGSia(map, x, y, local_xLow, local_yLow):
        x_table = map.x_table
        y_table = map.y_table
        z_table = map.z_table
        Aux_ = map.Ny

        # Saturation for x
        if x < x_table[0]:
            x = x_table[0]
        Aux__a = x_table[-1]
        if x > Aux__a:
            x = Aux__a

        # Local search for row axis
        Aux__b = local_xLow
        x_table += Aux__b

        if x < x_table[0]:
            # Linear search, start high
            while x < x_table[0]:
                Aux__b -= 1
                x_table -= 1
        else:
            # Linear search, start low
            while x > x_table[0]:
                Aux__b += 1
                x_table += 1

        # Saturation for y
        if y < y_table[0]:
            y = y_table[0]
        Aux__c = y_table[-1]
        if y > Aux__c:
            y = Aux__c

        # Local search for column axis
        Aux__b = local_yLow
        y_table += Aux__b

        if y < y_table[0]:
            # Linear search, start high
            while y < y_table[0]:
                Aux__b -= 1
                y_table -= 1
        else:
            # Linear search, start low
            while y > y_table[0]:
                Aux__b += 1
                y_table += 1

        # Differences in column axis
        Aux__b = y - y_table[0]
        Aux__d = y_table[1] - y_table[0]

        # Interpolation
        if Aux__b == 0:
            Aux__e = z_table[0]
            Aux__f = z_table[Aux_]
        else:
            Aux__g = z_table[0]

            # 1. Y-Interpolation
            Aux__h = z_table[1]
            if Aux__g < Aux__h:
                # Positive slope
                Aux__e = Aux__g + ((Aux__h - Aux__g) * Aux__b) // Aux__d
            else:
                # Negative slope
                Aux__e = Aux__g - ((Aux__g - Aux__h) * Aux__b) // Aux__d
            z_table += Aux_
            Aux__g = z_table[0]

            # 2. Y-Interpolation
            Aux__h = z_table[1]
            if Aux__g < Aux__h:
                # Positive slope
                Aux__f = Aux__g + ((Aux__h - Aux__g) * Aux__b) // Aux__d
            else:
                # Negative slope
                Aux__f = Aux__g - ((Aux__g - Aux__h) * Aux__b) // Aux__d

        # Differences in row axis
        Aux__a = x - x_table[0]
        Aux__i = x_table[1] - x_table[0]
        if Aux__i != 0:
            if Aux__e < Aux__f:
                # Positive slope
                Aux__e += ((Aux__f - Aux__e) * Aux__a) // Aux__i
            else:
                # Negative slope
                Aux__e -= ((Aux__e - Aux__f) * Aux__a) // Aux__i

        return Aux__e
