#!/usr/bin/python
from py2neo import neo4j
from py2neo import rel
from py2neo import cypher
import pickle
import sys

def main():
    #provide path to data pickle file.
    data_file = sys.argv[1]
    fd = open(data_file, "r")
    graph = pickle.load(fd)
    nodes =  graph.nodes()
    edges = graph.edges()
    print len(edges)
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # delete old databse
    result = neo4j.CypherQuery(graph_db, "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r").execute() 
    print result

    community = graph_db.get_or_create_index(neo4j.Node, "community")
    #inserting nodes in databasei
    node_count = 0
    for node in nodes:
        node_count+=1
        alice = community.create_if_none("id", node, None)
        if node_count%1000 == 0:
            print "{} nodes created".format(node_count)

    #creating an instance of batch to take bunch of request for making relatioships between nodes.
    batch = neo4j.WriteBatch(graph_db)
    #defining the relationship between nodes

    #alice, = graph_db.create({"name": "Alice Smith"})
    #people = graph_db.get_or_create_index(neo4j.Node, "People")
    #people.create_if_none("family_name", "Smith", alice)
    edge_count = 0
    count = 0
    for edge in edges:
        edge_count += 1
        count+=1
        node1 =  edge[0]
        node2 =  edge[1]
        #print node1
        #print node2
        ref1 = community.get("id", str(node1))
        ref2 = community.get("id", str(node2))
        #print ref1
        #print ref2
        batch.create(rel(ref1[0], "KNOWS", ref2[0]))
        if count>=1000:
            batch.run()
            count = 0
            batch.clear()
        if edge_count%10000 == 0:
            print "{} edges created".format(edge_count)
    results = batch.run()
    batch.clear()
    #print nodes
    #print
    #print edges

if __name__ == "__main__":
    main()

