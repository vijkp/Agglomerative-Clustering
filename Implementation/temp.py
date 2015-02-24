#!/usr/bin/python
# Traverse and cluster a graph database

from py2neo import neo4j, rel, cypher
import pickle
import sys
import re
import Queue
import networkx as nx

clusters = []


# Load graph data from file
data_file = "../Datasets/dataset-small/nodes-30/nodes-30.pckl"
fd = open(data_file, "r")
graph = pickle.load(fd);

G = nx.Graph()
G.add_nodes_from(graph.nodes())
G.add_edges_from(graph.edges())

ls = [20, 21, 25, 24]

subgraph = G.subgraph(ls)
coeff = nx.clustering(subgraph)

print coeff
