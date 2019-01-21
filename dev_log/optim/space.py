# -*- coding: utf-8 -*-

# @author Romain Pascual
# @author Maxime Dieudionne

# @class Space

"""

TODO: 
    assignNurse
    solve
    LP pour split les nurses
    mettre en forme les sorties
    functions solve_boolean(data) and solve_complete(data)
    GoogleMaps gestion des exceptions
    clean le code


function naming:
solve_boolean(data)
solve_complete(data)

ISSUE : if we have one big cluster that a nurse can not cover by him(her)self. -> done

Output:
[{"nurse_id":"id", "app_id":"id", "hour":"hh:mm"}]


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

    def getPointsByID(self, id):
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

    def regenerateCyclingPath(self, listPoints, amplMatPath, travel_times):
        """
        Given a list of points and the ampl transition matrix, rebuild the path.
        @param listPoints: list of points (id, lat, lon) such that its order is the same as
        the index in amplMatPath
        @param amplMatPath: transition matrix (returned by ampl) describing the path 
        (zero, one matrix) such that:
            amplMatPath[i,j] = 1 iff the path goes from listPoint[i] to listPoint[j]
        """

        n = len(listPoints)
        i = 0
        j = -1
        path = [listPoints[i]]
        travel_time = 0
        while j != 0:
            for k in range(n):
                if i != k and amplMatPath[i+1,k+1].value():
                    j = k
            travel_time += travel_times[i][j]
            i = j
            path.append(listPoints[i])
        return path, travel_time
        
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
    
    def getKmDistance(self):
        """
        Compute the matrix of distance between the points using distance as the crow flies.
        """
        dist = [[0 for k in range(self.nb_points)] for k in range(self.nb_points)]
        for i in range(self.nb_points):
            for j in range(i+1, self.nb_points):
                dist[i][j] = self.points[i].distanceKmTo(self.points[j])
        return dist

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
            _, _, dmin = Space.computeDmin(self)
            _, _, dmax = Space.computeDmax(self)
            self.dmin, self.dmax = math.sqrt(dmin), math.sqrt(dmax)
            
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
    def getNumberOfCluster(self):
        """
        Compute the minimum number of cluster having a radius bounded by
        walkingThreshold, which is a distance in kilometers (=2.0 by default)

        The office is set to be a center by default. 
        NB: The office id has to be set to 0.

        @return: the minimal number of clusters
        """
        # dist is a triangular matrix
        dist = self.getKmDistance()
        with open("models/clustering.dat", "w") as clustering:
            clustering.write("# threshold for walking distance\n")
            clustering.write("param d:= {};\n".format(self.walkingThreshold))
            
            clustering.write("\n")
            
            clustering.write("# nombre de sommets {}\n".format(self.nb_points))
            clustering.write("set V :=\n")
            for p in self.points:
                clustering.write("\t{}\n".format(p.getID()))
            clustering.write(";\n")

            clustering.write("\n")

            clustering.write("# id_sommet1, id_sommet2, distance\n")
            clustering.write("param distance :=\n")
            for p in self.points:
                p_ID = p.getID()
                clustering.write("\t{} {} 0\n".format(p_ID, p_ID))
            for i in range(self.nb_points):
                for j in range(i+1, self.nb_points):
                    p_ID1 = self.points[i].getID()
                    p_ID2 = self.points[j].getID()
                    clustering.write("\t{} {} {:.4f}\n".format(p_ID1, p_ID2, dist[i][j]))
                    clustering.write("\t{} {} {:.4f}\n".format(p_ID2, p_ID1, dist[i][j]))
            clustering.write(";\n")

        # set up ampl
        ampl = AMPL(Environment('ampl'))

        # Interpret the two files
        ampl.read('models/clustering.mod')
        ampl.readData('models/clustering.dat')

        # Solve
        ampl.solve()

        # Get objective entity by AMPL name
        numberCenters = ampl.getObjective('numberCenters')
        
        self.clusterNumber = numberCenters.get().value()

    def clusterSpace(self):
        """
        Cluster the space, using the k-median paradigm:
            provide the set of $k$ vertices ${c_1, ... c_k}$ minimizing
                sum_{v in V} min_i d_{c_i,v}
        
        k is stored in self.clusterNumber

        The office is set to be a center by default. 
        NB: The office id has to be set to 0.

        @store  a dict representing the clusters in self.clusters.

        The dictionnary representing the cluster has the format:
            - key = center
            - value = list of the points in the cluster (always starting with the center)
        """
        with open("models/clustering.dat", "r") as clustering:
            with open("models/kmedian.dat", "w") as kmedian:
                kmedian.write("# number of clusters\n")
                kmedian.write("param k := {};\n".format(self.clusterNumber))

                kmedian.write("\n")

                clustering.readline()
                clustering.readline()
                clustering.readline()

                for line in clustering.readlines():
                    kmedian.write(line)

        # set up ampl
        ampl = AMPL(Environment('ampl'))

        # Interpret the two files
        ampl.read('models/kmedian.mod')
        ampl.readData('models/kmedian.dat')

        # Solve
        ampl.solve()

        # Get objective entity by AMPL name
        centers = ampl.getVariable('center')
        
        listCenters = []

        # Access all instances using an iterator
        for index, instance in centers:
            if instance.value():
                listCenters.append(int(index))

        clusters = dict()
        for c in listCenters:
            clusters[c] = [c]

        # access the variable
        closestCenter = ampl.getVariable('closestCenter')
        for index, instance in closestCenter:
            if int(index[0]) not in listCenters and instance.value():
                clusters[int(index[1])].append(int(index[0]))

        self.clusters = clusters

    def recluster(self, toRecluster):
        """
        Recluster some clusters that are "too big".
        Namely, all clusters having a traveling time greater or equal to half the working time.

        This is used to prevent huge cluster that would be done by only one nurse. The half factor
        is used to soften the optimization.

        NB: The function assume the points have already been clustered and some clusters are "too big".
            The linear solver will fail to recluster a set of points not satisfying the cluster
            constraints.

        @param toRecluster: list of "too big" cluster centers
        """
        for c in toRecluster:
            unclusteredPoints = self.getListPointsByID(self.clusters.pop(c)[:-1])
            n = len(unclusteredPoints)
            time = self.getGoogleTravelTimes(unclusteredPoints, "walking")
            ctime = self.clusterTime.pop(c)
            k = math.ceil(0.5 * self.duration / ctime)

            with open("models/clusteringWithVertexValues.dat", "w") as clustering:
                clustering.write("# threshold for walking distance\n")
                # gmaps walking time is approximately 4.8km/hr and 3600/4.8 = 750
                clustering.write("param t:= {};\n".format(int(self.walkingThreshold*750)))
                
                clustering.write("\n")

                clustering.write("# number of clusters\n")
                clustering.write("param k := {};\n".format(k))

                clustering.write("\n")

                clustering.write("# max cluster size\n")
                clustering.write("param maxt := {};\n".format(math.floor(0.5 * self.duration)))

                clustering.write("\n")

                
                clustering.write("# nombre de sommets {}\n".format(n))
                clustering.write("param: V: duration :=\n")
                for p in unclusteredPoints:
                    p_ID = p.getID()
                    clustering.write("\t{} {}\n".format(p_ID,self.care_duration[p_ID]))
                clustering.write(";\n")

                clustering.write("\n")

                clustering.write("# id_sommet1, id_sommet2, time\n")
                clustering.write("param: A: time :=\n")
                for p in unclusteredPoints:
                    p_ID = p.getID()
                    clustering.write("\t{} {} 0\n".format(p_ID, p_ID))
                for i in range(n):
                    for j in range(i+1, n):
                        p_ID1 = unclusteredPoints[i].getID()
                        p_ID2 = unclusteredPoints[j].getID()
                        clustering.write("\t{} {} {}\n".format(p_ID1, p_ID2, int(time[i][j])))
                        clustering.write("\t{} {} {}\n".format(p_ID2, p_ID1, int(time[j][i])))
                clustering.write(";\n")

            # set up ampl
            ampl = AMPL(Environment('ampl'))

            # Interpret the two files
            ampl.read('models/clusteringWithVertexValues.mod')
            ampl.readData('models/clusteringWithVertexValues.dat')

            # Solve
            ampl.solve()

            # Get objective entity by AMPL name
            centers = ampl.getVariable('center')
            
            listCenters = []

            # Access all instances using an iterator
            for index, instance in centers:
                if instance.value():
                    listCenters.append(int(index))

            clusters = dict()
            for c in listCenters:
                clusters[c] = [c]

            # access the variable
            closestCenter = ampl.getVariable('closestCenter')
            for index, instance in closestCenter:
                if int(index[0]) not in listCenters and instance.value():
                    clusters[int(index[1])].append(int(index[0]))

            # update self.cluster and self.clusterTime 
            for cc in listCenters:
                walking_points = self.getListPointsByID(clusters[cc])
                walking_path, walking_time = self.getHamiltonianCycle(walking_points, mode="walking")
                walking_time += sum(self.care_duration[app_id] for app_id in walking_path)
                self.clusters[cc] = walking_path
                self.clusterTime[cc] = walking_time
            
        print("done")
    
    def getHamiltonianCycle(self, points, mode="driving", recompute=True):
        """
        Compute an hamiltonian cycle on the set of points.

        It uses a google maps key. Note that mode should be one of
            -"driving", 
            -"walking", 
            - (and "bicycling" but it is not taken into account at the moment)
        
        @param points: should be a subset of self.points
        """
        if recompute:

            n = len(points)

            if n == 1:
                path, travel_time = points, 0
            
            else:
                travel_times = self.getGoogleTravelTimes(points, mode)
            
                if n == 2:
                    path, travel_time = [points[0], points[1], points[0]], travel_times[0][1] + travel_times[1][0]

                else:
                    """
                    For the solver to work, the points has to be numbered from 1 to n
                    """

                    with open("models/travellingSalesman.dat", "w") as hamiltonian:
                        hamiltonian.write("# nombre de sommets {}\n".format(n))
                        hamiltonian.write("set V :=\n")
                        for k in range(1, n+1):
                            hamiltonian.write("\t{}\n".format(k))
                        hamiltonian.write(";\n")

                        hamiltonian.write("\n")

                        hamiltonian.write("# id_sommet1, id_sommet2, travelling time\n")
                        hamiltonian.write("param: A: time :=\n")
                        for i in range(n):
                            for j in range(i+1, n):
                                hamiltonian.write("\t{} {} {}\n".format(i+1, j+1, travel_times[i][j]))
                                hamiltonian.write("\t{} {} {}\n".format(j+1, i+1, travel_times[j][i]))
                        hamiltonian.write(";\n")

                    # set up ampl
                    ampl = AMPL(Environment('ampl'))

                    # Interpret the two files
                    ampl.read('models/travellingSalesman.mod')
                    ampl.readData('models/travellingSalesman.dat')

                    # Solve
                    ampl.solve()
                    
                    #regenerate the path
                    x = ampl.getVariable("x")

                    path, travel_time = self.regenerateCyclingPath(points, x, travel_times)
            return [p.getID() for p in path], travel_time
    

        else:

            # set up ampl
            ampl = AMPL(Environment('ampl'))
            
            #model4
            btm4 = time.time()

            # Interpret the two files
            ampl.read('models/travellingSalesman.mod')
            ampl.readData('models/travellingSalesman.dat')

            # Solve
            ampl.solve()

            # Get objective entity by AMPL name
            total_time_m4 = ampl.getObjective("total_time").value()
            
            etm4 = time.time()

            print("travellingSalesman - score: {}, time {}.".format(total_time_m4, etm4 - btm4))

            #regenerate the path
            x = ampl.getVariable("x")

            travel_times = []
            with open("times.txt", "r") as times:
                for line in times.readlines():
                    t = []
                    l = re.findall('[0-9]*',line)
                    for c in l:
                        try:
                            t.append(int(c))
                        except ValueError:
                            pass
                    travel_times.append(t)

            path, travel_time = self.regenerateCyclingPath(points, x, travel_times)
            return [p.getID() for p in path], travel_time

    def splitAmongNurse(self):
        """
        Split the clusters between the various nurses.
        """

        
        with open("models/vrp.dat", "w") as vrp:
            
            # TODO: Write data
            # TODO: Write LP

            vrp.write(";\n")

        # set up ampl
        ampl = AMPL(Environment('ampl'))

        # Interpret the two files
        ampl.read('models/vrp.mod')
        ampl.readData('models/vrp.dat')

        # Solve
        ampl.solve()

        # Get objective entity by AMPL name
        return None


    def solve(self):
        """

        """
        self.getNumberOfCluster()
        self.clusterSpace()
        self.clusterTime = dict()

        for c,p in self.clusters.items():
            walking_points = self.getListPointsByID(p)
            walking_path, walking_time = self.getHamiltonianCycle(walking_points, mode="walking")
            walking_time += sum(self.care_duration[app_id] for app_id in walking_path)
            self.clusters[c] = walking_path
            self.clusterTime[c] = walking_time

        """
        at this point: 
        => cluster is a dictionnary with:
            - key = center (its index)
            - value = hamiltonian path in the cluster (always starting with the center)
        => cluster_time is a dictionnary with:
            - key = center (its index)
            - value = time to go through the path stored in cluster
        """

        toRecluster = []
        for c,t in self.clusterTime.items():
            if t >=  0.5 * self.duration:
                toRecluster.append(c)
        while(len(toRecluster) > 0):   
            self.recluster(toRecluster)
            toRecluster = []
            for c,t in self.clusterTime.items():
                if t >=  0.5 * self.duration:
                    toRecluster.append(c)

        #appointment_distribution = self.splitAmongNurse()

        # TODO: mettre en forme la sortie.

        return None



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
    for k in range(5):
        lon = lonRef + random() * lonRange
        lat = latRef + random() * latRange
        patientDict[k+1] = (lat,lon)

    s = Space()
    s.buildSpaceFromDB(office, patientDict)
    s.clusters = dict()
    s.clusterTime = dict()
    path, time = s.getHamiltonianCycle(s.points,"walking")
    s.clusters[0] = path
    s.clusterTime[0] = time//4
    s.recluster([0])
    quit()
    s.getNumberOfCluster()
    points = s.getListPointsByID(s.clusters.keys())
    driving_path, driving_time = s.getHamiltonianCycle(points)

    global_path = []
    total_time = driving_time

    for index_center in driving_path[:-1]:
        walking_points = s.getListPointsByID(s.clusters[index_center])
        walking_path, walking_time = s.getHamiltonianCycle(walking_points, mode="walking")
        global_path += walking_path
        total_time += walking_time
    global_path.append(driving_path[-1])

    print(total_time)

