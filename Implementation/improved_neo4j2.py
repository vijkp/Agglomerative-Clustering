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
import math
from cluster_dbms import Cluster as cl

def check_and_merge_clusters(index, flag = True):
    global clusters
    result = False 
    given_cluster = []
    total_clusters = len(clusters)
    jaccard_index_all = [0]*total_clusters
    neighbor_list_given = get_neighbor_list_for_group(clusters[index], cluster_dict)
    
    temp_index = 0
    while temp_index < total_clusters:
        if temp_index == index:
            temp_index += 1
            continue
        #if len(clusters[index]) > len(clusters[temp_index]):
        #    temp_index += 1
        #    continue
        neighbor_list_current = get_neighbor_list_for_group(clusters[temp_index], cluster_dict)
        jaccard_index_all[temp_index] = compute_jaccardIndex2(neighbor_list_given, neighbor_list_current)
        temp_index = temp_index + 1
    # Find the index with highest coefficient and combine them
    max_index = jaccard_index_all.index(max(jaccard_index_all))
    #print "max: " + str(jaccard_index_all[max_index])     
    #print clusters[index]
    #print clusters[max_index]

    if jaccard_index_all[max_index] > jindex_groups:
        #print "combined"
        if index < max_index:
            combine_cluster(index, max_index)
        else: 
            combine_cluster(max_index, index)
        return True
    else: 
        return False

def get_neighbor_list_for_group(cllist, cluster_dict):
    global hit
    global nothit
    cllist_int = []
    for string in cllist:
        cllist_int.append(int(string))
    
    cl_id = get_id(cllist_int)
    if cl_id not in cluster_dict:
        nothit += 1
        add_list_to_cluster_dict(cl_id, cllist, cluster_dict)
    else:
        #print "returning from dict"
        hit += 1
    return cluster_dict[cl_id].neighbor_list


def get_clustering_coeff(cllist, graph, cluster_dict):
    global hit
    global nothit
    cllist_int = []
    for string in cllist:
        cllist_int.append(int(string))
    
    cl_id = get_id(cllist_int)
    if cl_id not in cluster_dict:
        nothit += 1
        add_list_to_cluster_dict(cl_id, cllist, graph, cluster_dict)
    else:
        #print "returning from dict"
        hit += 1
    return cluster_dict[cl_id].cl_coeff

def add_list_to_cluster_dict(cl_id, cllist, cluster_dict):
    neighbor_list = []
    if cl_id not in cluster_dict:
        for node in cllist:
            neighbor_list = union(neighbor_list, neighbor_dict[node])
        cluster_dict[cl_id] = cl(cl_id, cllist, neighbor_list)
    return 

def get_id(list):
    return str(sum(list)) + str(list[0:10])

def generate_cluster_dict(clusters, cluster_dict, graph):
    for i in clusters:
        i_int = []
        neighbor_list = []
        for string in i:
            i_int.append(int(string))
            neighbor_list = union(neighbor_list, neighbor_dict[string])
        id = get_id(i_int)
        if id not in cluster_dict:
            cluster_dict[id] = cl(id, i, neighbor_list)
            cluster_dict[id].show()

def combine_cluster(cl1, cl2):
    global clusters   
    if cl1 == cl2:
        return
    clusters[cl1] = clusters[cl1] + clusters[cl2]
    clusters.remove(clusters[cl2])

def can_combine_cluster(cl1, cl2):
    neighbor_list_1   = get_neighbor_list_for_group(cl1, cluster_dict) 
    neighbor_list_2   = get_neighbor_list_for_group(cl2, cluster_dict) 
    jindex = compute_jaccardIndex2(neighbor_list_1, neighbor_list_2)
    #print cl1
    #print cl2
    #print jindex
    
    if jindex > jindex_groups:
        #print "combined"
        return True
    else: 
        return False

def intersection(a, b):
    return list(set(a) & set(b))

def union(a, b):
    return list(set(a) | set(b))

def compute_jaccardIndex2(list1, list2):
    len1 = len(list1)
    len2 = len(list2)
    if len1 == 0 or len2 == 0:
        return 0.0
    return (float(float(len(intersection(list1, list2)))/(math.sqrt(len1*len2))))

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
    
    global clusters
    global cluster_dict
    # Login to database
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # Initial seed to start the traversal
    bfs_queue.put("1")
    bfs_index["1"] = 1

    # Start processing nodes from the traverse queue
    nodes_per_group = 25
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
        neighbor_dict[str(bfs_node)].append(str(bfs_node))
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
    
    sortedclusters = sorted(clusters, lambda x,y: 1 if len(x)>len(y) else -1 if len(x)<len(y) else 0)
    
    count = 1
    for i in sortedclusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        count += 1

    clusters = sortedclusters

    # load all the clusters into a dictionary
    generate_cluster_dict(clusters, cluster_dict, G)

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
                if (temp_index1 != temp_index2):
                    if (can_combine_cluster(temp_cluster1, temp_cluster2) == True):
                        combine_cluster(temp_index1, temp_index2)
                        continue
                temp_index2 = temp_index2 + 1
            temp_index1 = temp_index1 + 1
            total_clusters = len(clusters)
            if total_clusters < 5:
                break
            clusters_after = total_clusters
    
    print "level-2 complete"
    print datetime.datetime.now()
    # Print clusters
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
neighbor_dict = {}
jindex_threshold = 0.3
jindex_groups = 0.4

if len(sys.argv) < 1:
        print "Error: Invalid number of arguments"
        print "Usage: ./improved_neo4j2.py"
        exit()

# Load graph data from file
# data_file = "../Datasets/dataset-small/nodes-90/nodes-90.pckl"
#data_file = sys.argv[1]
#fd = open(data_file, "r")
#graph = pickle.load(fd);

G = nx.Graph()
#G.add_nodes_from(graph.nodes())
#G.add_edges_from(graph.edges())

if __name__ == "__main__":
    main()
