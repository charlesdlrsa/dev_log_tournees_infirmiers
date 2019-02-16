reset;
option solver gurobi;

# number of clusters
param k;

# max cluster size
param maxt;

set V;
param duration{V};
param n := card(V);

set A within{V,V};
param time{A};

# decision variable
var center{V}, binary;
	
# clustering variable
var closestCenter{V cross V}, binary;

# cluster value
var clusterValue{V}, >= 0;

# office is a not a center
param office := 0;
subject to officeIsNotCenter{v in V}:
	v <> office or center[v] = 0;
subject to officeIsNotCluster{v in V : v <> 1}:
	closestCenter[v,office] = 0;

# the closest center has to be a center
subject to isCenter{v in V, c in V}:
	closestCenter[v,c] <= center[c];
	
# every point should be in a cluster
subject to hasCenter{v in V}:
	sum{c in V} closestCenter[v,c] = 1;

# the closest center should effectively be the closest one
subject to isClosest{v in V, w in V}:
	sum{c in V} closestCenter[v,c] * time[v,c] * center[w] <= time[v,w];
		
# there are at most k centers
subject to maxKCenter:
	sum{v in V} center[v] = k;

# the cluster value is hold by the all points
subject to holdValue{c in V}:
	clusterValue[c] = 
		center[c] * (time[office,c] + time[c,office]) 
		+ sum{v in V}(duration[v] + time[v,c] + time[c,v]) * closestCenter[v,c];
	
# the value of a cluster has to be smaller than the threshold
subject to clusterValueIsBounded{v in V}:
	clusterValue[v] <= center[v] * maxt;

# mean value
var totalClusterValue >= 0;
subject to totalValue:
	totalClusterValue = sum{c in V} clusterValue[c];

# deviation
var deviation{V};
subject to computeDeviation{v in V}:
	deviation[v] = k * clusterValue[v] - totalClusterValue;

# under and above
var above{V}, >= 0;
var under{V}, >= 0;
subject to underAbove{v in V}:
	deviation[v] = above[v] - under[v];
	
# max deviation
var maxDeviation >= 0;
subject to maxDevAbove{v in V}:
	maxDeviation * k >= above[v];
subject to maxDevUnder{v in V}:
	center[v] = 0 or maxDeviation * k >= under[v];

# minimize the deviation
minimize minDeviation:
	maxDeviation;