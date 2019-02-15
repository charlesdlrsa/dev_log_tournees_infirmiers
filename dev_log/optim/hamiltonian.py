from dev_log.optim.space import Space, GmapApiError
from amplpy import AMPL, Environment

def rotateToStartingElement(l, e):
    """
    Rotate a list such that the list starts with the first element e.
    """
    if e not in l:
        raise ValueError(str(e) + "is not in list")
    while l[0] != e:
        x = l.pop(0)
        l.append(x)

def hamiltonian(s, pointIDs, starting_pointID, mode="walking"):

    """
    Compute an hamiltonian cycle on the set of points.
    It uses a google maps key. Note that mode is "walking" or "driving".
    
    @param points: should be a a list of ID's refering to subset of s.points
    """
    n = len(pointIDs)

    if n == 1:
        path, travel_time = pointIDs, 0
    
    else:
        if n == 2:
            if pointIDs[0] == starting_pointID:
                p_ID1, p_ID2 =  pointIDs[0], pointIDs[1]
            else:
                p_ID2, p_ID1 =  pointIDs[0], pointIDs[1]
            path = [p_ID1, p_ID2, p_ID1]
            travel_time = s.getDistSource2Target(p_ID1, p_ID2, mode) +  s.getDistSource2Target(p_ID2, p_ID1, mode)

        else:
            """
            For the solver to work, the points has to be numbered from 1 to n
            """

            with open("dev_log/optim/models/travellingSalesman.dat", "w") as hamiltonian:
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
                        p_ID1, p_ID2 =  pointIDs[i], pointIDs[j]
                        hamiltonian.write("\t{} {} {}\n".format(i+1, j+1, s.getDistSource2Target(p_ID1, p_ID2, mode)))
                        hamiltonian.write("\t{} {} {}\n".format(j+1, i+1, s.getDistSource2Target(p_ID2, p_ID1, mode)))
                hamiltonian.write(";\n")

            # set up ampl
            ampl = AMPL(Environment('dev_log/optim/ampl/linux'))


            # Interpret the two files
            ampl.read('dev_log/optim/models/travellingSalesman.mod')
            ampl.readData('dev_log/optim/models/travellingSalesman.dat')

            # Solve
            print("get Hamiltonian cycle")
            ampl.solve()
            
            #regenerate the path
            x = ampl.getVariable("x")

            # Given a list of pointIDs and the ampl transition matrix, we need to rebuild the path.
            # pointIDs is list of point  ID's such that its order is the same as the index in x (amplMatPath)
            # x is the transition matrix (returned by ampl) describing the path (zero, one matrix) such that:
            #   x[i,j] = 1 iff the path goes from pointIDs[i] to pointIDs[j]

            i = 0
            j = -1
            path = []

            while j != 0:
                for k in range(n):
                    if i != k and x[i+1,k+1].value():
                        j = k
                p_ID1, p_ID2 =  pointIDs[i], pointIDs[j]
                i = j
                path.append(pointIDs[i])
            rotateToStartingElement(path, starting_pointID)
            path.append(starting_pointID)

            # compute travel_time
            travel_time = 0
            for k in range(n):
                p_ID1, p_ID2 =  path[k], path[k+1]
                travel_time += s.getDistSource2Target(p_ID1, p_ID2, mode)

    return path, travel_time