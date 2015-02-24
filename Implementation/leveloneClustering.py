
from py2neo import neo4j
from py2neo import rel
from py2neo import cypher
import pickle
import sys
import re


def intersection(a, b):
 
    return list(set(a) & set(b))

def union(a, b):
 
    return list(set(a) | set(b))

def compute_jaccardIndex(list1, list2):

    number = len(union(list1, list2))
    if number==0:
        return 0.0
    return (float(float(len(intersection(list1, list2)))/float(number)))

def main():

    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    data_file = sys.argv[1]  
    fd = open(data_file, "r")
    graph = pickle.load(fd)
    nodes =  graph.nodes()
    edges = graph.edges()   

    #print nodes
    #print edges
    dict = {}

    clusters = []
    for vertex in nodes:
        dict[str(vertex)] = []
        query = neo4j.CypherQuery(graph_db, "MATCH (a)-[r]-(b) WHERE b.id="+"\""+str(vertex)+"\""+" RETURN a").execute()
        for r in query:
            m = re.findall("\"id\":(.*?)}", str(r.a))
            node_id = m[0].strip("\"")
            dict[str(vertex)].append(node_id)

        flag = 0
        #check if this vertex can be merged with previous clusters
        for cluster in clusters:
            union_list = []
            for node in cluster:
                union_list = union(union_list, dict[str(node)])
            index = compute_jaccardIndex(union_list, dict[str(vertex)])
            if index >= 0.4:
                flag = 1
                cluster.append(vertex)
                break
        
        if flag == 0:
            #if node has not found cluster to merge with, form a separate cluster
            clusters.append([vertex])
    
    print "Clusters"

    for cluster in clusters:
        print cluster
 

if __name__ == "__main__":
    main()
