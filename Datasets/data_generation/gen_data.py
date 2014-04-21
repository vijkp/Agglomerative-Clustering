#!/usr/bin/python
import sys
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import random
import math
import numpy
from networkx.generators.classic import empty_graph, path_graph, complete_graph
from collections import defaultdict
import pickle
import os
import csv

def plot_degree_histogram(graph, filename):
    degree_dist = sorted(nx.degree(graph).values(), reverse=True)
    dmax = max(degree_dist)
    hist, bin_edges =  numpy.histogram(degree_dist, range(dmax))
    plt.bar(bin_edges[:-1], hist, width = 1)
    plt.xlim(0, max(bin_edges)+10)
    plt.ylabel("number of nodes")
    plt.xlabel("degree")
    plt.savefig(filename)
    plt.clf()

def add_edges_to_two_groups(output, group1, group2, edges_to_add, prob):
    g1nodes = group1.nodes()
    g2nodes = group2.nodes()
    g1_sample = random.sample(g1nodes, int(len(g1nodes)*.25))
    g2_sample = random.sample(g2nodes, int(len(g2nodes)*.25))

    for i in g1_sample:
        random_g2_sample = random.sample(g2_sample, int(edges_to_add))
        for j in random_g2_sample:
            if random.random() < prob:
                output.add_edge(i, j)

def add_edges_to_groups(output_graph, groups_list, edges_to_add, prob, level):
    total_groups = len(groups_list)
    edges_per_node = max((3 - level), 1)
    triangle_prob = 0.1*level
    if False:
        random_graph = nx.random_regular_graph(int(total_groups/3), total_groups)
    else:
        random_graph = nx.powerlaw_cluster_graph(total_groups, edges_per_node, triangle_prob, random.random()*10)
    random_edges = random_graph.edges()
    
    for edge in random_edges:
        e0 = edge[0]
        e1 = edge[1]
        if random.random() > 0.3:
            e0, e1 = e1, e0
        print("adding level{} edges between group{} and group{}".format(level, e0, e1))
        add_edges_to_two_groups(output_graph, groups_list[e0], groups_list[e1], edges_to_add, prob)

if len(sys.argv) < 6:
    print "Invalid number of arguments"
    print "Example: ./connected_graphs.py <no. of groups> <nodes_per_group> <avg_edges_per_node> <dataset-name> <edge_addition_prob> [plot graph flag]"
    print "./connected_graphs.py 5 50 10  dataset-name"
    exit()

total_edges = 0
total_groups = int(sys.argv[1])
nodes_per_group = int(sys.argv[2])
random_edges_per_node = int(sys.argv[3])
triangle_prob = 0.8
edge_addition_prob = 0.1
dataset_name = sys.argv[4]
input_prob = float(sys.argv[5])
if len(sys.argv) >= 7:
    if sys.argv[6] == "True":
        plot_graph = True
else:
    plot_graph = False


if os.path.exists(dataset_name):
    print "error: dataset already exists"
else: 
    os.makedirs(dataset_name)
    print("Directory {} created".format(dataset_name))

dataset_name = dataset_name + "/" + dataset_name
image_name = dataset_name + ".png"
pckl_name = dataset_name + ".pckl"
hist_name = dataset_name + "-degree_hist.png"
gl_name = dataset_name + "-gldata.csv"
statfile_name = dataset_name + "-stats.txt"

# save stats to a file
fsf = open(statfile_name, 'w')
fsf.write("argument list\n")
fsf.write(str(sys.argv) + "\n")

groups_list = []
output_graph = nx.Graph()

for i in range(total_groups):
    groups_list.append(nx.powerlaw_cluster_graph(nodes_per_group, random_edges_per_node, triangle_prob, random.random()*10))
    groups_list[i] = nx.convert_node_labels_to_integers(groups_list[i],first_label=(nodes_per_group*i))
    output_graph = nx.union(output_graph, groups_list[i])
    print("group{} created".format(i))

#nx.draw(output_graph)
#plt.show()

edges_to_add = math.ceil(random_edges_per_node/5)
add_edges_to_groups(output_graph, groups_list, edges_to_add, input_prob, 1) 
add_edges_to_groups(output_graph, groups_list, edges_to_add, float(input_prob/3), 2) 
add_edges_to_groups(output_graph, groups_list, edges_to_add, float(input_prob/9), 3) 
add_edges_to_groups(output_graph, groups_list, edges_to_add, float(input_prob/27), 4) 
add_edges_to_groups(output_graph, groups_list, edges_to_add, float(input_prob/81), 5) 

total_edges = output_graph.number_of_edges()
total_nodes = output_graph.number_of_nodes()
plot_degree_histogram(output_graph, hist_name)

fsf.write("total edges: " + str(total_edges) + "\n")
fsf.write("total nodes: " + str(total_nodes) + "\n")
print "total edges:", total_edges
print "data generation complete"
if plot_graph:
    plt.axis('off')
    position = nx.graphviz_layout(output_graph, prog='sfdp')
    nx.draw_networkx_nodes(output_graph, position, node_size=20, node_color=output_graph.degree().values())
    nx.draw_networkx_edges(output_graph, position, alpha=0.2)
    plt.savefig(image_name, bbox_inches='tight', dpi=1000);
    print "plot saved as ", image_name
    plt.clf()

# save csv file
line = ["id1", "id2"]
outputfd = csv.writer(open(gl_name, 'wb'), delimiter=',', quotechar='|')
outputfd.writerow(line)
edges_list = output_graph.edges()
for line in edges_list:
    outputfd.writerow(line)
print ("graphlab data file saved {}".format(gl_name))

# save graph structures on disk
f = open(pckl_name, 'w')
pickle.dump(output_graph, f)
f.close()
print ("pckl file saved as {}".format(pckl_name))

# close stat file
fsf.close()
exit()

