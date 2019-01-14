 gmaps = googlemaps.Client(key='AIzaSyDLCCZa9YjI1Swt2vRuotgrCLBaWijDEK8')
>>> distance = gmaps.distance_matrix('32 rue Florence Arthaud Massy France', '3 rue Joliot-Curie Gif-sur-Yvette France')
>>> print(distance)



distance = gmaps.distance_matrix({'lat' : 48.2586, 'lng' : 2.263},{'lat' : 49 , 'lng' : 2})
>>> print(distance)



distance = gmaps.distance_matrix([{'lat' : 48.2586, 'lng' : 2.263},{'lat' : 48.723, 'lng' : 2.263}],[{'lat' : 49, 'lng' : 2}, {'lat' : 50, 'lng' : 3}])
>>> print(distance)



lieux = [(48.2586, 2.263),(48.723, 2.263),(49, 2),(50, 3)]
>>> distance = gmaps.distance_matrix(lieux, lieux)
>>> print(distance)

import googlemaps
import numpy as np

def matrix_distance(addresses, key, mode):
    gmaps = googlemaps.Client(key= str(key))
    distance = gmaps.distance_matrix(addresses, addresses, mode)
    length = len(addresses)
    matrix_distance = np.zeros((length, length))
    for i in range(length):
        for j in range(length):
            matrix_distance[i][j] = distance['rows'][i]['elements'][j]['duration']['value']

