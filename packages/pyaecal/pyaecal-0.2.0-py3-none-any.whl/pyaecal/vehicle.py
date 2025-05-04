import numpy

from .engine import Engine
from .gearbox import Gearbox
from .resistance import Resistance

# TODO vehicle configuration from JSON file


class Vehicle(object):
    """
    class to represent a vehicle and basic calulation for the vehicle configuration

    """

    def __init__(self):
        super().__init__()
        self.name = "vehicle"
        self.gearbox = Gearbox()
        self.engine = Engine()
        self.resistance = Resistance(1, 1, 1)
        self.rar = 2.15
        self.dynradius = 0.503

    def energy(self, n, gear, mass):
        return 0.5 * mass * self.engine_to_speed(n, gear) ** 2

    def engine_to_speed(self, engine, gear):
        """
        Returns the vehicle speed from the engine speed and the common powertrain ratio
        :param engine: engine speed in 1/min
        :param gear: gear number
        :return: vehicle speed in m/s
        """
        res = engine / 60 / self.ratio(gear) * self.dynradius * 2 * numpy.pi
        return res #.astype(float)

    def fresist(self, speed, mass, grade=0):
        """
        Returns the resistance force by entering the vehicle speed and the ratio
        (default ratio = 1)
        :param speed: vehicle speed in m/s
        :param mass: total vehicle mass in kg
        :param grade: road grade
        :return: resistance force in N
        """
        return self.resistance.resistance(speed, mass, grade)

    def force_to_torque(self, f, gear):
        """
        Returns the engine torque from the traction force and the common powertrain
         ratio
        :param f: traction force in N
        :param ratio: common powertrain ratio
        :return: engine torque in Nm
        """
        return f * self.dynradius / self.ratio(gear)

    def ratio(self, gear):
        """
        return the gear ration from the given gear

        :param gear: gear number
        :return: trans ratio (gear and rear axle ratio)
        """
        return self.gearbox.ratio(gear) * self.rar

    def speed_to_engine(self, speed, gear):
        """
        Returns the engine speed from the vehicle speed and the common powertrain ratio
        :param speed: vehicle speed in m/s
        :param gear: gear number
        :return: engine speed in 1/min
        """
        res = speed / (2 * numpy.pi * self.dynradius) * self.ratio(gear) * 60
        return res #.astype(float)

    def torque(self, n, pedal=100):
        """
        By default, this function returns the torque at an engine speed with a max
         percentage torque (100% is full torque)
        :param n: engine speed in rpm
        :param pedal: percentage value of the accelerator pedal; default 100% means
         full torque
        :return: engine torque in Nm
        """
        return self.engine.torque(n)

    def torque_to_force(self, t, gear):
        """
        Returns the traction force from the engine torque and the common powertrain
         ratio
        :param t: engine torque in Nm
        :param ratio: common powertrain ratio
        :return: traction force in N
        """
        return t * self.ratio(gear) / self.dynradius
