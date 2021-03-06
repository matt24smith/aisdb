from aisdb.tests.create_testing_data import random_polygons_domain
from aisdb.gis import DomainFromPoints


def test_domain():
    domain = random_polygons_domain(count=10)
    dist_to_centroids = domain.nearest_polygons_to_point(-64, 45)

    print(dist_to_centroids)

    for zone in domain.zones:
        poly = zone['geometry']
        # assert poly.is_valid
        print(poly.type, end='|')
    print()

    zoneID = domain.point_in_polygon(zone['geometry'].centroid.x,
                                     zone['geometry'].centroid.y)
    print(f'{zoneID = }')

    print(f'{domain.minX=}\n{domain.maxX=}\n{domain.minY=}\n{domain.maxY=}')


def test_DomainFromPoints():

    domain = DomainFromPoints([(-45, 50), (-50, 35), (-40, 55)],
                              [10000, 1000, 100000])
