reset;
option solver gurobi;

param k;
set V;
param distance{V, V};


# decision variable
var center{V}, binary;

# office is a center
param office := 0;
subject to officeIsCenter{v in V}:
	v <> office or center[v] = 1;
	
# there are at most k centers
subject to maxKCenter:
	sum{v in V} center[v] <= k;

# clustering variable
var closestCenter{V cross V}, binary;

# the closest center has to be a center
subject to isCenter{v in V, c in V}:
	closestCenter[v,c] <= center[c];
	
# every point should be in a cluster
subject to hasCenter{v in V}:
	sum{c in V} closestCenter[v,c] = 1;

# minimising the distance
minimize distanceMediane:
	sum{v in V, c in V} distance[v,c] * closestCenter[v,c];