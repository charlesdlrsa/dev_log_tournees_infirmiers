reset;
option solver gurobi;

# max cluster size
param maxClusterSize;

# max walking time
param maxWalkingTime;

set V;
param duration{V};
param n := card(V);

set A within{v in V, w in V};
param drivingTime{A};
param walkingTime{A};

# decision variable
var center{V}, binary;
	
# clustering variable
var closestCenter{V cross V}, binary;

# cluster value
var clusterValue{V}, >= 0;

# office is a center
param office := 0;
subject to officeIsCenter{v in V}:
	v <> office or center[v] = 1;

# the closest center has to be a center
subject to isCenter{v in V, c in V}:
	closestCenter[v,c] <= center[c];
	
# every point should be in a cluster
subject to hasCenter{v in V}:
	sum{c in V} closestCenter[v,c] = 1;

# the closest center should effectively be the closest one
subject to isClosest{v in V, w in V}:
	sum{c in V} closestCenter[v,c] * walkingTime[v,c] * center[w] <= walkingTime[v,w];

# the distance to a point in the cluster should be smaller than the threshold
subject to maxFootTime{v in V, c in V}:
	walkingTime[v,c] * closestCenter[v,c] <= maxWalkingTime;

# the cluster value is held by the center
subject to holdValue{c in V}:
	clusterValue[c] = 
		center[c] * (drivingTime[office,c] + drivingTime[c,office]) 
		+ sum{v in V}(duration[v] + walkingTime[v,c] + walkingTime[c,v]) * closestCenter[v,c];
	
# the value of a cluster has to be smaller than the threshold
subject to clusterValueIsBounded{v in V}:
	clusterValue[v] <= center[v] * maxClusterSize;
	
# minimizing the number of centers (thus maximizing the cluster values)
minimize numberCenters:
	sum{v in V} center[v];