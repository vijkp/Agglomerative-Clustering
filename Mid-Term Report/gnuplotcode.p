# GNU Plot file

set   autoscale                        # scale axes automatically
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set xtic auto                          # set xtics automatically
set ytic auto                          # set ytics automatically
#set log y 
set title "Neo4j Clustering Performance"
set xlabel "Size of graph (number of nodes)"
set ylabel "Time of execution (seconds)"
plot    "Data.txt" title "Neo4j" with linespoints
