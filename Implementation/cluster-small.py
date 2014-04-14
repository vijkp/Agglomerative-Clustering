#!/usr/bin/python
import sys
import matplotlib.pyplot as plt
import math
import pickle
from operator import itemgetter
import networkx as nx
clusters = []

def unique(a):
    a = set(a)
    return list(a)

def can_combine_cluster2(cl1, cl2):
    combine = False
    temp_graph1 = G.subgraph(cl1)
    temp_graph2 = G.subgraph(cl2)
    temp_graph_all = G.subgraph(cl1 + cl2)
    
    if len(cl1) >= len(cl2):
        common_elements = list(set(cl1).intersection(set(cl2)))
        if len(common_elements) > 0.8*len(cl2):
            combine = True
        #print common_elements
    else:
        common_elements = list(set(cl2).intersection(set(cl1)))
        if len(common_elements) > 0.8*len(cl1): 
            combine = True


    clustering_coeff_1   = nx.average_clustering(temp_graph1)
    clustering_coeff_2   = nx.average_clustering(temp_graph2)
    clustering_coeff_all = nx.average_clustering(temp_graph_all)
    #print cl1
    #print cl2
    #print (str)(clustering_coeff_1) + " " + (str)(clustering_coeff_2) +" "+ (str)(clustering_coeff_all)
    #print " "
    
    if combine:
        if (clustering_coeff_all >= .8*clustering_coeff_1) and (clustering_coeff_all >= 0.8*clustering_coeff_2):
            return True
    else:
        if (clustering_coeff_all >= clustering_coeff_1) and (clustering_coeff_all >= clustering_coeff_2):
            return True
    return False 

def can_combine_cluster(cl1, cl2):
    temp_graph1 = G.subgraph(cl1)
    temp_graph2 = G.subgraph(cl2)
    temp_graph_all = G.subgraph(cl1 + cl2)

    clustering_coeff_1   = nx.average_clustering(temp_graph1)
    clustering_coeff_2   = nx.average_clustering(temp_graph2)
    clustering_coeff_all = nx.average_clustering(temp_graph_all)
    #print (str)(clustering_coeff_1) + " " + (str)(clustering_coeff_2) +" "+ (str)(clustering_coeff_all)
    
    if clustering_coeff_1 < .7:
        if cl1 in clusters: clusters.remove(cl1)
        return False
    if clustering_coeff_2 < .7:
        if cl2 in clusters: clusters.remove(cl2)
        return False
    if (clustering_coeff_all >= clustering_coeff_1) and (clustering_coeff_all >= clustering_coeff_2):
        return True
    return False 

def combine_cluster(cl1, cl2):
    global clusters   
    if cl1 == cl2:
        return
    clusters[cl1] = unique(clusters[cl1] + clusters[cl2])
    clusters.remove(clusters[cl2])

if len(sys.argv) < 2:
    print "Error: Invalid number of arguments"
    print "Example: ./small_cluster.py <data_filename>"
    exit()

## main ##

# Load graph data from file
data_file = sys.argv[1]
fd = open(data_file, "r")
graph = pickle.load(fd);

G = nx.Graph()
G.add_nodes_from(graph.nodes())
G.add_edges_from(graph.edges())
#nx.draw(G)
#plt.show()

print "Total number of nodes: " + (str)(graph.number_of_nodes())
print "Total number of edges: " + (str)(graph.number_of_edges())

while graph.number_of_nodes() != 0:
    # Calculate degree for each node
    graph_degrees = graph.degree()

    # Find the node with highest degree
    sorted_graph_degrees = sorted(graph.degree_iter(), key = itemgetter(1), reverse=True)
    #print sorted_graph_degrees
    node_highest_degree = sorted_graph_degrees[0][0]
    #print "Node with highest degree: " + (str)(node_highest_degree) + " Degree: " + (str)(sorted_graph_degrees[0][1])

    # Find the neighbors of the highest degree node
    temp_list = graph.neighbors(node_highest_degree)
    if len(temp_list) > 1:
        temp_list.append(node_highest_degree)
        clusters.append(temp_list)

    # Remove all connections of the node with maximum degree
    graph.remove_node(node_highest_degree)
    for i in temp_list:
        try:
            graph.remove_edge(node_highest_degree, i)
        except:
            try:
                graph.remove_edge(i, node_highest_degree)
            except:
                pass
#    nx.draw(graph)
#    plt.show()

print "level-1 complete."
#for i in clusters:
#    print i

total_clusters = len(clusters)
clusters_before = total_clusters
clusters_after = 0
while clusters_before != clusters_after:
    clusters_before = clusters_after
    temp_index1 = 0    
    while temp_index1  < total_clusters:
        temp_cluster1 = clusters[temp_index1]
        temp_index2   = len(clusters) - 1 
        while temp_index2 > temp_index1:
            temp_cluster2 = clusters[temp_index2] 
            if (can_combine_cluster(temp_cluster1, temp_cluster2) == True)  and (temp_index1 != temp_index2):
                combine_cluster(temp_index1, temp_index2)
            temp_index2 = temp_index2 - 1
        temp_index1 = temp_index1 + 1
        total_clusters = len(clusters)
        clusters_after = total_clusters

print "level-2 complete."

# filter the noise i.e. remove nodes with 1 degree
for i in clusters:
    temp = G.subgraph(i)
    graph_degrees = temp.degree()
    for key in graph_degrees:
        if graph_degrees[key] <= 2:
            i.remove(key)
print "noise removal complete."

## combine clusters ever more
total_clusters = len(clusters)
clusters_before = total_clusters
clusters_after = 0
while clusters_before != clusters_after:
    clusters_before = clusters_after
    temp_index1 = 0    
    while temp_index1  < total_clusters:
        temp_cluster1 = clusters[temp_index1]
        temp_index2   = len(clusters) - 1 
        while temp_index2 > temp_index1:
            temp_cluster2 = clusters[temp_index2] 
            if (can_combine_cluster2(temp_cluster1, temp_cluster2) == True)  and (temp_index1 != temp_index2):
                combine_cluster(temp_index1, temp_index2)
            temp_index2 = temp_index2 - 1
        temp_index1 = temp_index1 + 1
        total_clusters = len(clusters)
        clusters_after = total_clusters

print "level-3 complete."
count = 1
for i in clusters:
    print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)

exit()

# show the nodes in a graph
C = nx.Graph()
count = 1
for i in clusters:
    print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
    temp = G.subgraph(i)
    C.add_nodes_from(temp.nodes())
    C.add_edges_from(temp.edges())
    count += 1

pos = nx.spring_layout(C) 

colors = ['r', 'b', 'g', 'y']
count = 0
for i in clusters:
    temp = G.subgraph(i)
    nx.draw_networkx(temp, pos, node_color=colors[count])
    count += 1
#plt.show()
    
