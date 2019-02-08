# -*- coding: utf-8 -*-

# @author Romain Pascual
# @author Maxime Dieudionne

# @class Space

"""

TODO: 
    recluster -> issue with office
    assignNurse -> do LP
    solve
    mettre en forme les sorties
    functions solve_boolean(data) and solve_complete(data)
    clean le code

ISSUES:
    reclustering -> some solutions are infeasible


function naming:
solve_boolean(data)
solve_complete(data)

Output: list of two dicts
[{"nurse_id":"id", "app_id":"id", "hour":"hh:mm"}]
[{"app_id:"id, "travel_mode":["driving"/"walking"]}]



Use of the Distance Matrix service for existing Premium Plan customers

In order to switch over to the new pay as you go pricing plan, you must create a new project, as your existing Premium project cannot be transferred. You must get new API keys, and use them to to replace your existing keys. Please contact your account manager and/or reseller to coordinate your transition to the new plan before your current Premium license expires. In the meantime, your Premium Plan quotas remain in effect.

    Shared daily free quota of 100,000 elements per 24 hours; additional requests applied against the annual purchase of Maps APIs Credits.
    Limited to 100 elements per client-side request.
    Maximum of 25 origins and 25 destinations per server-side request.
        Server-side requests using mode=transit or using the optional parameter departure_time when mode=driving are limited to 100 elements per request.
    1,000 server-side elements per second. *Note that the client-side service offers Unlimited elements per second, per project.


googlemaps.exceptions.ApiError: MAX_ELEMENTS_EXCEEDED

"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
import math
import time
import re
from point import Point
from operator import attrgetter
from amplpy import AMPL, Environment
import numpy as np
import googlemaps
from key import key
googlekey = key

class GmapApiError(Exception):
    pass

class Space :
    
    ## Attributes :
    # nb_points: number of points
    # points: list of the points
    # dmin: minimal distance between two points in the space
    # dmax: maximal distance between two points in the space

    clustering_factor = 0.5
    
    # -------------------------------------------------------------------------
    # -- INITIALIZATION
    # -------------------------------------------------------------------------

    def __init__(
            self,
            nb_points = 0,
            points = [],
            walkingThreshold = 2.0):
        
        self.nb_points = nb_points
        self.points = points
        self.walkingThreshold =walkingThreshold
        self.points_by_long = []
        self.points_by_lat = []
        self.points_lex_sorted = []
        self.upperConvexHull = []
        self.lowerConvexHull = []
        self.dmin = None
        self.dmax = None
    
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- PARSE 
    # -------------------------------------------------------------------------

    def buildSpaceFromDic(self, dataDict):
        """
        Build a 2D space from a given dictionnary describing the data.
        @param dataDict: json like dictionnary describing the data:
            - "start" : "hh:mm"
                starting time, format is two digits for hour, two points and two digits for minutes
            - "end" : "hh:mm"
                endging time, format is two digits for hour, two points and two digits for minutes
            -'nurse_id' : ["id1", "id2", ...]
                list of nurse ids in string format
            - "office_lat" : "lat"
                office latitude in string format
            - "office_lon" : "lon"
                office longitude in string format
            - "appointments" : list[dict]
                list of nested json like dictionnaries describing the appointments.
                one dictionnary is described as follows:
                    - "app_id" : "id"
                        appointment id in string format
                    - "app_lat" : "lat"
                        appointment latitude in string format
                    - "app_lon" : "lon"
                        appointment longitude in string format
                    - "app_length" : "mm"
                        duration of care performed at the given appointment in minutes
        """
        self.start = [int(x) for x in dataDict["start"].split(":")]
        self.end = [int(x) for x in dataDict["end"].split(":")]
        self.duration = (self.end[0] - self.start[0])*3600 + (self.end[1] - self.start[1]) * 60
        self.nurse_ids = [int(x) for x in dataDict["nurse_id"]]
        self.points = [Point(id=0, lat=float(dataDict["office_lat"]), lon=float(dataDict["office_lon"]))]
        self.care_duration[0] = 0
        self.nb_points = 1
        self.care_duration = dict()
        for app in dataDict["appointments"]:
            self.points.append(Point(id=int(app["app_id"]), lat=float(app["app_lat"]), lon=float(app["app_lon"])))
            self.nb_points += 1
            self.care_duration[int(app["app_id"])] = 60 * int(app["app_length"])



    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- CREATION 
    # -------------------------------------------------------------------------

    def buildSpaceFromDB(self, office, patients, nurse_ids=[], cares=[], start = [8,0], end = [12,0]):
        """
        Build a 2D space from a given dictionnary of patients and the realted office.
        @param office: position of the office(latitude, longitude)
        @param patients: a dict of the patients to be seen.
            k = patient_id
            v = position (latitude, longitude)
        """

        # setting attributs
        self.nb_points = 0
        self.points = []
        self.start = start
        self.end = end
        self.duration = (self.end[0] - self.start[0])*3600 + (self.end[1] - self.start[1]) * 60

        # add office
        self.nb_points +=1
        self.points.append(Point(0, office[0], office[1]))
        self.care_duration = dict()
        self.care_duration[0] = 0

        # process nurses
        self.nurse_ids = nurse_ids
        if len(self.nurse_ids) == 0:
            self.nurse_ids = [0]

        # process patients
        for patient_id, patient_position in patients.items():
            try:
                self.care_duration[patient_id] = cares[self.nb_points-1]
            except IndexError:
                self.care_duration[patient_id] = 1800
            self.nb_points += 1
            self.points.append(Point(patient_id,patient_position[0], patient_position[1]))

    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- Finders 
    # -------------------------------------------------------------------------
    def getCareDuration(self):
        """
        Return the care duration list
        """
        return self.care_duration

    def getPointByID(self, id):
        """
        Return the point in the space having the given id if exists, None otherwise.
        """
        for p in self.points:
            if p.getID() == id:
                return p
        return None
    
    def getListPointsByID(self, listIds):
        """
        Return the list of points in the space having the given ids, can be empty.
        """
        l = []
        self.sortByID()
        lID = sorted(listIds)
        i_list = 0
        i_points = 0
        n = len(lID)

        while i_list < n and i_points < self.nb_points:
            if lID[i_list] == self.points_by_id[i_points].getID():
                l.append(self.points[i_points])
                i_list += 1
                i_points += 1
            elif lID[i_list] < self.points_by_id[i_points].getID():
                i_list += 1
            else:
                i_points += 1
        
        del self.points_by_id

        return l

    def rotateToStartingPoint(self, path, starting_point):
        while path[0].getID() != starting_point:
            point = path.pop(0)
            path.append(point)
        path.append(path[0])

    def regenerateCyclingPath(self, listPoints, amplMatPath, travel_times, starting_point):
        """
        Given a list of points and the ampl transition matrix, rebuild the path.
        @param listPoints: list of points (id, lat, lon) such that its order is the same as
        the index in amplMatPath
        @param amplMatPath: transition matrix (returned by ampl) describing the path 
        (zero, one matrix) such that:
            amplMatPath[i,j] = 1 iff the path goes from listPoint[i] to listPoint[j]
        @param travel_times: time matrix such that travel_times[i][j] is the time to 
        travel from from listPoint[i] to listPoint[j].
        """
        n = len(listPoints)
        i = 0
        j = -1
        path = []
        travel_time = 0
        while j != 0:
            for k in range(n):
                if i != k and amplMatPath[i+1,k+1].value():
                    j = k
            travel_time += travel_times[i][j]
            i = j
            path.append(listPoints[i])
        self.rotateToStartingPoint(path, starting_point)
        return path, travel_time

    
    def buildVRPSolution(self, listCenters, amplMatPath, travel_times, path_number):
        """
        Given a list of points and the ampl transition matrix, rebuild the differents
        pathes (according to the number of pathes).
        Return a list of path x time.

        @param listPoints: list of points (id, lat, lon) such that its order is the same as
        the index in amplMatPath
        @param amplMatPath: transition matrix (returned by ampl) describing the path 
        (zero, one matrix) such that:
            amplMatPath[i,j] = 1 iff one path goes from listPoint[i] to listPoint[j]
        @param travel_times: time matrix such that travel_times[i][j] is the time to 
        travel from from listPoint[i] to listPoint[j].
        @param path_number: number of pathes that we try to rebuild
        """
        n = len(listCenters)
        VRP = []
        for p in range(n):
            if p != 0 and amplMatPath[1,p+1].value():
                i = p
                j = -1
                path = [listCenters[0], listCenters[p]]
                travel_time = travel_times[0][p]
                while j != 0:
                    for k in range(n):
                        if i != k and amplMatPath[i+1,k+1].value():
                            j = k
                    travel_time += self.clusterTime[listCenters[i].getID()] + travel_times[i][j]
                    i = j
                    path.append(listCenters[i])
                VRP.append([path,travel_time])
        return VRP
        
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

    def sortByID(self):
        """
        Sort the points in the space according to their id.
        """
        self.points_by_id = self.points.copy()
        self.points_by_id.sort(key=attrgetter("id"))
           
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
    
    def computeKmDistance(self):
        """
        Compute the matrix of distance between the points using distance as the crow flies.
        This is a triangular matrix.
        """
        dist = [[0 for k in range(self.nb_points)] for k in range(self.nb_points)]
        for i in range(self.nb_points):
            for j in range(i+1, self.nb_points):
                dist[i][j] = self.points[i].distanceKmTo(self.points[j])
        self.kmDist = dist

    def getGoogleTravelTimes(self, addresses, mode):
        """
        Compute the matrix of time to travel (in seconds) between the points googlemaps 
        in either driving or walking mode.

        doc gmaps

        :param mode: Specifies the mode of transport to use when calculating
            directions. Valid values are "driving", "walking", "transit" or
            "bicycling".
        :type mode: string
        """
        gmaps = googlemaps.Client(key=googlekey)
        length = len(addresses)
        liste_coordonnees = [(addresses[i].getLatitude(),addresses[i].getLongitude()) for i in range(length)]
        distance = gmaps.distance_matrix(liste_coordonnees, liste_coordonnees, mode)
        mat_travel_times = np.zeros((length, length))
        for i in range(length):
            for j in range(length):
                mat_travel_times[i][j] = distance['rows'][i]['elements'][j]['duration']['value']
        return mat_travel_times
        
    # -------------------------------------------------------------------------
     
    # -------------------------------------------------------------------------
    # -- DMIN USING DIVIDE AND CONQUER
    # -------------------------------------------------------------------------
    
    """
    Dmin is computed approximating latitude and longitude as coordinates in a 2D space
    """

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
    
    Dmax is computed approximating latitude and longitude as coordinates in a 2D space
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
        They are computed approximating latitude and longitude as coordinates in a 
        2D space.
        """
        if self.dmin is None or self.dmax is None:
            pmin1, pmin2, _ = Space.computeDmin(self)
            pmax1, pmax2, _ = Space.computeDmax(self)
            self.dmin, self.dmax = pmin1.distanceKmTo(pmin2), pmax1.distanceKmTo(pmax2)
            
            # freeing memory
            self.points_by_long = []
            self.points_by_lat = []
            self.points_lex_sorted = []
            self.upperConvexHull = []
            self.lowerConvexHull = []

    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- PROCESS
    # -------------------------------------------------------------------------
    def setClusterNumber(self, clusterNumber):
        self.clusterNumber = clusterNumber
    
    def computeClusterNumber(self):
        from clusterNumber import numberOfClusters
        numberOfClusters(self)

    def setClusters(self, clusters):
        self.clusters = clusters
    
    def clusterSpace(self):
        from processClustering import runClustering
        runClustering(self)

    def reclusterSpace(self, toRecluster):
        from reclustering import runReclustering
        runReclustering(self, toRecluster)
    
    def getHamiltonianCycle(self, points, starting_point):
        from hamiltonian import hamiltonian
        return hamiltonian(self, points, starting_point)

    def splitAmongNurse(self, centers):
        from splitAmongNurses import vrp
        return vrp(self, centers)
    
    def setDrivingTimes(self,time):
        self.driving_mat = time

    def solve(self, addApp=False):
        """

        """
        if self.dmin is None or self.dmax is None:
            Space.computeExtremalDistances(self)

        # compute distance as the crow flies
        self.computeKmDistance()

        # get the minimal number of clusters
        self.computeClusterNumber()

        del self.kmDist

        # cluster the space
        self.clusterSpace()

        # compute time to see patients in each cluster
        self.clusterTime = dict()
        for c,p in self.clusters.items():
            walking_points = self.getListPointsByID(p)
            walking_path, walking_time = self.getHamiltonianCycle(walking_points, c)
            walking_time += sum(self.care_duration[app_id] for app_id in walking_path)
            self.clusters[c] = walking_path
            self.clusterTime[c] = walking_time

        """
        at this point: 
        => cluster is a dictionnary with:
            - key = center (its index)
            - value = hamiltonian path in the cluster (always starting with the center)
        => clusterTime is a dictionnary with:
            - key = center (its index)
            - value = time to go through the path stored in cluster
        """

        """
        # recluster the patients to avoid having clusters with too important time to process
        toRecluster = []
        print("before reclustering:", len(self.clusters.keys()))
        for c,t in self.clusterTime.items():
            if t >  Space.clustering_factor * self.duration:
                print("center", c, "cluster", self.clusters[c])
                toRecluster.append(c)
        while(len(toRecluster) > 0):   
            self.reclusterSpace(toRecluster)
            toRecluster = []
            for c,t in self.clusterTime.items():
                if t >=  Space.clustering_factor * self.duration:
                    toRecluster.append(c)
        
        print("after reclustering:", len(self.clusters.keys()))
        """

        # split the clusters among the nurses
        centers = list(self.clusters.keys())
        appointment_distribution = self.splitAmongNurse(centers)
        # TODO: mettre en forme la sortie.

        i = 0
        n_id = self.nurse_ids[i]
        officeIndex = centers.index(0)
        res = []

        for [path,_] in appointment_distribution:
            current_time = self.start[0]*3600 + self.start[1] * 60
            previous_index = officeIndex
            for c in range(1, len(path) -1):
                current_pointID = path[c].getID()
                point_index = centers.index(current_pointID)
                current_time += self.driving_mat[previous_index,point_index]
                
                walking_path = self.clusters[current_pointID]
                walking_point = [self.getPointByID(p_id) for p_id in walking_path[:-1]]
                
                try:
                    travel_times = self.getGoogleTravelTimes(walking_point, "walking")
                except:
                    raise GmapApiError
                for k in range(len(walking_path)-2):
                    res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                    current_time += self.care_duration[current_pointID] + travel_times[k,k+1]
                    current_pointID = walking_path[k+1]
                res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                current_time += self.care_duration[current_pointID] + travel_times[len(walking_path)-2,0]
                previous_index = point_index
            current_time += self.driving_mat[previous_index,officeIndex]

            i += 1
            try:
                n_id = self.nurse_ids[i]
            except:
                return False

            if addApp and current_time > self.end[0]*3600 + self.end[1] * 60:
                return False

        if addApp:
            return True

        return res

    def formatTime(self, time):
        h = int(time // 3600)
        time %= 3600
        m = int(time/60.)
        s = str(h) + ":" + str(m)
        return s
 

def solve_complete(data):
    s = Space()
    s.buildSpaceFromDic(data)
    return s.solve()

def solve_boolean(data):
    s = Space()
    s.buildSpaceFromDic(data)
    return s.solve(addApp=True)

if __name__ == "__main__":
    from random import random, seed
    seed(9001)
    lonMin = 2.313721
    lonMax = 2.394590

    latMin = 48.832261
    latMax = 48.892978

    lonRef = lonMin
    lonRange = lonMax - lonMin

    latRef = latMin
    latRange = latMax - latMin

    office = [latRef + random() * latRange, lonRef + random() * lonRange]

    patientDict = dict()
    for k in range(10):
        lon = lonRef + random() * lonRange
        lat = latRef + random() * latRange
        patientDict[k+1] = (lat,lon)

    nurses = [1,2,3,4]
    s = Space()
    s.buildSpaceFromDB(office, patientDict, nurse_ids=nurses) 
    print(s.solve())

