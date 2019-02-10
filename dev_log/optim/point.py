# -*- coding: utf-8 -*-

# @author Romain Pascual

import math

# @class Point

class Point :
    """
    Point in the euclidien space.
            
    Attributes:
        id: patient id of wanting an appointment
        longitude: longitude of the point in the euclidien space
        latitude: latitude of the point in the euclidien space
    """

    ## Earth Radius
    R = 6373.0

    
    def __init__(
            self,
            id = 0,
            lat = 0, # y axis
            lon = 0): # x axis
        
        self.id = id
        self.longitude = lon
        self.latitude = lat
        
    def getID(self):
        return self.id
    
    def getLongitude(self):
        return self.longitude
    
    def getLatitude(self):
        return self.latitude
    
    def squaredDistanceTo(self,other):
        """
        Compute the square of the euclidien distance between two points
        """
        if not isinstance(other,Point):
            return 
        return (self.longitude - other.getLongitude())**2 +(self.latitude - other.getLatitude())**2
    
    def distanceTo(self,other):
        """
        Compute the euclidien distance between two points
        """
        if not isinstance(other,Point):
            return 
        return math.sqrt((self.longitude - other.getLongitude())**2 +(self.latitude - other.getLatitude())**2)
    
    def distanceKmTo(self, other):
        """
        Compute the distance in kilometers between two points
        """
        lon1 = math.radians(self.longitude)
        lon2 = math.radians(other.longitude)
        dlon = lon2 - lon1
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlat = lat2 - lat1

        
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return Point.R * c
        

    def sameLocation(self, other):
        """
        Determine if two points are at the same location (faster than testing d ==0)
        """
        if not isinstance(other,Point):
            return False
        return self.longitude == other.getLongitude() and self.latitude == other.getLatitude()
    
    
    # -------------------------------------------------------------------------
    # -- Override Object methods
    # -------------------------------------------------------------------------
    
    def __eq__(self, other):
        """
        Equality testing
        """
        if not isinstance(other,Point):
            return False
        return (self.id == other.getID() and self.longitude == other.getLongitude()) \
                and self.latitude == other.getLatitude()
    
    def __hash__(self):
        """
        Hash function on the points so they can be stored in sets, dictionnaries, ...
        """
        return hash((self.id, self.longitude, self.latitude))
    
    def __repr__(self):
        return "Point[id: {}, longitude {}, latitude {}]".format(
                self.id, self.longitude, self.latitude)

    def __str__(self):
        return "[id: {}, longitude {}, latitude {}]".format(
                self.id, self.longitude, self.latitude)


    # -------------------------------------------------------------------------
    # -- Some tests
    # -------------------------------------------------------------------------

if __name__ == "__main__":
    import random
    patients = []
    for k in range(1,15,2):
        patients.append(Point(k, 360. * (random.random()-.5), 180. * (random.random()-.5)))
    print(patients)

    print("distance between two points is the square root of the squared distance between these two points?",\
    patients[0].distanceTo(patients[1]) == math.sqrt(patients[0].squaredDistanceTo(patients[1])))