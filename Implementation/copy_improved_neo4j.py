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
import datetime
from cluster_dbms import Cluster as cl

def check_and_merge_clusters(index, flag = True):
    global clusters
    global G
    result = False 
    given_cluster = []
    total_clusters = len(clusters)
    cluster_coeff_all = [0]*total_clusters
    cluster_coeff_temp = [0]*total_clusters
    clustering_coeff_given   = get_clustering_coeff(clusters[index], G, cluster_dict)
    
    temp_index = 0
    while temp_index < total_clusters:
        if temp_index == index:
            temp_index += 1
            continue
        #if len(clusters[index]) > len(clusters[temp_index]):
        #    temp_index += 1
        #    continue
        clustering_coeff_all = get_clustering_coeff(clusters[index] + clusters[temp_index], G, cluster_dict)
        clustering_coeff_temp = get_clustering_coeff(clusters[temp_index], G, cluster_dict)
        cluster_coeff_all[temp_index] = clustering_coeff_all
        cluster_coeff_temp[temp_index] = clustering_coeff_temp        
        temp_index = temp_index + 1
    
    # Find the index with highest coefficient and combine them
    max_index = cluster_coeff_all.index(max(cluster_coeff_all))
    print "max: " + str(cluster_coeff_all[max_index]) + "  given: " + str(clustering_coeff_given) + "  temp: " + str(cluster_coeff_temp[max_index])
    print clusters[index]
    print clusters[max_index]
    if flag:
        threshold_factor = .98
    else: 
        threshold_factor = .90
    
    if clustering_coeff_given > .96:
        clustering_coeff_given = 1
    if cluster_coeff_temp[max_index]  > .96:
        cluster_coeff_temp[max_index] =1
    if (cluster_coeff_all[max_index] >= threshold_factor*clustering_coeff_given) and (cluster_coeff_all[max_index] >= threshold_factor*cluster_coeff_temp[max_index]):
        print "combined"
        if max_index < index:
            result = True
        combine_cluster(index, max_index)
    
    return result


def get_clustering_coeff(cllist, graph, cluster_dict):
    #print cllist
    global hit
    global nothit
    cllist_int = []
    for string in cllist:
        cllist_int.append(int(string))
    
    cl_id = get_id(cllist_int)
    if cl_id not in cluster_dict:
        nothit += 1
        add_list_to_cluster_dict(cllist_int, graph, cluster_dict)
    else:
        #print "returning from dict"
        hit += 1
    return cluster_dict[cl_id].cl_coeff

def add_list_to_cluster_dict(cllist, graph, cluster_dict):
    cl_id  = get_id(cllist)
    if cl_id not in cluster_dict:
        sub_graph = graph.subgraph(cllist)
        clustering_coeff = nx.average_clustering(sub_graph)
        cluster_dict[cl_id] = cl(cllist, clustering_coeff)
    return 

def get_id(list):
    return str(sum(list)) + str(list[0:10])

def generate_cluster_dict(clusters, cluster_dict, graph):
    for i in clusters:
        i_int = []
        for string in i:
            i_int.append(int(string))
        id = get_id(i_int)
        if id not in cluster_dict:
            sub_graph = graph.subgraph(i_int)
            clustering_coeff = nx.average_clustering(sub_graph)
            cluster_dict[id] = cl(i_int, clustering_coeff)

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

    clustering_coeff_1   = get_clustering_coeff(cl1_int, G, cluster_dict) 
    clustering_coeff_2   = get_clustering_coeff(cl2_int, G, cluster_dict) 
    clustering_coeff_all = get_clustering_coeff(cl1_int + cl2_int, G, cluster_dict) 

    print (str)(clustering_coeff_1) + " " + (str)(clustering_coeff_2) +" "+ (str)(clustering_coeff_all)   
	
    if clustering_coeff_1 == 1:
        clustering_coeff_1 = .96

    if clustering_coeff_2 == 1:
        clustering_coeff_2 = .96
    
    if (clustering_coeff_1 == 0) and (clustering_coeff_2 == 0):
        return False
    
    fraction = .97
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
    print datetime.datetime.now() 
    bfs_index = {}
    bfs_queue = Queue.Queue()
    neighbor_dict = {}
    jindex_threshold = 0.3
    
    global clusters
    global cluster_dict
    # Login to database
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # Initial seed to start the traversal
    bfs_queue.put("1")
    bfs_index["1"] = 1

    # Start processing nodes from the traverse queue
    nodes_per_group = int(G.number_of_nodes()/10)
    count = 1
    while bfs_queue.empty() == False:
        bfs_node = bfs_queue.get()
        if count%nodes_per_group == 0:
            print "Processed " + str(count) + " nodes"
        count += 1
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
        # Add node to the neigbhors list
        # neighbor_dict[str(bfs_node)].append(bfs_node)

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
    
    print "level-1 complete"
    print datetime.datetime.now()

    # Print clusters
    count = 1
    for i in clusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        count += 1
   
    # load all the clusters into a dictionary
    generate_cluster_dict(clusters, cluster_dict, G)

    ## combine clusters in the second pass
    clusters_before = len(clusters)
    clusters_after = 0
    while clusters_before != clusters_after:
        clusters_before = clusters_after
        temp_index = 0   
        while temp_index  < len(clusters):
            check_and_merge_clusters(temp_index)
            temp_index = temp_index + 1
        clusters_after = len(clusters)
        if clusters_after < 4:
            break
    
    print "level-2 complete"
    print datetime.datetime.now()
    # Print clusters
    count = 1
    for i in clusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        count += 1
    print "hit: " + str(hit)
    print "nothit: " + str(nothit)
    
    ## combine clusters in the third pass
    clusters_before = len(clusters)
    clusters_after = 0
    while (clusters_before != clusters_after) and (clusters_before >= 4):
        clusters_before = clusters_after
        temp_index = 0   
        while temp_index  < len(clusters):
            if check_and_merge_clusters(temp_index, False) == False:
                temp_index = temp_index + 1
        clusters_after = len(clusters)
        if clusters_after < 4:
            break
    print "level-3 complete"
    count = 1
    for i in clusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        count += 1
    print "hit: " + str(hit)
    print "nothit: " + str(nothit)

# Globals
clusters = []
cluster_dict = {}
hit = 0
nothit = 0

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

if __name__ == "__main__":
    main()
