# Tabu Search
the basic tabu search implementaion with pyhton using TSP as an example.


Tabu search is a metaheuristic search method employing local search methods used for mathematical optimization. It was created by Fred W. Glover in 1986[1] and formalized in 1989.


## Pseudo code
```
sBest ← s0
 2 bestCandidate ← s0
 3 tabuList ← []
 4 tabuList.push(s0)
 5 while (not stoppingCondition())
 6     sNeighborhood ← getNeighbors(bestCandidate)
 7     bestCandidate ← sNeighborhood[0]
 8     for (sCandidate in sNeighborhood)
 9         if ( (not tabuList.contains(sCandidate)) and (fitness(sCandidate) > fitness(bestCandidate)) )
10             bestCandidate ← sCandidate
11         end
12     end
13     if (fitness(bestCandidate) > fitness(sBest))
14         sBest ← bestCandidate
15     end
16     tabuList.push(bestCandidate)
17     if (tabuList.size > maxTabuSize)
18         tabuList.removeFirst()
19     end
20 end
21 return sBest
```
(the Pseudo code from [wikipedia](https://en.wikipedia.org/wiki/Tabu_search))


## Numerical example
'R101.txt' is from solomon benchmark, more details can be found in [solomon-benchmark](https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/).



## Ref
 1. Fred Glover (1986). "Future Paths for Integer Programming and Links to Artificial Intelligence". Computers and Operations Research. 13 (5): 533–549. doi:10.1016/0305-0548(86)90048-1.  
 2. Fred Glover (1989). "Tabu Search – Part 1". ORSA Journal on Computing. 1 (2): 190–206. doi:10.1287/ijoc.1.3.190.
