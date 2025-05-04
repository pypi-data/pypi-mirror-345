class Axis:
    def __init__(self, values, name="") -> None:
        self.name = name
        self.values = values

    def insert(self, value):
        """
        Insert a value in the monotone axis and return the position of insertion
        """
        pass

    # def append(self, value):
    #     self.values.append(value)

    def value(self, pos):
        return self.values[pos]
