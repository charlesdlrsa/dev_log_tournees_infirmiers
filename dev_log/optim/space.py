# -*- coding: utf-8 -*-

# @author Romain Pascual
# @author Maxime Dieudionne

# @class Space

"""

TODO: 
    remove calls to GmapAPI
    clean le code

ISSUES:
    reclustering -> some solutions are infeasible



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
        self.walkingThreshold = walkingThreshold
        self.points_by_long = []
        self.points_by_lat = []
        self.points_lex_sorted = []
        self.upperConvexHull = []
        self.lowerConvexHull = []
        self.dmin = None
        self.dmax = None

        self.start = None
        self.end = None
        self.duration = None
        self.nurse_ids = None
        self.care_duration = None

        self.clusters = None
        self.hamiltonianPathes = None
        self.clusterTime = None
    
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
        self.nb_points = 1
        self.care_duration = dict()
        self.care_duration[0] = 0
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
    
    def getCareDurationByID(self, p_ID):
        """
        Return the care duration to be done at a given point
        """
        return self.care_duration[p_ID]

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
    
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- BUILD DISTANCE MATRICES
    # -------------------------------------------------------------------------

    def computeKmDistance(self):
        """
        Compute the matrix of distance between the points using distance as the crow flies.
        This is stored as a dictionnary using pointID's as keys
        """
        dist = dict()
        for p1 in self.points:
            for p2 in self.points:
                if p1 != p2 :
                    dist[(p1.getID(),p2.getID())] = p1.distanceKmTo(p2)
                else:
                    dist[(p1.getID(),p2.getID())] = 0
        return dist
    
    def computeGmapDist(self, mode):
        """
        Compute the matrix of distance between two points using googlemaps.
        This is stored as a dictionnary using pointID's as keys
        """
        dist = dict()

        nb_sublist = math.ceil(self.nb_points / 10.)

        for i in range(nb_sublist):
            for j in range(nb_sublist):
                sources = self.points[10*i:10*(i+1)]
                targets = self.points[10*j:10*(j+1)]

                d = self.getGoogleTravelTimes(sources, targets, mode)

                for s in range(len(sources)):
                    for t in range(len(targets)):
                        dist[(sources[s].getID(), targets[t].getID())] = int(d[s][t])

        return dist

    def buildDistanceMatrices(self):
        """
        Build the three distance matrices (as the crow flies, walking and driving)
        """
        self.distKm = self.computeKmDistance()

        print(self.nb_points)
        import time
        a = time.time()
        self.distWalking = self.computeGmapDist(mode="walking")
        self.distDriving = self.computeGmapDist(mode="driving")
        b = time.time()

        print("app Gmap API:", b-a)

    def getGoogleTravelTimes(self, sources, targets, mode):
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
        n_sources = len(sources)
        n_targets = len(targets)
        coordonnees_sources = [(p.getLatitude(), p.getLongitude()) for p in sources]
        coordonnees_targets = [(p.getLatitude(), p.getLongitude()) for p in targets]
        distance = gmaps.distance_matrix(coordonnees_sources, coordonnees_targets, mode)
        mat_travel_times = np.zeros((n_sources, n_targets))
        for i in range(n_sources):
            for j in range(n_targets):
                mat_travel_times[i][j] = distance['rows'][i]['elements'][j]['duration']['value']
        return mat_travel_times

    def getDistKM(self):
        """
        Return the matrix of distances as the crow flies
        """
        return self.distKm

    def getDistKMSource2Target(self, sourceID, targetID):
        """
        Return the distance as the crow flies between two points given by their ID
        """
        return self.distKm[(sourceID, targetID)]
    
    def getDistWalking(self):
        """
        Return the matrix of walking distance
        """
        return self.distWalking
    
    def getDistWalkingSource2Target(self, sourceID, targetID):
        """
        Return the walking distance between two points given by their ID
        """
        return self.distWalking[(sourceID, targetID)]

    def getDistDriving(self):
        """
        Return the matrix of driving distance
        """
        return self.distDriving

    def getDistDrivingSource2Target(self, sourceID, targetID):
        """
        Return the driving distance between two points given by their ID
        """
        return self.distDriving[(sourceID, targetID)]
    
    def getDist(self, mode):
        """
        Return either the matrix of walking distance or the matrix of driving
        distance, depending on the mode given.
        """
        if mode == "walking":
            return self.getDistWalking()
        elif mode == "driving":
            return self.getDistDriving()
    
    def getDistSource2Target(self, sourceID, targetID, mode):
        """
        Return either the walking distance or the driving distance between two
        points given by their ID, depending on the mode given.
        """
        if mode == "walking":
            return self.getDistWalkingSource2Target(sourceID, targetID)
        elif mode == "driving":
            return self.getDistDrivingSource2Target(sourceID, targetID)

        
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
    def setClusters(self, clusters):
        """
        self.cluster is a dictionnary.
            - key: pointID if the cluster center
            - value: list of pointID's belonging to the cluster
        """
        self.clusters = clusters
    
    def clusterSpace(self):
        from processClustering import runClustering
        runClustering(self)

    def reclusterSpace(self, toRecluster):
        from reclustering import runReclustering
        runReclustering(self, toRecluster)
    
    def getHamiltonianCycle(self, pointIDs, starting_pointID, mode="walking"):
        from hamiltonian import hamiltonian
        return hamiltonian(self, pointIDs, starting_pointID, mode)

    def splitAmongNurse(self, centers):
        from splitAmongNurses import vrp
        return vrp(self, centers)

    def solve(self, mode="schedule"):
        """

        """
        if self.dmin is None or self.dmax is None:
            Space.computeExtremalDistances(self)
        
        print("1")

        # compute distance matrices
        self.buildDistanceMatrices()


        print("2")

        # get the minimal number of clusters
        #self.computeClusterNumber()

        # cluster the space
        self.clusterSpace()


        print("3")

        # compute time to see patients in each cluster
        self.clusterTime = dict()
        self.hamiltonianPathes = dict()
        for c, walking_points in self.clusters.items():
            # c and walking_points are pointID's
            walking_path, walking_time = self.getHamiltonianCycle(walking_points, c)
            walking_time += sum(self.care_duration[app_id] for app_id in walking_path)
            self.hamiltonianPathes[c] = walking_path
            self.clusterTime[c] = walking_time

        print(4)
        exit()

        """
        at this point: 
        => cluster is a dictionnary with:
            - key = center (its index)
            - value = list of pointID's belonging to the cluster
        => hamiltonianPathes is a dictionnary with:
            - key = center (its index)
            - value = hamiltonian path in the cluster (always starting with the center)
        => clusterTime is a dictionnary with:
            - key = center (its index)
            - value = time to go through the path stored in hamiltonianPathes
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

        i = 0
        officeIndex = centers.index(0)
        res = []
        path_index = 0
        isOfficeDone = False

        for [path,_] in appointment_distribution:
            print("***")
            print([p.getID() for p in path])
            try:
                n_id = self.nurse_ids[i]
            except:
                return False
            current_time = self.start[0]*3600 + self.start[1] * 60
            previous_index = officeIndex
            for c in range(1, len(path) -1):
                current_point = path[c]
                current_pointID = current_point.getID()
                point_index = centers.index(current_pointID)
                current_time += self.driving_mat[previous_index,point_index]
                if mode == "path":
                    source = path[c-1]
                    order = str(path_index)
                    s_lat = str(source.getLatitude())
                    s_lon = str(source.getLongitude())
                    t_lat = str(current_point.getLatitude())
                    t_lon = str(current_point.getLongitude())
                    res.append({"order": order, "s_lat": s_lat, "s_lon": s_lon, "t_lat": t_lat, "t_lon": t_lon,"mode": "driving"})
                    path_index += 1
                
                walking_path = self.clusters[current_pointID]
                if len(walking_path) > 1:
                    walking_point = [self.getPointByID(p_id) for p_id in walking_path[:-1]]
                    try:
                        travel_times = self.getGoogleTravelTimes(walking_point, "walking")
                    except:
                        raise GmapApiError
                    for k in range(len(walking_path)-2):
                        next_pointID = walking_path[k+1]
                        next_point = self.getPointByID(next_pointID)
                        if mode == "schedule":
                            res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                        elif mode == "path":
                            order = str(path_index)
                            s_lat = str(current_point.getLatitude())
                            s_lon = str(current_point.getLongitude())
                            t_lat = str(next_point.getLatitude())
                            t_lon = str(next_point.getLongitude())
                            res.append({"order": order, "s_lat": s_lat, "s_lon": s_lon, "t_lat": t_lat, "t_lon": t_lon, "mode": "walking"})
                            path_index += 1
                        current_time += self.care_duration[current_pointID] + travel_times[k,k+1]
                        current_pointID = next_pointID
                        current_point = next_point
                    if mode == "schedule":
                        res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                    elif mode == "path":
                            order = str(path_index)
                            s_lat = str(current_point.getLatitude())
                            s_lon = str(current_point.getLongitude())
                            t_lat = str(path[c].getLatitude())
                            t_lon = str(path[c].getLongitude())
                            res.append({"order": order, "s_lat": s_lat, "s_lon": s_lon, "t_lat": t_lat, "t_lon": t_lon, "mode": "walking"})
                            path_index += 1
                    current_time += self.care_duration[current_pointID] + travel_times[len(walking_path)-2,0]
                else:
                    if mode == "schedule":
                        res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                    current_time += self.care_duration[current_pointID]
                previous_index = point_index
            current_time += self.driving_mat[previous_index,officeIndex]

            if mode=="addAppointment" and current_time > self.end[0] * 3600 + self.end[1] * 60:
                return False

            # try and affect office cluster
            if not isOfficeDone:
                walking_path = self.clusters[0]
                if len(walking_path) < 2:
                    isOfficeDone = True
                elif current_time + self.clusterTime[0] < self.end[0] * 3600 + self.end[1] * 60:
                    # add office cluster
                    walking_point = [self.getPointByID(p_id) for p_id in walking_path[:-1]]
                    try:
                        travel_times = self.getGoogleTravelTimes(walking_point, "walking")
                    except:
                        raise GmapApiError
                    current_pointID = walking_path[1]
                    current_point = self.getPointByID(current_pointID)
                    for k in range(1,len(walking_path)-2):
                        next_pointID = walking_path[k+1]
                        next_point = self.getPointByID(next_pointID)
                        if mode == "schedule":
                            res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                        elif mode == "path":
                            order = str(path_index)
                            s_lat = str(current_point.getLatitude())
                            s_lon = str(current_point.getLongitude())
                            t_lat = str(next_point.getLatitude())
                            t_lon = str(next_point.getLongitude())
                            res.append({"order": order, "s_lat": s_lat, "s_lon": s_lon, "t_lat": t_lat, "t_lon": t_lon, "mode": "walking"})
                            path_index += 1
                        current_time += self.care_duration[current_pointID] + travel_times[k,k+1]
                        current_pointID = next_pointID
                        current_point = next_point
                    if mode == "schedule":
                        res.append({"nurse_id":str(n_id), "app_id":str(current_pointID), "hour":self.formatTime(current_time)})
                    elif mode == "path":
                            order = str(path_index)
                            s_lat = str(current_point.getLatitude())
                            s_lon = str(current_point.getLongitude())
                            t_lat = str(path[c].getLatitude())
                            t_lon = str(path[c].getLongitude())
                            res.append({"order": order, "s_lat": s_lat, "s_lon": s_lon, "t_lat": t_lat, "t_lon": t_lon, "mode": "walking"})
                            path_index += 1
                    current_time += self.care_duration[current_pointID] + travel_times[len(walking_path)-2,0]
                    isOfficeDone = True
          
            i += 1
        if mode=="addAppointment":
            return isOfficeDone

        #print(self.clusters)
        return res

    def formatTime(self, time, ft=1):
        t = int(time)
        s = "%s%d.%s%d"%("0" if t // 3600 < 10 else "", t // 3600, "0" if (t % 3600)//60 < 10 else "", (t % 3600)//60)
        return s
        

def solve_complete(data):
    s = Space()
    s.buildSpaceFromDic(data)
    return s.solve(mode="schedule")


def solve_boolean(data):
    s = Space()
    s.buildSpaceFromDic(data)
    return s.solve(mode="addAppointment")

def solve_path(data):
    s = Space()
    s.buildSpaceFromDic(data)
    return s.solve(mode="path")

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

    test_dict = {'nurse_id': ['2', '1'], 'office_lat': '48.7263802', 'office_lon': '2.2643467', 'start': '08:00', 'end': '12:00', 'appointments': [{'app_id': '6', 'app_lat': '48.73590189999999', 'app_lon': '2.2591394', 'app_length': '30'},{'app_id': '16', 'app_lat': '48.6559099', 'app_lon': '2.23327', 'app_length': '15'}, {'app_id': '7', 'app_lat': '48.7317076', 'app_lon': '2.2807308', 'app_length': '35'}, {'app_id': '8', 'app_lat': '48.7400286', 'app_lon': '2.3156139', 'app_length': '20'}, {'app_id': '9', 'app_lat': '48.6961912', 'app_lon': '2.2900446', 'app_length': '30'}, {'app_id': '10', 'app_lat': '48.7086557', 'app_lon': '2.241912', 'app_length': '35'}, {'app_id': '11', 'app_lat': '48.7450455', 'app_lon': '2.2664304', 'app_length': '35'}, {'app_id': '12', 'app_lat': '48.6964354', 'app_lon': '2.2691329', 'app_length': '25'}, {'app_id': '13', 'app_lat': '48.7382421', 'app_lon': '2.2176977', 'app_length': '35'}, {'app_id': '14', 'app_lat': '48.7973917', 'app_lon': '2.3484036', 'app_length': '35'}]}
    s = Space()
    #s.buildSpaceFromDB(office, patientDict, nurse_ids=nurses)
    s.buildSpaceFromDic(test_dict)
    
    res = s.solve()
    nurses = dict()
    for app in res:
        try :
            nurses[app['nurse_id']].append(app['app_id'])
        except:
            nurses[app['nurse_id']] = [app['app_id']]
    #print(nurses)
    