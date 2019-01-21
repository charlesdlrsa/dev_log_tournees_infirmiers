reset;
option solver gurobi;

param t;
param k;
param maxt;

set V;
param duration{V};
param n := card(V);

set A within{V, V};
param time{A};

# decision variable
var center{V}, binary;

# office is a center
param office = 0;
subject to officeIsCenter:
	if office in V then center[office] = 1.0;

# clustering variable
var closestCenter{V cross V}, binary;

# the closest center has to be a center
subject to isCenter{v in V, c in V}:
	closestCenter[v,c] <= center[c];
	
# every point should be in a cluster
subject to hasCenter{v in V}:
	sum{c in V} closestCenter[v,c] = 1;

# the radius of a cluster has to be smaller than the thresold time
subject to maxDistance{v in V, c in V}:
	time[v,c] * closestCenter[v,c] <= t;
	
# there are at most k centers
subject to maxKCenter:
	sum{v in V} center[v] <= k;

# cluster value
var clusterValue{V}, >= 0;

# the cluster value is hold by the center
subject to holdValue{c in V}:
	clusterValue[c] = sum{v in V}(duration[v] + time[v,c]) * closestCenter[v,c];
	
# the value of a cluster has to be smaller than the threshold
subject to clusterValueIsBounded{v in V}:
	clusterValue[v] <= center[v] * maxt;
	
# minimize the cluster values
minimize clusterValues:
	sum{c in V} clusterValue[c];