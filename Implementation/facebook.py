import networkx as nx
import sys
import csv
import pickle
import math
l = []
G = nx.Graph()
lines=open("/home/ubuntu/DBProject/Implementation/facebook_combined.txt", "r").readlines()

for line in lines:
    tokens = line.split()
    node1 = tokens[0]
    node2 = tokens[1]
    if not(node1 in l):
        l.append(node1)
        G.add_node(node1)
    elif not(node2 in l):
        l.append(node2)
        G.add_node(node2)
    G.add_edge(node1, node2)

dataset_name = "facebook_graph"
gl_name = dataset_name + "-gldata.csv" 
pckl_name = dataset_name + ".pckl"

line = ["id1", "id2"]  
outputfd = csv.writer(open(gl_name, 'wb'), delimiter=',', quotechar='|')
outputfd.writerow(line)
edges_list = G.edges()
for line in edges_list:
    outputfd.writerow(line)
print ("graphlab data file saved {}".format(gl_name))
f = open(pckl_name, 'w') 
pickle.dump(G, f) 
f.close()
print ("pckl file saved as {}".format(pckl_name)) 
print len(G.nodes())
print G.edges()
