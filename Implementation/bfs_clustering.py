#!/usr/bin/python
# Traverse and cluster a graph database

from py2neo import neo4j
from py2neo import rel
from py2neo import cypher
import pickle
import sys
import re
import Queue

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
    clusters = []
    jindex_threshold = 0.3

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

if __name__ == "__main__":
    main()
