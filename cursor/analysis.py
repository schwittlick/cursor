import numpy as np

class Histogram:
    def __init__(self):
        pass

    def get(self, data):
        if isinstance(data, list):
            return np.histogram(data, bins=10) # bins = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180])
