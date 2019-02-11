from dev_log.optim.space import Space, GmapApiError
from amplpy import AMPL, Environment

"""
Need
    - space.points
    - space.getGoogleTravelTimes
    - space.regenerateCyclingPath
"""

def hamiltonian(s, points, starting_point):
    """
    Compute an hamiltonian cycle on the set of points.
    It uses a google maps key. Note that mode is "walking".
    
    @param points: should be a subset of s.points
    """
    n = len(points)

    if n == 1:
        path, travel_time = points, 0
    
    else:
        try:
            travel_times = s.getGoogleTravelTimes(points, "walking")
        except:
            raise GmapApiError
    
        if n == 2:
            if points[0].getID() == starting_point:
                p1, p2 =  points[0], points[1]
            else:
                p2, p1 =  points[0], points[1]
            path, travel_time = [p1, p2, p1], travel_times[0][1] + travel_times[1][0]

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
                        hamiltonian.write("\t{} {} {}\n".format(i+1, j+1, travel_times[i][j]))
                        hamiltonian.write("\t{} {} {}\n".format(j+1, i+1, travel_times[j][i]))
                hamiltonian.write(";\n")

            # set up ampl
            ampl = AMPL(Environment('dev_log/optim/ampl'))

            # Interpret the two files
            ampl.read('dev_log/optim/models/travellingSalesman.mod')
            ampl.readData('dev_log/optim/models/travellingSalesman.dat')

            # Solve
            print("get Hamiltonian cycle")
            ampl.solve()
            
            #regenerate the path
            x = ampl.getVariable("x")

            path, travel_time = s.regenerateCyclingPath(points, x, travel_times, starting_point)
    return [p.getID() for p in path], travel_time