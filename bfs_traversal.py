#!/usr/bin/python
from py2neo import neo4j
from py2neo import rel
import pickle
import sys
import re
import Queue

# Breadth first search traversal of data in neo4j
# state - 0: unprocessed
# state - 1: processed

flag = True

def main():
    bfs_index = {}
    bfs_queue = Queue.Queue()
   
    # Login to database
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # Adding the first element in the queue to start the traversal
    bfs_queue.put("1") 
    bfs_queue.put("20")
    bfs_index["1"] = 1
    bfs_index["20"] = 1 
    
    # Iterate through the queue
    while bfs_queue.empty() == False:
        bfs_node = bfs_queue.get()
        #print bfs_node
        query = neo4j.CypherQuery(graph_db, "MATCH (a)-[r]-(b) WHERE b.id="+"\""+str(bfs_node)+"\""+" RETURN a").execute()
        for r in query:
            m = re.findall("\"id\":(.*?)}", str(r.a))
            node_id = m[0].strip("\"")
            if node_id not in bfs_index:
                bfs_index[node_id] = 1 
                bfs_queue.put(node_id)
 
    print bfs_index

if __name__ == "__main__":
    main()
