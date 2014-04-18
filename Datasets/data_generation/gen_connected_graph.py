#!/usr/bin/python
import sys
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
from networkx.generators.classic import empty_graph, path_graph, complete_graph
from collections import defaultdict
import pickle

try:
    from itertools import izip_longest as zip_longest
except ImportError: # Python3 has zip_longest
    from itertools import zip_longest
from networkx.utils import is_string_like

def union_all(graphs, rename=(None,) , name=None):
    graphs_names = zip_longest(graphs,rename)
    U, gname = next(graphs_names)
    for H,hname in graphs_names:
        U = nx.union(U, H, (gname,hname),name=name)
        gname = None
    return U

if len(sys.argv) < 5:
    print "Invalid number of arguments"
    print "Example: ./connected_graphs.py <group_total_nodes> <avg_edges> <triange_prob> <prob_edge_addition> [<dataset-name>]"
    print "./connected_graphs.py 50 10 .8 .3 [<image name>]"
    exit()

dataset_name = "output"
if len(sys.argv) == 6:
    dataset_name = sys.argv[5];
image_name = dataset_name + ".png"
dot_name = dataset_name + ".dot"
pckl_name = dataset_name + ".pckl"
neo4j_data = dataset_name + "-neo4j.txt"

total_edges = 0
nodes_per_group = int(sys.argv[1])
random_edges_per_node = int(sys.argv[2])
triangle_prob = float(sys.argv[3])
edge_addition_prob = float(sys.argv[4]) 

G = nx.powerlaw_cluster_graph(nodes_per_group, random_edges_per_node, triangle_prob,10)
Gnode_count = G.number_of_nodes()
Gnodes = G.nodes()
print "Edges in group G: ", G.number_of_edges()

H = nx.powerlaw_cluster_graph(nodes_per_group, random_edges_per_node, triangle_prob,10)
H = nx.convert_node_labels_to_integers(H,first_label=nodes_per_group)
Hnodes = H.nodes()
Hnode_count = H.number_of_nodes()
print "Edges in group H: ", H.number_of_edges()

I = nx.powerlaw_cluster_graph(nodes_per_group, random_edges_per_node, triangle_prob,10)
I = nx.convert_node_labels_to_integers(I,first_label=nodes_per_group*2)
Inodes = I.nodes()
Inode_count = I.number_of_nodes()
print "Edges in group I: ", I.number_of_edges()

J = nx.powerlaw_cluster_graph(nodes_per_group, random_edges_per_node, triangle_prob,10)
J = nx.convert_node_labels_to_integers(J,first_label=nodes_per_group*3)
Jnodes = J.nodes()
Jnode_count = J.number_of_nodes()
print "Edges in group J: ", J.number_of_edges()

R=union_all((G,H,I,J))

count = 0
for i in Gnodes:
    random_Hnodes = random.sample(Hnodes, int(random_edges_per_node*.5))
    for j in random_Hnodes:
        if random.random() < edge_addition_prob:
            R.add_edge(i, j)
            count = count+1

for i in Hnodes:
    random_Inodes = random.sample(Inodes, int(random_edges_per_node*.5))
    for j in random_Inodes:
        if random.random() < edge_addition_prob:
            R.add_edge(i, j)
            count = count+1

for i in Inodes:
    random_Jnodes = random.sample(Jnodes, int(random_edges_per_node*.5))
    for j in random_Jnodes:
        if random.random() < edge_addition_prob:
            R.add_edge(i, j)
            count = count+1

for i in Jnodes:
    random_Gnodes = random.sample(Gnodes, int(random_edges_per_node*.5))
    for j in random_Gnodes:
        if random.random() < edge_addition_prob:
            R.add_edge(i, j)
            count = count+1

total_edges = R.number_of_edges()
print "total edges:", total_edges
print "new edges across two groups: ", count
print "data generation complete"
nx.draw(R)
plt.savefig(image_name);
print "plot saved as ", image_name
#plt.show()
nx.write_dot(R, dot_name)

# save graph structures on disk
f = open(pckl_name, 'w')
pickle.dump(R, f)
f.close()

exit()

# save graph in structured format for loading into neo4j database 
fd = open(neo4j_data, "w")
Rnumber = R.number_of_nodes()
Redges = R.edges()
for i in range(Rnumber):
    fd.write("CREATE (n:Person {name: \"p" + str(i)+ "\" });\n")  
for i in Redges:
    fd.write("MATCH (person1:Person) WHERE person1.name = \"p" + str(i[0]) + "\"")
    fd.write("MATCH (person2:Person) WHERE person2.name = \"p" + str(i[1]) + "\"")
    fd.write("CREATE (person1)-[:FRIENDS_WITH]->(person2);\n")
fd.close()

exit()
