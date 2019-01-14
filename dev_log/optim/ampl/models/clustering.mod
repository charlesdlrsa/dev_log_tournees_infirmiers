param d;

set V;
param distance{V, V} >= 0;

# variable de décision
var center{V}, binary;

# variable de clustering
var nearestCenter{V cross V}, binary;

subject to isCenter{v in V, c in V}:
	nearestCenter[v,c] <= center[c];
	
subject to hasCenter{v in V}:
	sum{c in V} nearestCenter[v,c] = 1;

subject to maxDistance{v in V, c in C}:
	distance[v,c] * nearestCenter[v,c] <= d

# minimising number of centers
minimize numberCenters:
	sum{v in V} center[v];