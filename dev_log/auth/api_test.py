import pandas as pd
import googlemaps
from itertools import tee

gmaps = googlemaps.Client(key= 'AIzaSyDLCCZa9YjI1Swt2vRuotgrCLBaWijDEK8')

distance = gmaps.distance_matrix('32 rue Florence Arthaud France','3 rue Joliot Curie Gif-sur-Yvette')
print(distance)