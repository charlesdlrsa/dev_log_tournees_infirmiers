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

            # get indexes to recluster
            cluster = self.clusters.pop(c)[:-1]

            # get points to recluster
            unclusteredPoints = self.getListPointsByID(cluster)
            n = len(unclusteredPoints)

            # get travel times with Gmaps
            try:
                time = self.getGoogleTravelTimes(unclusteredPoints, "walking")
            except:
                raise GmapApiError

            # get cluster number
            k = self.getNumberOfCluster(time, )
            math.ceil(ctime / (self.duration * Space.clustering_factor))

            # gmaps walking time is approximately 4.8km/hr and 3600/4.8 = 
            d_threshold = min(self.walkingThreshold, (self.dmax+self.dmin)/2.0)
            threshold = int(d_threshold*750)

            with open("dev_log/optim/models/clusteringWithVertexValues.dat", "w") as clustering:
                clustering.write("# threshold for walking distance\n")
                clustering.write("param t:= {};\n".format(threshold))
                
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
            ampl = AMPL(Environment('dev_log/optim/ampl'))

            # Interpret the two files
            ampl.read('dev_log/optim/models/clusteringWithVertexValues.mod')
            ampl.readData('dev_log/optim/models/clusteringWithVertexValues.dat')

            # Solve
            print("reclustering")
            ampl.solve()

            # Get objective entity by AMPL name
            centers = ampl.getVariable('center')
            
            listCenters = []
            if sum(b.value() for (_,b) in centers) < 2:
                quit()
            print("***")


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
                print("cc:", cc)
                walking_points = self.getListPointsByID(clusters[cc])
                walking_path, walking_time = self.getHamiltonianCycle(walking_points, cc)
                walking_time += sum(self.care_duration[app_id] for app_id in walking_path)
                self.clusters[cc] = walking_path
                self.clusterTime[cc] = walking_time
            
        print("done")