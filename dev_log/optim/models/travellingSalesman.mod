reset;
option solver gurobi;

set V;
param n := card(V);

set A within{v in V, w in V : v <> w};

param time{A};

var x{A}, binary;

subject to source{i in V}:
	sum{j in V : i <> j} x[i,j] = 1;

subject to target{j in V}:
	sum{i in V : i <> j} x[i,j] = 1;

var t{A}, >= 0, integer;

subject to tokens{(i,j) in A}:
	t[i,j] <= (n-1) * x[i,j];
	
subject to dropToken{i in V}:
	sum{j in V : i <> j} t[j,i] - sum{j in V : i <> j}  t[i,j] == if i = 1 then 1-n else 1;

minimize total_time:
	sum{i in V, j in V : i <> j} time[i,j] * x [i,j];