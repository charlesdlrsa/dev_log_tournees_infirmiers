# -*- coding: utf-8 -*-

# @author Romain Pascual

# @class ClusteringInstance

from point import Point
import matplotlib.pyplot as plt
import random

class ClusteringInstance:
    """
    One instance of clusters for a given threshold.
    
    Attributes:
        thold: the maximal allowed size of a cluster (radius).
        k: the maximum number of allowed centers.
        S: the set of centers
        C: the list of clusters
        U: the set of unclustered points
    """

    # -------------------------------------------------------------------------
    # -- INITIALIZATION
    # -------------------------------------------------------------------------
    
    def __init__(self,thold,k):
        self.thold = thold
        self.k = k
        self.rmax = 0
        
        self.S = set()   # centers such that for every x != y d(x,y) > 2thold 
        self.C = []      # clusters corresponding to the previous centers
        self.U = set()   # set of unclustered points such that for all x in U, for all c in S d(c,x)>2thold
    
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- AUX FUNCTIONS 
    # -------------------------------------------------------------------------

    def get_cluster_index(self,p):
        """
        Give the index in C of the cluster containing p.
            -> Runs in O(k).
        """
        for i in range(len(self.C)):
            if p in self.C[i]:
                return i

    def getR(self,center):
        """
        Compute the radius of a given cluster.
        """
        for c in self.C:
            if center in c:
                r = 0
                for p in c:
                    d = p.distanceTo(center)
                    if d > r:
                        r = d
                return r
    
    def getRmax(self):
        """
        Return the maximum radius in the instance, throughout the all execution.
        """
        return self.rmax
    
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- CLUSTERING PROCESS 
    # -------------------------------------------------------------------------
        
    def insertion(self,x):
        """
        Add a new point. Try to affect it to some already existing cluster, then
        try to build a new cluster from it and finally add it to the set of 
        unclustered points.
            -> Runs in O(k).
        """
        for c in self.S:
            d = c.distanceTo(x)
            if  d <= 2 * self.thold:
                i = self.get_cluster_index(c)
                self.C[i].add(x)
                if d > self.rmax:
                    self.rmax = d
                return
        if len(self.C) < self.k:
            self.S.add(x)
            cluster = set()
            cluster.add(x)
            self.C.append(cluster)
        else:
            self.U.add(x)
            
    def deletion(self,x):
        """
        Delete a point. 
        If it is unclustered or not a center, simply removes it.
            -> Runs in O(1).
        Else, randomly recluster a part of the points. Note that a try is added to
        add the removed points to the kept clusters as clusters may overlap.
            -> Runs in O(nk) where n is the number of points
        """
        if x in self.U:
            self.U.remove(x)
        elif x not in self.S:
            try:
                self.C[self.get_cluster_index(x)].remove(x)
            except TypeError: # self.get_center(x) return None if x in not a valid point
                # print ("The following point has already been removed : {}".format(x))
                pass
        else: # x is a center
            i = self.get_cluster_index(x)
            self._X = set()
            for cluster in self.C[i:]:
                self._X.update(cluster)
            self.S.difference_update(self._X)
            self.C = self.C[:i]
            self._X.remove(x)
            
            self.tryWithCurrentCenters()
            self._X.update(self.U)
            
            _S, _C = ClusteringInstance.randRecluster(self,self.k-i)
                        
            self.S.update(_S)
            self.C += _C
            self.U = self._X
            del(self._X)
    
    def tryWithCurrentCenters(self):
        """
        Some points in the removed clusters may be within distance <= 2thold from another center
        """
        added = set()        
        for x in self._X:
            for c in self.S:
                d = c.distanceTo(x)
                if  d <= 2 * self.thold:
                    i = self.get_cluster_index(c)
                    self.C[i].add(x)
                    added.add(x)
                    if d > self.rmax:
                        self.rmax = d
                    break
        self._X.difference_update(added)
    
    def randRecluster(self,k):
        """
        Randomly recluster the points.
        """
        S = set()
        C = []
        kappa = 0
        while len(self._X) > 0 and kappa < k:
            kappa += 1
            c = random.sample(self._X,1)[0]
            self._X.remove(c)
            S.add(c)
            cluster = set()
            cluster.add(c)
            for x in self._X:
                d = c.distanceTo(x)
                if d <= 2 * self.thold:
                    cluster.add(x)
                    if d > self.rmax:
                        self.rmax = d
            self._X.difference_update(cluster)
            C.append(cluster)
        return S,C
    
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # -- OUTPUTS 
    # -------------------------------------------------------------------------
    
    def plot(self, file_name):
        """
        Plot the instance
        """
        colors = []
        for k in range(7):
            colors.append(((6-k)/6,k/6,0))
            colors.append(((6-k)/6,0,k/6))
            colors.append((0,(6-k)/6,k/6))
        k = 0
        for c in self.C:
            x = [p.longitude for p in c]
            y = [p.latitude for p in c]
            plt.scatter(x,y, s =5, c=colors[k])
            k +=1
        x = [p.longitude for p in self.U]
        y = [p.latitude for p in self.U]
        plt.scatter(x,y, s=5, c = (0,0,0))
        for center in self.S:
            r = self.getR(center)
            circle = plt.Circle((center.longitude, center.latitude), r, linewidth = 1, color = (0,0,0), fill = False)
            plt.gca().add_artist(circle)
        plt.savefig(file_name, dpi = 300)
        plt.show()
    
    def path(self,center):
        """
        Compute the path of a given cluster.
        It is an hamiltonian path starting at the center of the cluster
        """
        for c in self.C:
            if center in c:
                pass
"""
TODO:
    - hamiltonian cycle in a cluster
    - hamiltonian cycle on the centers
    - find the appropriate cluster instance in "space"
    