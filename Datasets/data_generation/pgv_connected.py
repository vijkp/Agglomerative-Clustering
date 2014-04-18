#!/usr/bin/env python
import pygraphviz as pgv
import sys
import pickle

filename = sys.argv[1]

fd = open(filename, "r")
graph = pickle.load(fd)
nodes =  graph.nodes()
edges = graph.edges()

G=pgv.AGraph() # create a new graph from file
G.add_nodes_from(nodes)
G.add_edges_from(edges)
G.layout(prog='fdp') # layout with default (neato)
G.draw('simple.png') # draw png
print "Wrote simple.png"

