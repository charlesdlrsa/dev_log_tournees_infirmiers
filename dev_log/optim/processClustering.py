from space import Space
from amplpy import AMPL, Environment


def runClustering(s):
    """
    Cluster the space, using a weighted k-median paradigm.
    The goal is to minimize k.

    The office is set to be a center by default. 
    NB: The office id has to be set to 0.

    @return: a dict representing the clusters

    The dictionnary representing the cluster has the format:
        - key = center
        - value = list of the points in the cluster (always starting with the center)

    """
    threshold = min(s.walkingThreshold, (s.dmax+s.dmin)/2.0)
    with open("models/maxFootTimeClustering.dat", "w") as clustering:
        clustering.write("# threshold for cluster size\n")
        clustering.write("param maxClusterSize:= {};\n".format(12000))
        
        clustering.write("\n")

        clustering.write("# threshold for walking time\n")
        clustering.write("param maxWalkingTime:= {};\n".format(3600))
        
        clustering.write("\n")
        
        clustering.write("# nombre de sommets {}\n".format(s.nb_points))
        clustering.write("param: V: duration :=\n")
        for p in s.points:
            p_ID = p.getID()
            p_duration = s.getCareDurationByID(p_ID)
            clustering.write("\t{} {}\n".format(p_ID, p_duration))
        clustering.write(";\n")

        clustering.write("\n")

        clustering.write("# id_sommet1, id_sommet2, drivingTime\n")
        clustering.write("param: A: drivingTime :=\n")
        for p1 in s.points:
            for p2 in s.points:
                if p1 == p2:
                    p_ID = p1.getID()
                    clustering.write("\t{} {} 0\n".format(p_ID, p_ID))
                else:
                    p_ID1 = p1.getID()
                    p_ID2 = p2.getID()
                    clustering.write("\t{} {} {}\n".format(p_ID1, p_ID2, s.distDriving[(p_ID1,p_ID2)]))
        clustering.write(";\n")
        
        clustering.write("# id_sommet1, id_sommet2, walkingTime\n")
        clustering.write("param: walkingTime :=\n")
        for p1 in s.points:
            for p2 in s.points:
                if p1 == p2:
                    p_ID = p1.getID()
                    clustering.write("\t{} {} 0\n".format(p_ID, p_ID))
                else:
                    p_ID1 = p1.getID()
                    p_ID2 = p2.getID()
                    clustering.write("\t{} {} {}\n".format(p_ID1, p_ID2, s.distWalking[(p_ID1,p_ID2)]))
        clustering.write(";\n")
    
    # set up ampl
    ampl = AMPL(Environment('ampl/linux'))

    # Interpret the two files
    ampl.read('models/maxFootTimeClustering.mod')
    ampl.readData('models/maxFootTimeClustering.dat')

    # Solve
    print("cluster space")
    ampl.solve()

    # Get objective entity by AMPL name
    centers = ampl.getVariable('center')
    
    listCenters = []

    # Access all instances using an iterator
    for index, instance in centers:
        if instance.value():
            # int(index) is the point_ID of a center
            listCenters.append(int(index))

    clusters = dict()
    for c in listCenters:
        clusters[c] = [c]

    # access the variable
    closestCenter = ampl.getVariable('closestCenter')
    for index, instance in closestCenter:
        if int(index[0]) not in listCenters and instance.value():
            clusters[int(index[1])].append(int(index[0]))

    print(clusters)
    s.setClusters(clusters)