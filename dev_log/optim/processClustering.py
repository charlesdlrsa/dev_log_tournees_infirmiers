from amplpy import AMPL, Environment

"""
Need: 
    - space.clusterNumber
"""

def runClustering(s):
    """
    Cluster the space, using the k-median paradigm:
        provide the set of $k$ vertices ${c_1, ... c_k}$ minimizing
            sum_{v in V} min_i d_{c_i,v}
    
    k is stored in space.clusterNumber

    The office is set to be a center by default. 
    NB: The office id has to be set to 0.

    @store  a dict representing the clusters in space.clusters.

    The dictionnary representing the cluster has the format:
        - key = center
        - value = list of the points in the cluster (always starting with the center)
    """
    with open("models/clustering.dat", "r") as clustering:
        with open("models/kmedian.dat", "w") as kmedian:
            kmedian.write("# number of clusters\n")
            kmedian.write("param k := {};\n".format(s.clusterNumber))

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
    print("cluster space")
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

    s.setClusters(clusters)