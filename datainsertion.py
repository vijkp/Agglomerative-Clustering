from py2neo import neo4j
from py2neo import rel
from py2neo import cypher
import pickle
import sys

def main():
    #provide path to data pickle file.
    #data_file = sys.argv[1]
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
     
    query = neo4j.CypherQuery(graph_db, "MATCH (a)-[r]-(b) WHERE b.id=\"2\" RETURN a").execute()
    #answer = query.execute()
    #answer2 = neo4$.CypherResults(answer)
    for r in query:
        print r.a
	#print type(r.p)
    exit()
    data_file = sys.argv[1]
    fd = open(data_file, "r")
    graph = pickle.load(fd)
    nodes =  graph.nodes()
    edges = graph.edges()
    print len(edges)
    print ashish
    community = graph_db.get_or_create_index(neo4j.Node, "community")
    #inserting nodes in database
    for node in nodes:
        alice = community.create_if_none("id", node, None)

    #creating an instance of batch to take bunch of request for making relatioships between nodes.
    batch = neo4j.WriteBatch(graph_db)
    #defining the relationship between nodes

    #alice, = graph_db.create({"name": "Alice Smith"})
    #people = graph_db.get_or_create_index(neo4j.Node, "People")
    #people.create_if_none("family_name", "Smith", alice)
    for edge in edges:
   
        node1 =  edge[0]
	node2 =  edge[1]
	print node1
	print node2
	ref1 = community.get("id", str(node1))
        ref2 = community.get("id", str(node2))
	print ref1
	print ref2
	batch.create(rel(ref1[0], "KNOWS", ref2[0]))

    results = batch.submit()   

    print nodes
    print
    print edges

if __name__ == "__main__":
    main()
