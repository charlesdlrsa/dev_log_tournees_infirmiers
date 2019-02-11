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

var x{A}, binary;
var tourID{v in V : v <> 1}, >= 1, <= k;

subject to source{i in V : i <> 1}:
	sum{j in V : i <> j} x[i,j] = 1;

subject to start:
	sum{v in V : v <> 1} x[1,v] = k;

subject to target{j in V : j <> 1}:
	sum{i in V : i <> j} x[i,j] = 1;
	
subject to end:
	sum{v in V : v <> 1} x[v,1] = k;

#subject to shareTourID{(i,j) in A : i <> 1 and j <> 1}:
#	if x[i,j] then tourID[i] = tourID[j];

#subject to outgoingTourID{(i,j) in A : i <> 1 and j <> 1}:
#	if x[1,i] and x[1,j] then tourID[i] - tourID[j] <> 0;

#subject to incomingTourID{(i,j) in A : i <> 1 and j <> 1}:
#	if x[i,1] and x[j,1] then tourID[i] - tourID[j] <> 0;

subject to respectTourID{v in V, w in V : v <> 1 and w <> 1 and v <> w}:
	tourID[v] >= x[w,v]*(tourID[w]);

subject to respectTourID2{v in V, w in V : v <> 1 and w <> 1 and v <> w}:
	x[w,v]*(tourID[v]) <= tourID[w];

subject to uniqueOutgoing{i in V, j in V : i <> 1 and j <> 1 and i <> j}:
	(x[1,i] = 0 or x[1,j] = 0) ==> tourID[i] <> tourID[j];

var tourTime{v in V};

#subject to initTourTime:
#	tourTime[1] = duration[1];

#subject to respectTimeDuration{v in V: v <> 1}:
#	tourTime[v] =  duration[v] + sum{w in V : w <> v} x[w,v]*(tourTime[w]);

#subject to fitInGiventime{v in V : v <> 1}:
#	x[v,1] * (tourTime[v] + time[v,1]) <= maxt;

var t{A}, >= 0, integer;

subject to tokens{(i,j) in A}:
	t[i,j] <= (n-1) * x[i,j];
	
subject to dropToken{i in V}:
	sum{j in V : i <> j} t[j,i] - sum{j in V : i <> j}  t[i,j] == if i = 1 then 1-n else 1;

minimize total_time:
	sum{i in V, j in V : i <> j} time[i,j] * x [i,j];