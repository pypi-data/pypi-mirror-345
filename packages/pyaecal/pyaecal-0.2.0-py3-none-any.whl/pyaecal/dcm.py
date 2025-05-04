from .axis import Axis
from .curve import Curve

# from .value import Value
# from .generator import Generator
from .map import Map

# from .parser import Parser

# from pathlib import Path


class DCM(object):
    """
    DCM class import and export DCM file format
    """

    def __init__(self, filename, version=2):
        super().__init__()
        self.filename = filename
        self.version = version

        self.params = dict()
        self.output = dict()

    def map(self, map):
        """
        Generate output for Map
        """
        x = map._x
        if x.name == "":
            print(map.name)
        self.output[x.name] = self.STUETZSTELLENVERTEILUNG(x.name, x.values)
        y = map._y
        self.output[y.name] = self.STUETZSTELLENVERTEILUNG(y.name, y.values)

        self.output[map.name] = self.GRUPPENKENNFELD(map)

    def curve(self, curve):
        """
        generate output for curve
        """
        if isinstance(curve._x, Axis):
            x = curve._x
            if x.name == "":
                self.output[curve.name] = self.FESTKENNLINIE(
                    curve.name, curve._x.values, curve._y
                )
            else:
                self.output[x.name] = self.STUETZSTELLENVERTEILUNG(x.name, x.values)
                self.output[curve.name] = self.GRUPPENKENNLINIE(curve)
        else:
            self.output[curve.name] = self.FESTKENNLINIE(curve.name, curve._x, curve._y)

    def value(self, value, name):
        """
        Generate output for value
        """
        self.output[name] = self.FESTWERT(name, value)

    def generate(self):
        """
        Generate the DCM file
        """
        # writer = Generator()
        file = open(self.filename, "w")
        for key in self.params.keys():
            param = self.params[key]
            if type(param) is Map:
                self.map(param)
                continue
            if type(param) is Curve:
                self.curve(param)
                continue
            if type(param) is Axis:
                continue
            self.value(param, key)
        for key in self.output.keys():
            file.write(self.output[key])
        file.close()

    def FESTWERT(self, name, value):
        output = ""
        output += "FESTWERT %s\n" % (name)
        output += "WERT %s\n" % (value)
        output += "END\n\n"
        return output

    def FESTKENNLINIE(self, name, x, v):
        output = ""
        output += "FESTKENNLINIE %s %i\n" % (name, len(x))
        output += "%s" % (self.STX(x))
        output += "%s" % (self.WERT(v))
        output += "END\n\n"
        return output

    def STUETZSTELLENVERTEILUNG(self, name, v):
        output = ""
        output += "STUETZSTELLENVERTEILUNG %s %i\n" % (name, len(v))
        output += "*SST\n"
        output += "%s" % (self.STX(v))
        output += "END\n\n"
        return output

    def GRUPPENKENNLINIE(self, curve):
        output = ""
        output += "GRUPPENKENNLINIE %s %i\n" % (curve.name, len(curve._x.values))
        output += "*SSTX %s\n" % (curve._x.name)
        output += "%s" % (self.STX(curve._x.values))
        output += "%s" % (self.WERT(curve._y))
        output += "END\n\n"
        return output

    def GRUPPENKENNFELD(self, map):
        output = ""
        output += "GRUPPENKENNFELD %s %i %i\n" % (
            map.name,
            len(map._x.values),
            len(map._y.values),
        )
        output += "*SSTX %s\n" % (map._x.name)
        output += "*SSTY %s\n" % (map._y.name)
        output += "%s" % (self.STX(map._x.values))
        for y in map._y.values:
            output += "%s" % (self.STY([y]))
            wert = [map.z(x, y) for x in map._x.values]
            output += "%s" % (self.WERT(wert))
        output += "END\n\n"
        return output

    def STX(self, data):
        res = ""
        for block in [data[i : i + 6] for i in range(0, len(data), 6)]:
            res = "%s\tST/X" % res
            for i in block:
                res = "%s\t%s" % (res, i)
            res = "%s\n" % res
        return res

    def STY(self, data):
        res = ""
        for block in [data[i : i + 6] for i in range(0, len(data), 6)]:
            res = "%s\tST/Y" % res
            for i in block:
                res = "%s\t%s" % (res, i)
            res = "%s\n" % res
        return res

    def WERT(self, data):
        res = ""
        # TODO max text length !
        for block in [data[i : i + 6] for i in range(0, len(data), 6)]:
            res = "%s\tWERT" % res
            for i in block:
                res = "%s\t%s" % (res, i)
            res = "%s\n" % res
        return res
