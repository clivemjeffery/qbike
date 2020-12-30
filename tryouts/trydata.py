import jsonpickle
import zones

def setZones(hrzones):
    cts_zones = {'Endurance': zones.Zone(133, 158, 'g'),
                 'Tempo': zones.Zone(153, 157, 'y'),
                 'Steady': zones.Zone(160, 164, 'r'),
                 'Climb': zones.Zone(None, 169, 'c'),
                 'Power': zones.Zone(174, None, 'm')}
    hrzones.setZones(cts_zones)

# prototype a heart rate zones set
basicHeartZones = zones.HeartRateZones(max=220-55)
print(basicHeartZones)

ctsHeartZones = zones.HeartRateZones(name='CTS Zones')
setZones(ctsHeartZones)
print(ctsHeartZones)

filename = "hr_zones.json"
original = ctsHeartZones
reloaded = None

with open(filename, "w") as f:
    f.write(jsonpickle.encode(original))

reloaded = zones.HeartRateZones.loadZones(filename)
print(reloaded)
