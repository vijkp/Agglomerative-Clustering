#!/usr/bin/env python
import pygraphviz as pgv
import sys

filename = sys.argv[1]
print filename
B=pgv.AGraph(filename) # create a new graph from file
B.layout(prog='fdp') # layout with default (neato)
B.draw('simple.png') # draw png
print "Wrote simple.png"

