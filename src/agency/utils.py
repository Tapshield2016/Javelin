from math import sin, cos, sqrt, atan2, radians
from django.contrib.gis.geos import Point


def kilometers_between_coordinates(point1, point2):

    to_km = 6371 # km

    lat1 = radians(point1.x)
    lon1 = radians(point1.y)
    lat2 = radians(point2.x)
    lon2 = radians(point2.y)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = to_km * c
    return distance


def radius_from_center(point, boundaries):

    point2 = Point(0, 0)
    max_distance = 0

    for string in boundaries:
        split = string.split(',')
        point2.x = float(split[1])
        point2.y = float(split[0])

        distance = kilometers_between_coordinates(point, point2)

        if distance > max_distance:
            max_distance = distance

    return max_distance*0.621371  # miles


def centroid_from_boundaries(boundaries):

    x_coordinates = []
    y_coordinates = []

    for x in boundaries:
        split = x.split(',')
        x_coordinates.append(float(split[0]))
        y_coordinates.append(float(split[1]))

    signed_area = 0.0
    centroid = Point(0, 0)

    for i in range(len(x_coordinates)):

        x0 = x_coordinates[i]
        y0 = y_coordinates[i]

        j = i+1
        if i == len(x_coordinates)-1:
            j = 0

        x1 = x_coordinates[j]
        y1 = y_coordinates[j]
        a = x0*y1 - x1*y0
        signed_area += a
        centroid.x += (x0 + x1)*a
        centroid.y += (y0 + y1)*a

    signed_area *= 0.5
    centroid.x /= (6.0*signed_area)
    centroid.y /= (6.0*signed_area)

    return centroid
