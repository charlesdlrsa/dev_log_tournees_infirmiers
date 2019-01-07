# -*- coding: utf-8 -*-

# @author Romain Pascual

# @class Space

from point import Point
import math
from operator import attrgetter

class Space :
    
    ## Attributes :
    # nb_points: number of points
    # points: list of the points
    # dmin: minimal distance between two points in the space
    # dmax: maximal distance between two points in the space
    
    # -------------------------------------------------------------------------
    # -- INITIALIZATION
    # -------------------------------------------------------------------------

    def __init__(
            self,
            nb_points = 0,
            points = []):
        
        self.nb_points = nb_points
        self.points = points
        self.points_by_long = []
        self.points_by_lat = []
        self.points_lex_sorted = []
        self.upperConvexHull = []
        self.lowerConvexHull = []
        self.dmin = None
        self.dmax = None
        
        self.centerSize = []
    
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- CREATION 
    # -------------------------------------------------------------------------
    def buildSpaceFromDict(self, patients):
        """
        Build a 2D space from a given dictionnary of patients.
        @param patients: a dict of the patients to be seen.
            k = patient_id
            v = position (latitude, longitude)
        """

        # setting attributs
        self.nb_points = 0
        self.points = []

        # process patients
        for patient_id, patient_position in patients.items():
            self.nb_points += 1
            self.points.append(Point(patient_id,patient_position[0], patient_position[1]))
        
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- PRE COMPUTATION
    # -------------------------------------------------------------------------
    
    def sortByLong(self):
        """
        Sort the points in the space according to their longitude.
        """
        self.points_by_long = self.points.copy()
        self.points_by_long.sort(key=attrgetter("longitude"))
    
    def sortByLat(self):
        """
        Sort the points in the space according to their latitude.
        """
        self.points_by_lat = self.points.copy()
        self.points_by_lat.sort(key=attrgetter("latitude"))
           
    def lexSort(self):
        """
        Sort the points in the space according to their (longitude, latitude),
        using lexicographic order.
        """
        self.points_lex_sorted = self.points.copy()
        self.points_lex_sorted.sort(key=(attrgetter("longitude", "latitude")))
    
    def surface(self):
        """
        Determine the rectangular surface in which the points are.
        """
        if not self.points_by_long:
            self.sortByLong()
        if not self.points_by_lat:
            self.sortByLat()
        
        delta_long = self.points_by_long[-1].getLongitude() - self.points_by_long[0].getLongitude()
        delta_lat = self.points_by_lat[-1].getLatitude() - self.points_by_lat[0].getLatitude()
        
        return delta_lat * delta_long
        
    # -------------------------------------------------------------------------
     
    # -------------------------------------------------------------------------
    # -- DMIN USING DIVIDE AND CONQUER
    # -------------------------------------------------------------------------
        
    def bruteForce(self,points_by_long):
        """
        Brute force guess for small instances
        """
        p1 = points_by_long[0]
        p2 = points_by_long[1]
        dmin = p1.squaredDistanceTo(p2)
        if dmin == 0:
            dmin = math.inf
        length = len(points_by_long)
        if length == 2:
            return p1, p2, dmin
        for i in range(0,length-1):
            for j in range(i+1, length):
                if i != 0 and j != 1:
                    p, q = points_by_long[i], points_by_long[j]
                    if not p.sameLocation(q):
                        d = p.squaredDistanceTo(q)
                        if d < dmin:
                            p1, p2, dmin = p, q, d
        return p1, p2, dmin
    
    def closestPairCenter(self, center, dist, pmin,qmin):
        """
        Compute the minimum distance in the center
        """
        p1, p2, dmin = pmin, qmin, dist
        length = len(center) 
        for i in range(length - 1):
            for j in range(i+1, min(i + 7, length)):
                p, q = center[i], center[j]
                if not p.sameLocation(q):
                    d = p.squaredDistanceTo(q)
                    if d < dmin:
                        p1, p2, dmin = p, q , d
        return p1, p2, dmin
    
    def closestPair(self,points_by_long, points_by_lat, stop = 3):
        """
        Implementation of the divide and conquer
        """
        # Brute force for small instances
        length = len(points_by_long)
        if length <= stop:
            return Space.bruteForce(self,points_by_long)
        
        # divide
        med = length // 2
        leftLong = points_by_long[:med]
        rightLong = points_by_long[med:]
        longitude_midpoint = points_by_long[med].getLongitude()  
        leftLat = list()
        rightLat = list()
        for x in points_by_lat:
            if x.getLongitude() <= longitude_midpoint:
               leftLat.append(x)
            else:
               rightLat.append(x)
    
        # recursive calls
        p1, q1, dmin1 = Space.closestPair(self,leftLong, leftLat, stop = stop)
        p2, q2, dmin2 = Space.closestPair(self,rightLong, rightLat, stop = stop)
    
        if dmin1 <= dmin2:
            p, q, d = p1, q1, dmin1
        else:
            p, q, d = p2, q2, dmin2
    
        # get the min distance for points in the middle
        center = [points for points in points_by_lat if longitude_midpoint - d <= p.getLongitude() <= longitude_midpoint - d]
        p3, q3, dmin3 = Space.closestPairCenter(self, center, d, p,q)
        
        if d <= dmin3:
            return p, q, d
        else:
            return p3, q3, dmin3
    
    def computeDmin(self, stop=10):
        """
        Compute dmin using a divide and conquer approach
        """
        self.sortByLat()
        self.sortByLong()
        p1, p2, dmin = Space.closestPair(self,self.points_by_lat,self.points_by_long,stop=stop)
        return p1,p2,dmin

    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- Computing Dmax using a convex hull algorithm
    # -------------------------------------------------------------------------
    """
    Andrew's monotone chain algorithm is used to build the convex hull and
    Shamos algorithm (based on rotating calipers) to compute the diamater of the
    convex hull.
    """
    
    def orient (self, p, q, r):
        """
        Determine if the points are clockwise oriented (returned value = 1),
        counter-clockwise oriented (returned vlaue = 1) or colinear (returned 
        value = 0). p is taken as the origin of the two vectors
        """
        px, py = p.getLongitude(), p.getLatitude()
        qx, qy = q.getLongitude(), q.getLatitude()
        rx, ry = r.getLongitude(), r.getLatitude()
        
        cp1 = (qy - py) * (rx - px)
        cp2 = (qx - px) * (ry - py)
        
        return (cp1 > cp2) - (cp1 < cp2)
    
    def convexHull(self):
        upper = list()
        lower = list()
        
        if not self.points_lex_sorted:
            self.lexSort()
        
        for p in self.points_lex_sorted:
            while len(upper) > 1 and Space.orient(self, upper[-2], upper[-1], p) != 1:
                upper.pop()
            while len(lower) > 1 and Space.orient(self, lower[-2], lower[-1], p) != 1:
                lower.pop()
            upper.append(p)
            lower.append(p)
        
        self.upperConvexHull = upper
        self.lowerConvexHull = lower
    
    def computeDmax(self):
        """
        Computte dmax using rotation calipers on the convex hull.
        """        
        p1, p2, dmax = None, None, 0
        
        if not (self.upperConvexHull and self.lowerConvexHull):
            Space.convexHull(self)
        
        
        length_upper = len(self.upperConvexHull) - 1
        rotating_calipers = []
        upper_index = 0
        lower_index = len(self.lowerConvexHull) - 1
        while upper_index < length_upper or lower_index > 0:
            rotating_calipers.append((self.upperConvexHull[upper_index],self.lowerConvexHull[lower_index]))
            
            # upper finished
            if upper_index == length_upper:
                lower_index -= 1
                
            # lower finished
            elif lower_index == 0:
                upper_index += 1
            
            # none finished
            else:
                u_px, u_py = self.upperConvexHull[upper_index].getLongitude(), self.upperConvexHull[upper_index].getLatitude()
                u_npx, u_npy = self.upperConvexHull[upper_index+1].getLongitude(), self.upperConvexHull[upper_index+1].getLatitude()
                l_px, l_py = self.lowerConvexHull[lower_index].getLongitude(), self.lowerConvexHull[lower_index].getLatitude()
                l_npx, l_npy = self.lowerConvexHull[lower_index-1].getLongitude(), self.lowerConvexHull[lower_index-1].getLatitude()
                
                if (u_npy - u_py) * (l_px - l_npx) > (l_py - l_npy) * (u_npx - u_px):
                    upper_index += 1
                else:
                    lower_index -= 1
            
        for p,q in rotating_calipers:
            if not p.sameLocation(q):
                d = p.squaredDistanceTo(q)
                if d > dmax:
                    p1, p2, dmax = p, q, d
        return p1, p2, dmax
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- Extremal distances
    # -------------------------------------------------------------------------
    
    def computeExtremalDistances(self):
        """
        Compute the extremal distances using the two algorithms explained above.
        """
        if self.dmin is None or self.dmax is None:
            p1, p2, dmin = Space.computeDmin(self)
            p1, p2, dmax = Space.computeDmax(self)
            self.dmin, self.dmax = math.sqrt(dmin), math.sqrt(dmax)
            
            # freeing memory
            self.points_by_long = []
            self.points_by_lat = []
            self.points_lex_sorted = []
            self.upperConvexHull = []
            self.lowerConvexHull = []