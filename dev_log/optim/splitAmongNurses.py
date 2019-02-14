from dev_log.optim.space import Space, GmapApiError
from amplpy import AMPL, Environment

"""
Need
    - space.getListPointsByID
    - space.nurse_ids
    - space.getGoogleTravelTimes
    - space.duration
    - space.clusterTime
    - space.buildVRPSolution
"""

def vrp(s, centers):
    """
    Split the clusters between the various nurses.
    """
    centers = s.getListPointsByID(centers)
    n = len(centers)
    k = min(len(s.nurse_ids), n-1)
    if k < 1:
        k = 1
    try:
        time = s.getGoogleTravelTimes(centers, "driving")
        s.setDrivingTimes(time)
    except:
        raise GmapApiError
    
    with open("dev_log/optim/models/vrp.dat", "w") as vrp:
        # number of nurses
        vrp.write("# number of clusters\n")
        vrp.write("param k := {};\n".format(k))

        vrp.write("\n")
        
        # TODO: adapt according to nurses
        vrp.write("# max cluster size\n")
        vrp.write("param maxt := {};\n".format(s.duration))

        vrp.write("\n")

        vrp.write("# nombre de sommets {}\n".format(n))
        vrp.write("param: V: duration :=\n")
        for k in range(n):
            p_ID = centers[k].getID()
            vrp.write("\t{} {}\n".format(k+1,s.clusterTime[p_ID]))
        vrp.write(";\n")

        vrp.write("\n")

        vrp.write("# id_sommet1, id_sommet2, time\n")
        vrp.write("param: A: time :=\n")
        for i in range(n):
            for j in range(i+1, n):
                vrp.write("\t{} {} {}\n".format(i+1, j+1, int(time[i][j])))
                vrp.write("\t{} {} {}\n".format(j+1, i+1, int(time[j][i])))
        vrp.write(";\n")

    # set up ampl
    ampl = AMPL(Environment('dev_log/optim/ampl'))

    # Interpret the two files
    ampl.read('dev_log/optim/models/splitclusters.mod')
    ampl.readData('dev_log/optim/models/vrp.dat')

    # Solve
    ampl.solve()

    # Get objective entity by AMPL name
    cntrs = ampl.getVariable('center')
    
    listCenters = []

    # Access all instances using an iterator
    for index, instance in cntrs:
        if instance.value():
            listCenters.append(centers[int(index)-1].getID())

    clusters = dict()
    for c in listCenters:
        clusters[c] = [c]

    # access the variable
    closestCenter = ampl.getVariable('closestCenter')
    for index, instance in closestCenter:
        if centers[int(index[0])-1].getID() not in listCenters and instance.value():
            clusters[centers[int(index[1]-1)].getID()].append(centers[int(index[0]-1)].getID())

    for c in clusters.values():
        if not 0 in c:
            c.append(0)
    
    #print(clusters)
    res = []
    
    for c in clusters.keys():
        h = s.getHamiltonianCycle(s.getListPointsByID(clusters[c]), 0, mode ="driving")
        clusters[c] = [s.getPointByID(p) for p in h[0]], h[1]
        res.append(clusters[c])

    return res

    return res
