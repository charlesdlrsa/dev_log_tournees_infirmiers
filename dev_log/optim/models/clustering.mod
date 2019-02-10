reset;
option solver gurobi;

set V;
param distance{V, V};
param d;

# decision variable
var center{V}, binary;

# office if a center
param office = 0;
subject to officeIsCenter:
	center[office] = 1.0;

# clustering variable
var closestCenter{V cross V}, binary;

# the closest center has to be a center
subject to isCenter{v in V, c in V}:
	closestCenter[v,c] <= center[c];
	
# every point should be in a cluster
subject to hasCenter{v in V}:
	sum{c in V} closestCenter[v,c] = 1;

# the cluster value has to be smaller than the thresold
subject to maxDistance{v in V, c in V}:
	distance[v,c] * closestCenter[v,c] <= d;

# minimising the number of centers
minimize numberCenters:
	sum{v in V} center[v];