#!/usr/bin/python
# Traverse and cluster a graph database

from py2neo import neo4j
from py2neo import rel
from py2neo import cypher
import pickle
import sys
import re
import Queue
import networkx as nx
from cluster_db Cluster as cl


clusters = []

if len(sys.argv) < 2:
        print "Error: Invalid number of arguments"
        print "Usage: ./bfs_clustering.py <filepath to pckl file>"
        exit()

# Load graph data from file
# data_file = "../Datasets/dataset-small/nodes-90/nodes-90.pckl"
data_file = sys.argv[1]
fd = open(data_file, "r")
graph = pickle.load(fd);

G = nx.Graph()
G.add_nodes_from(graph.nodes())
G.add_edges_from(graph.edges())

def combine_cluster(cl1, cl2):
    global clusters   
    if cl1 == cl2:
        return
    clusters[cl1] = clusters[cl1] + clusters[cl2]
    clusters.remove(clusters[cl2])

def can_combine_cluster(cl1, cl2):
    global G
    cl1_int = []
    cl2_int = []
    for string in cl1:
        cl1_int.append(int(string))
    for string in cl2:
        cl2_int.append(int(string))

    temp_graph1 = G.subgraph(cl1_int)
    temp_graph2 = G.subgraph(cl2_int)
    temp_graph_all = G.subgraph(cl1_int + cl2_int)
    
    clustering_coeff_1   = nx.average_clustering(temp_graph1)
    clustering_coeff_2   = nx.average_clustering(temp_graph2)
    clustering_coeff_all = nx.average_clustering(temp_graph_all)
    #print (str)(clustering_coeff_1) + " " + (str)(clustering_coeff_2) +" "+ (str)(clustering_coeff_all)   
	
    if clustering_coeff_1 == 1:
        clustering_coeff_1 = .98

    if clustering_coeff_2 == 1:
        clustering_coeff_2 = .98
    
    if (clustering_coeff_1 == 0) and (clustering_coeff_2 == 0):
        return False
    
    fraction = 1
    if (clustering_coeff_all > fraction*clustering_coeff_1) and (clustering_coeff_all > fraction*clustering_coeff_2):
        #print "combine"
        return True
    return False 

def intersection(a, b):
    return list(set(a) & set(b))

def union(a, b):
    return list(set(a) | set(b))

def compute_jaccardIndex(list1, list2):
    number = len(union(list1, list2))
    if number==0:
        return 0.0
    return (float(float(len(intersection(list1, list2)))/float(number)))

def get_query_string(bfs_node):
    return "MATCH (a)-[r]-(b) WHERE b.id="+"\""+str(bfs_node)+"\""+" RETURN a"

def main():
    # Variables
    bfs_index = {}
    bfs_queue = Queue.Queue()
    neighbor_dict = {}
    jindex_threshold = 0.3
    
    global clusters
    # Login to database
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # Initial seed to start the traversal
    bfs_queue.put("1")
    bfs_index["1"] = 1

    # Start processing nodes from the traverse queue
    while bfs_queue.empty() == False:
        bfs_node = bfs_queue.get()
        print "Processing node " + str(bfs_node)
        neighbor_dict[str(bfs_node)] = []
        query = neo4j.CypherQuery(graph_db, get_query_string(bfs_node)).execute()
        for r in query:
            m = re.findall("\"id\":(.*?)}", str(r.a))
            node_id = m[0].strip("\"")
            neighbor_dict[str(bfs_node)].append(node_id)
            # Index and queue for bfs traversal
            if node_id not in bfs_index:
                bfs_index[node_id] = 1
                bfs_queue.put(node_id)

        flag = 0
        # Check if this bfs_node can be merged with previous clusters
        for cluster in clusters:
            union_list = []
            for node in cluster:
                union_list = union(union_list, neighbor_dict[str(node)])
            index = compute_jaccardIndex(union_list, neighbor_dict[str(bfs_node)])
            if index >= jindex_threshold:
                flag = 1
                cluster.append(bfs_node)
                break

        # If node has not found a cluster to merge with, create a new cluster
        if flag == 0:
            clusters.append([bfs_node])

    print "Clusters"
    for cluster in clusters:
        print cluster

    # load all the clusters into a dictionary

    print "level 2"
    ## combine clusters ever more
    total_clusters = len(clusters)
    clusters_before = total_clusters
    clusters_after = 0
    while clusters_before != clusters_after:
        clusters_before = clusters_after
        temp_index1 = 0    
        while temp_index1  < total_clusters:
            temp_cluster1 = clusters[temp_index1]
            temp_index2   = 1 
            while (temp_index1 < len(clusters)) and (temp_index2 < len(clusters)):
                temp_cluster2 = clusters[temp_index2]
                #print str(temp_index1) + " " + str(temp_index2)
                if (can_combine_cluster(temp_cluster1, temp_cluster2) == True)  and (temp_index1 != temp_index2):
                    combine_cluster(temp_index1, temp_index2)
                    continue
                temp_index2 = temp_index2 + 1
            temp_index1 = temp_index1 + 1
            total_clusters = len(clusters)
            clusters_after = total_clusters

    for cluster in clusters:
        print cluster
        print len(cluster)


if __name__ == "__main__":
    main()
