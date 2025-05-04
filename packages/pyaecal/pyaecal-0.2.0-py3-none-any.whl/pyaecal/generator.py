# DCM writer

# from curve import Curve
# from map import Map


class Generator:
    # TODO generate from Map
    # TODO generate from Curve
    def __init__(self, version=2) -> None:
        self.version = version

    def close(self):
        self.f.close()

    def FESTWERT(self, name, value):
        output = ""
        output += "FESTWERT %s\n" % (name)
        output += "WERT %s\n" % (value)
        output += "END\n\n"
        return output

    # def FESTWERTEBLOCK(self, name, valueList):
    #     output+="FESTWERTEBLOCK %s\n" % (name))
    #     output+="WERT %s\n" % (valueList))
    #     output+="END\n\n")

    # def KENNFELD(self, name, x, y):
    #     pass

    # def FESTKENNFELD(self):
    #     pass

    # def KENNLINIE(self, name, x, v):
    #     self.param[name] = {"X": x, "Y": v, "Z": None}
    #     output+="KENNLINIE %s %i\n" % (name, len(x)))
    #     output+="%s" % (self.STX(x)))
    #     output+="%s" % (self.WERT(v)))
    #     output+="END\n\n")

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
