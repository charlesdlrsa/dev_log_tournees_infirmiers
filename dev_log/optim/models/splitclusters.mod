reset;
option solver gurobi;

# number of clusters
param k;

# max cluster size
param maxt;

set V;
param duration{V};
param n := card(V);

set A within{v in V, w in V : v <> w};
param time{A};

# decision variable
var center{V}, binary;
	
# clustering variable
var closestCenter{V cross V}, binary;

# cluster value
var clusterValue{V}, >= 0;

# office is a not a center
param office := 1;
subject to officeIsNotCenter{v in V}:
	v <> office or center[v] = 0;
subject to officeIsNotCluster{v in V : v <> 1}:
	closestCenter[v,1] = 0;
subject to officeValue{v in V}:
	v <> office or clusterValue[v] = 0;

# the closest center has to be a center
subject to isCenter{v in V, c in V}:
	closestCenter[v,c] <= center[c];
	
# every point should be in a cluster
subject to hasCenter{v in V}:
	sum{c in V} closestCenter[v,c] = 1;
		
# there are at most k centers
subject to maxKCenter:
	sum{v in V} center[v] <= k;

# the cluster value is hold by the center
subject to holdValue{c in V : c <> 1}:
	clusterValue[c] = center[c] * (time[1,c] + time[c,1]) + sum{v in V : v <> c}(duration[v] + time[v,c]) * closestCenter[v,c];
	
# the value of a cluster has to be smaller than the threshold
subject to clusterValueIsBounded{v in V}:
	clusterValue[v] <= center[v] * maxt;
	
# minimize the cluster values
minimize clusterValues:
	sum{c in V} clusterValue[c];