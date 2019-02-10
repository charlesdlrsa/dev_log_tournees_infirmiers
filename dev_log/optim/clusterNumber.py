from space import Space
from amplpy import AMPL, Environment

"""
Need: 
    - space.walkingThreshold
    - space.dmin
    - space.dmax
    - space.nb_points
    - space.points
    - space.kmDist
"""

def numberOfClusters(s):
    """
    Compute the minimum number of cluster having a radius bounded by
    the minimimum between the average between dmin and dmax and the 
    walkingThreshold (=2.0 by default), which is a distance in kilometers.

    The office is set to be a center by default. 
    NB: The office id has to be set to 0.

    @return: the minimal number of clusters
    """
    threshold = min(s.walkingThreshold, (s.dmax+s.dmin)/2.0)
    with open("models/clustering.dat", "w") as clustering:
        clustering.write("# threshold for walking distance\n")
        clustering.write("param d:= {};\n".format(threshold))
        
        clustering.write("\n")
        
        clustering.write("# nombre de sommets {}\n".format(s.nb_points))
        clustering.write("set V :=\n")
        for p in s.points:
            clustering.write("\t{}\n".format(p.getID()))
        clustering.write(";\n")

        clustering.write("\n")

        clustering.write("# id_sommet1, id_sommet2, distance\n")
        clustering.write("param distance :=\n")
        for p in s.points:
            p_ID = p.getID()
            clustering.write("\t{} {} 0\n".format(p_ID, p_ID))
        for i in range(s.nb_points):
            for j in range(i+1, s.nb_points):
                p_ID1 = s.points[i].getID()
                p_ID2 = s.points[j].getID()
                clustering.write("\t{} {} {:.4f}\n".format(p_ID1, p_ID2, s.kmDist[i][j]))
                clustering.write("\t{} {} {:.4f}\n".format(p_ID2, p_ID1, s.kmDist[i][j]))
        clustering.write(";\n")

    # set up ampl
    ampl = AMPL(Environment('ampl'))

    # Interpret the two files
    ampl.read('models/clustering.mod')
    ampl.readData('models/clustering.dat')

    # Solve
    print("Get number of clusters")
    ampl.solve()

    # Get objective entity by AMPL name
    numberCenters = ampl.getObjective('numberCenters')
    
    s.setClusterNumber(numberCenters.get().value())