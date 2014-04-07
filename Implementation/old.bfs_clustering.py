#!/usr/bin/python
# Traverse and cluster a graph database

from py2neo import neo4j, rel, cypher
import pickle
import sys
import re
import Queue
import networkx as nx

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

def check_and_merge_clusters(index):
    global clusters
    global G
        
    given_cluster = []
    total_clusters = len(clusters)
    cluster_coeff_all = [0]*total_clusters
    cluster_coeff_temp = [0]*total_clusters
    for string in clusters[index]:
        given_cluster.append(int(string))
    given_graph = G.subgraph(given_cluster)
    clustering_coeff_given   = nx.average_clustering(given_graph)
    
    temp_index = 0
    while temp_index < total_clusters:
        temp_cluster = []
        for string in clusters[temp_index]:
            temp_cluster.append(int(string))
        temp_graph = G.subgraph(temp_cluster)
        temp_graph_all = G.subgraph(temp_cluster + given_cluster)

        clustering_coeff_all = nx.average_clustering(temp_graph_all)
        clustering_coeff_temp = nx.average_clustering(temp_graph)
        cluster_coeff_all[temp_index] = clustering_coeff_all
        cluster_coeff_temp[temp_index] = clustering_coeff_temp        
        temp_index = temp_index + 1

    # Find the index with highest coefficient and combine them
    max_index = cluster_coeff_all.index(max(cluster_coeff_all))
    if clustering_coeff_given > .94:
        clustering_coeff_given = 0.94
    if cluster_coeff_temp[max_index] > .94:
        cluster_coeff_temp[max_index] =0.94
    if (cluster_coeff_all[max_index] >= .95*clustering_coeff_given) and (cluster_coeff_all[max_index] >= .95*cluster_coeff_temp[max_index]):
        combine_cluster(index, max_index)
    
def combine_cluster(cl1, cl2):
    global clusters   
    if cl1 == cl2:
        return
    clusters[cl1] = clusters[cl1] + clusters[cl2]
    clusters.remove(clusters[cl2])

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
    
    counter = 0
    # Start processing nodes from the traverse queue
    while bfs_queue.empty() == False:
        bfs_node = bfs_queue.get()
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
        
        # counter to monitor the progress
        counter = counter + 1
        if counter%10 == 0:
            print str(counter) + " nodes processed"

    print "Clusters after initial pass"
    for cluster in clusters:
        print cluster

    print "Clusters after final pass"
    # combine clusters ever more
    total_clusters = len(clusters)
    clusters_before = total_clusters
    clusters_after = 0
    while clusters_before != clusters_after:
        clusters_before = clusters_after
        temp_index = 0    
        while temp_index  < len(clusters):
            check_and_merge_clusters(temp_index)
            temp_index = temp_index + 1
        clusters_after = len(clusters)
    for cluster in clusters:
        print cluster
        print "Nodes:" + str(len(cluster))
    return
  
if __name__ == "__main__":
    main()
