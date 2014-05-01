#!/usr/bin/python
# Traverse and cluster a graph database

from py2neo import neo4j
from py2neo import rel
from py2neo import cypher
import pickle
import sys
import re
import Queue
#import networkx as nx
import datetime
import math
from cluster_dbms import Cluster as cl
import random
from loadDataGraphLab import startGraphlab
from loadDataGraphLab import getNeighborlist
from loadDataGraphLab import getTotalNodes
import thresholds as th

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

def generate_cluster_dict(clusters, cluster_dict):
    for i in clusters:
        i_int = []
        neighbor_list = []
        for string in i:
            i_int.append(int(string))
            neighbor_list = union(neighbor_list, neighbor_dict[string])
        id = get_id(i_int)
        if id not in cluster_dict:
            cluster_dict[id] = cl(id, i, neighbor_list)
            #cluster_dict[id].show()

def combine_cluster(cl1, cl2):
    global clusters   
    if cl1 == cl2:
        return
    clusters[cl1] = clusters[cl1] + clusters[cl2]
    clusters.remove(clusters[cl2])

def can_combine_cluster2(cl1, cl2, avgl, flag=False):
    l1 = len(cl1)
    l2 = len(cl2)
     
    if (l1 > avgl) and (l2 > avgl):
        return False

    if l2 < 3:
        #print "less than 3"
        return False

    if l1 > l2:
        temp = cl2
        cl2 = cl1
        cl1 = cl2

    neighbor_list_1   = get_neighbor_list_for_group(cl1, cluster_dict) 
    neighbor_match = intersection(neighbor_list_1, cl2)
    neighbor_match_ratio = float(float(len(neighbor_match))/float(len(neighbor_list_1)))

    if flag:
        print "cl1: {} cl2: {} ng1: {} nm: {} ratio: {}".format(len(cl1), len(cl2), len(neighbor_list_1), len(neighbor_match), neighbor_match_ratio)

    if neighbor_match_ratio > neighbor_match_th:
        if flag:
            print "combined"
        return True
    else:
        return False

def can_combine_cluster(cl1, cl2):
    neighbor_list_1   = get_neighbor_list_for_group(cl1, cluster_dict) 
    neighbor_list_2   = get_neighbor_list_for_group(cl2, cluster_dict) 
    jindex = compute_jaccardIndex2(neighbor_list_1, neighbor_list_2)
    
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
    result = "START b=node:community(\'id:" + str(bfs_node) + "\') MATCH b-[:KNOWS]-a return a"
    return result

def main(inputfile):
    # Variables
    start_time = datetime.datetime.now() 
    bfs_index = {}
    bfs_queue = Queue.Queue()
    
    global clusters
    global cluster_dict
    global neighbor_match_th
    # start graphlab
    startGraphlab(inputfile)
    
    fdlog = open(outputlog, "w")
    total_nodes = getTotalNodes()
    print "Total nodes in the system: {}".format(total_nodes)
    fdlog.write("Total nodes in the system: {}\n".format(total_nodes))

    # Initial seed to start the traversal 
    if total_nodes >= 40:
        random_sample = random.sample(range(total_nodes), 20)
    else:
        random_sample = random.sample(range(total_nodes), 2)

    print "Random nodes to start the graph travresal {}".format(random_sample)
    for i in random_sample:
        bfs_queue.put(str(i))
        bfs_index[str(i)] = 1

    # Start processing nodes from the traverse queue
    nodes_per_group = int(total_nodes*0.1)
    count = 1
    while bfs_queue.empty() == False:
        bfs_node = bfs_queue.get()
        if count%nodes_per_group == 0:
            current_time = datetime.datetime.now()
            time_taken = float(datetime.timedelta.total_seconds(current_time - start_time))
            print "Processed {} nodes in {} seconds".format(count, time_taken)
        count += 1
        neighbor_dict[str(bfs_node)] = []
        query = getNeighborlist(bfs_node) 
        for node_id in query:
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
            index = compute_jaccardIndex2(union_list, neighbor_dict[str(bfs_node)])
            if index >= jindex_threshold:
                #print index
                flag = 1
                cluster.append(bfs_node)
                break
        # If node has not found a cluster to merge with, create a new cluster
        if flag == 0:
            clusters.append([bfs_node])
    
    current_time = datetime.datetime.now()
    time_taken = float(datetime.timedelta.total_seconds(current_time - start_time))
    print "level-1 completes in {}".format(time_taken)
    fdlog.write("\nlevel-1 completes in {} seconds\n".format(time_taken))
    
    sortedclusters = sorted(clusters, lambda x,y: 1 if len(x)<len(y) else -1 if len(x)>len(y) else 0)
    
    count = 1
    for i in sortedclusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        fdlog.write("Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i) + "\n")
        count += 1

    clusters = sortedclusters

    # load all the clusters into a dictionary
    generate_cluster_dict(clusters, cluster_dict)

    ## combine clusters ever more
    total_clusters = len(clusters)
    clusters_before = total_clusters
    clusters_after = 0
    maxlen = len(sortedclusters[0])
    minlen = len(sortedclusters[total_clusters -1])
    avglen = int((minlen+maxlen)*0.5)
    print "avg length: {}".format(avglen)
    while clusters_before != clusters_after:
        not_joined = 0
        clusters_before = clusters_after
        temp_index1 = total_clusters -1 
        while temp_index1 > 1:
            temp_cluster1 = clusters[temp_index1]
            temp_index2   = 0
            while temp_index1 > temp_index2:
                temp_cluster2 = clusters[temp_index2]
                #print "inner inner loop "  + str(temp_index1) + " " + str(temp_index2) + " " + str(len(clusters))
                if (can_combine_cluster2(temp_cluster1, temp_cluster2, avglen) == True):
                    combine_cluster(temp_index2, temp_index1)
                    break
                temp_index2 = temp_index2 + 1
                if temp_index1 == temp_index2:
                    not_joined += 1
                    break
            total_clusters = len(clusters)
            temp_index1 = total_clusters -1 - not_joined 
        total_clustes = len(clusters)
        if total_clusters < 5:
            break
        clusters_after = total_clusters
    
    current_time = datetime.datetime.now()
    time_taken = float(datetime.timedelta.total_seconds(current_time - start_time))
    print "level-2 completes in {}".format(time_taken)
    fdlog.write( "\nlevel-2 completes in {} seconds\n".format(time_taken))
    sortedclusters = sorted(clusters, lambda x,y: 1 if len(x)<len(y) else -1 if len(x)>len(y) else 0)
    clusters = sortedclusters
    # Print clusters
    count = 1
    for i in clusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        fdlog.write("Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i) + "\n")
        count += 1

    #neighbor_match_th = 0.2
    neighbor_match_th = float(neighbor_match_th*0.68) 
    total_clusters = len(clusters)
    clusters_before = total_clusters
    clusters_after = 0
    minlen = len(sortedclusters[total_clusters -1])
    avglen = int((minlen+maxlen)*0.5)
    print "avg length: {}".format(avglen)
    while clusters_before != clusters_after:
        not_joined = 0
        clusters_before = clusters_after
        temp_index1 = total_clusters -1 
        while temp_index1 > 1:
            temp_cluster1 = clusters[temp_index1]
            temp_index2   = 0
            while temp_index1 > temp_index2:
                temp_cluster2 = clusters[temp_index2]
                #print "inner inner loop "  + str(temp_index1) + " " + str(temp_index2) + " " + str(len(clusters))
                if (can_combine_cluster2(temp_cluster1, temp_cluster2, avglen, False) == True):
                    combine_cluster(temp_index2, temp_index1)
                    break
                temp_index2 = temp_index2 + 1
                if temp_index1 == temp_index2:
                    not_joined += 1
                    break
            total_clusters = len(clusters)
            temp_index1 = total_clusters -1 - not_joined 
        total_clustes = len(clusters)
        if total_clusters < 5:
            break
        clusters_after = total_clusters

    current_time = datetime.datetime.now()
    time_taken = float(datetime.timedelta.total_seconds(current_time - start_time))
    print "level-3 completes in {}".format(time_taken)
    fdlog.write("\nlevel-3 completes in {}\n".format(time_taken))
    
    # Print clusters
    count = 1
    for i in clusters:
        print "Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i)
        fdlog.write("Cluster-"+ str(count) + " Total nodes: " + str(len(i)) + " " + str(i) + "\n")
        count += 1
    print "hit: " + str(hit)
    print "nothit: " + str(nothit)
    f = open(outputfile, 'w')
    pickle.dump(clusters, f)
    f.close()
    print "output clusters saved in pckl file {}".format(outputfile)
    fdlog.write("\nTotal time of execution: {} seconds\n".format(time_taken))

# Globals
clusters = []
cluster_dict = {}
hit = 0
nothit = 0
neighbor_dict = {}
jjindex_groups = th.jindex_groups
jindex_threshold = th.jindex_threshold
neighbor_match_th = th.neighbor_match_th

if len(sys.argv) < 3:
        print "Error: Invalid number of arguments"
        print "Usage: ./improved_neo4j2.py inputfile outputfile_name"
        exit()

outputfile = sys.argv[2] + "_clusters.pckl"
outputlog = sys.argv[2] + "_result.log"


if __name__ == "__main__":
    main(sys.argv[1])
