# Python classes for generic measurment zone, e.g. heart rate or speed
import jsonpickle

class Zone():
    def __init__(self, min, max, colour):
        self.min = min
        self.max = max
        self.colour = colour
    def __str__(self):
        smin = ''
        smax = ''
        if self.min is not None:
            smin = f'{self.min:.0f}'
        if self.max is not None:
            smax = f'{self.max:.0f}'
        return f'{smin}-{smax}'

class HeartRateZones():
    def __init__(self, name='Polar Basic', max=200):
        self.name = name
        self.max = max
        self.zones = {'Zone 1': Zone(max*0.5, max*0.6, 'g'),
                      'Zone 2': Zone(max*0.6, max*0.7, 'y'),
                      'Zone 3': Zone(max*0.7, max*0.8, 'c'),
                      'Zone 4': Zone(max*0.8, max*0.9, 'r')}
    def __str__(self):
        str = f'Heart Rate Zones: "{self.name}"'
        zns = ''
        for name, zone in self.zones.items():
            zns = (f'{zns}\n\t{name} {zone}')
        return f'{str}{zns}'
        
    def __repr__(self):
       return (f'{self.__class__.__name__}('
               f'{self.name!r}, {self.max})')

    def setZones(self, zones):
        self.zones = zones
        
    @staticmethod
    def loadZones(filename):
        with open(filename, "r") as f:
            loaded = jsonpickle.decode(f.read())
            return loaded

    def addOrUpdateZone(self, name, hr_min, hr_max, colour='r'):
        self.zones[name] = [hr_min, hr_max, colour]
