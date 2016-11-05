from miso_tables import models

with open("./data_loading/files/node_GPS_locations_full.csv", "r") as f:
    for line in f.readlines()[1:]:
        name, latitude, longitude, _, _ = line.split(",")
        longitude = float(longitude.strip())
        latitude = float(latitude.strip())
        node = models.Node.objects.filter(name=name.strip())
        if node.count() > 0:
            assert node.count() == 1
            print(name)
            node = node[0]
            node.longitude = longitude
            node.latitude = latitude
            node.save()