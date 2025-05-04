import xml.etree.ElementTree as ET

from .axis import Axis  # , Value
from .curve import Curve
from .map import Map


class CDF:
    def __init__(self, filename) -> None:
        self.filename = filename
        tree = ET.parse(self.filename)
        self.root = tree.getroot()
        self.params = dict()

    def parse(self):
        params = dict()
        params["VALUE"] = dict()
        params["COM_AXIS"] = dict()
        params["CURVE"] = dict()
        params["MAP"] = dict()

        for child in self.root.iter("SW-INSTANCE"):
            data = self.sw_instance(child)
            match data["CATEGORY"]:
                case "VALUE":
                    params["VALUE"][data["SHORT-NAME"]] = data
                case "CURVE":
                    params["CURVE"][data["SHORT-NAME"]] = data
                case "MAP":
                    params["MAP"][data["SHORT-NAME"]] = data
                case "COM_AXIS":
                    params["COM_AXIS"][data["SHORT-NAME"]] = data
                case _:
                    params[data["SHORT-NAME"]] = data

        # TODO process CURVE and MAPS

        # need to process seperatly as requires COM-AXIS
        for key in params["COM_AXIS"].keys():
            self.params[key] = self.com_axis(params["COM_AXIS"][key])

        for key in params["CURVE"].keys():
            self.params[key] = self.curve(params["CURVE"][key])

        for key in params["MAP"].keys():
            self.params[key] = self.map(params["MAP"][key])

        for key in params["VALUE"].keys():
            self.params[key] = self.value(params["VALUE"][key])

        return self.params

    def value(self, data):
        # name = data["SHORT-NAME"]
        # unit = data["SW-VALUE-CONT"]["UNIT-DISPLAY-NAME"]
        value = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"][0]
        # res = dict()
        # res[name] = value
        return value

    def com_axis(self, data):
        name = data["SHORT-NAME"]
        values = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        return Axis(values, name)

    def curve(self, data):
        name = data["SHORT-NAME"]
        axis = data["SW-AXIS-CONTS"][0]
        match axis["CATEGORY"]:
            case "FIX_AXIS":
                x = Axis(axis["SW-VALUES-PHYS"])
            case "COM_AXIS":
                name = axis["SW-INSTANCE-REF"]
                x = self.params[name]
            case _:
                x = None
        y = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        return Curve(x, y, name)

    def map(self, data):
        name = data["SHORT-NAME"]
        x_axis = data["SW-AXIS-CONTS"][0]
        match x_axis["CATEGORY"]:
            case "FIX_AXIS":
                x = Axis(x_axis["SW-VALUES-PHYS"])
            case "COM_AXIS":
                name = x_axis["SW-INSTANCE-REF"]
                x = self.params[name]
            case _:
                x = None

        y_axis = data["SW-AXIS-CONTS"][1]
        match y_axis["CATEGORY"]:
            case "FIX_AXIS":
                y = Axis(y_axis["SW-VALUES-PHYS"])
            case "COM_AXIS":
                name = y_axis["SW-INSTANCE-REF"]
                y = self.params[name]
            case _:
                y = None

        z = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        map = Map(x, y, z, name)
        return map

    def category(self, item):
        return item.text

    def csentry(self, item):
        csentry = dict()
        for child in item:
            match child.tag:
                case "STATE":
                    self.state(child)
                case "DATE":
                    self.date(child)
                case "CSUS":
                    self.csus(child)
                case "CSPR":
                    self.cspr(child)
                case "CSWP":
                    self.cswp(child)
                case "CSTO":
                    self.csto(child)
                case "CSTV":
                    self.cstv(child)
                case "CSPI":
                    self.cspi(child)
                case "CSDI":
                    self.csdi(child)
                case "REMARK":
                    self.remark(child)
                case "SD":
                    self.sd(child)
                case _:
                    pass
        return csentry

    def csdi(self, item):
        return item.text

    def cspi(self, item):
        return item.text

    def cspr(self, item):
        return item.text

    def csto(self, item):
        return item.text

    def cstv(self, item):
        return item.text

    def csus(self, item):
        return item.text

    def cswp(self, item):
        return item.text

    def data_file(self, item):
        return item.text

    def date(self, item):
        return item.text  # TODO convert to datetime ?

    def display_name(self, item):
        return item.text

    def flag(self, item):
        return item.text

    def label(self, item):
        return item.text

    def locs(self, item):
        pass

    def long_name(self, item):
        return item.text

    def msrsw(self, item):
        self.short_name(item)
        self.category(item)
        self.sw_system(item)
        self.sdgs(item)
        self.locs(item)

    def nameloc(self, item):
        self.short_name(item)
        self.long_name(item)
        self.nmlist(item)

    def nmlist(self, item):
        return item.text

    def p(self, item):
        return item.text

    def remark(self, item):
        for child in item:
            self.p(child)

    def revision(self, item):
        return item.text

    def sd(self, item):
        return (item.attibute, item.text)

    def sdg(self, item):
        self.sdg_adaption(item)
        self.sd(item)
        self.sdg(item)

    def sdg_caption(self, item):
        self.short_name(item)
        self.long_name(item)

    def sdgs(self, item):
        self.sdg(item)

    def short_name(self, item):
        return item.text

    def state(self, item):
        pass

    def sw_array_index(self, item):
        pass

    def sw_arraysize(self, item):
        pass

    def sw_axis_cont(self, item):
        data = dict()
        for child in item:
            match child.tag:
                case "CATEGORY":
                    data["CATEGORY"] = self.category(child)
                case "UNIT-DISPLAY-NAME":
                    data["UNIT-DISPLAY-NAME"] = self.unit_display_name(child)
                case "SW-INSTANCE-REF":
                    data["SW-INSTANCE-REF"] = self.sw_instance_ref(child)
                case "SW-ARRAYSIZE":
                    data["SW-ARRAYSIZE"] = self.sw_arraysize(child)
                case "SW-VALUES-PHYS":
                    data["SW-VALUES-PHYS"] = self.sw_values_phys(child)
        return data

    def sw_axis_conts(self, item):
        data = []
        for child in item:
            match child.tag:
                case "SW-AXIS-CONT":
                    data.append(self.sw_axis_cont(child))
        return data

    def sw_collection_ref(self, item):
        pass

    def sw_cs_collection(self, item):
        pass

    def sw_cs_collections(self, item):
        pass

    def sw_cs_flag(self, item):
        pass

    def sw_cs_flags(self, item):
        pass

    def sw_cs_history(self, item):
        pass

    def sw_feature_ref(self, item):
        pass

    def sw_instance(self, item):
        data = dict()
        for child in item:
            match child.tag:
                case "SHORT-NAME":
                    data["SHORT-NAME"] = self.short_name(child)
                case "SW-ARRAY-INDEX":
                    data["SW-ARRAY-INDEX"] = self.sw_array_index(child)
                case "LONG-NAME":
                    data["LONG-NAME"] = self.long_name(child)
                case "DISPLAY-NAME":
                    data["DISPLAY-NAME"] = self.display_name(child)
                case "CATEGORY":
                    data["CATEGORY"] = self.category(child)
                case "SW-FEATURE-REF":
                    data["SW-FEARTURE-REF"] = self.sw_feature_ref(child)
                case "SW-VALUE-CONT":
                    data["SW-VALUE-CONT"] = self.sw_value_cont(child)
                case "SW-AXIS-CONTS":
                    data["SW-AXIS-CONTS"] = self.sw_axis_conts(child)
                case "SW-CS-HISTORY":
                    data["SW-CS-HISTORY"] = self.sw_cs_history(child)
                case "SW-CS-FLAGS":
                    data["SW-CS-FLAGS"] = self.sw_cs_flags(child)
                case "SW-INSTANCE-PROPS-VARIANTS":
                    data["SW-INSTANCE-PROPS-VARIANTS"] = (
                        self.sw_instance_props_variants(child)
                    )
                case _:
                    pass
        return data

    def sw_instance_props_variant(self, item):
        pass

    def sw_instance_props_variants(self, item):
        pass

    def sw_instance_ref(self, item):
        return item.text

    def sw_instance_spec(self, item):
        pass

    def sw_instance_tree(self, item):
        pass

    def sw_instance_tree_origin(self, item):
        pass

    def sw_system(self, item):
        pass

    def sw_value_cont(self, item):
        data = dict()
        for child in item:
            match child.tag:
                case "UNIT-DISPLAY-NAME":
                    data["UNIT-DISPLAY-NAME"] = self.unit_display_name(child)
                case "SW-ARRAYSIZE":
                    data["SW-ARRAYSIZE"] = self.sw_arraysize(child)
                case "SW-VALUES-PHYS":
                    data["SW-VALUES-PHYS"] = self.sw_values_phys(child)
        return data

    def sw_values_phys(self, item):
        values = []
        for child in item:
            match child.tag:
                case "VT":
                    values.append(self.vt(child))
                    # return self.vt(child)
                case "VG":
                    values.append(self.vg(child))
                    # return self.vg(child)
                case "V":
                    values.append(self.v(child))
                    # return self.v(child)
        return values

    def sw_vcd_criterion_ref(self, item):
        pass

    def sw_vcd_crterion_value(self, item):
        pass

    def symbolic_file(self, item):
        pass

    def unit_display_name(self, item):
        return item.text

    def v(self, item):
        return float(item.text)

    def vg(self, item):
        values = []
        for child in item:
            match child.tag:
                case "VT":
                    values.append(self.vt(child))
                    # return self.vt(child)
                case "V":
                    values.append(self.v(child))
                    # return self.v(child)
        return values

    def vt(self, item):
        return item.text
