#!/usr/bin/env python
import pygraphviz as pgv
import sys

image_name = "output.png"
if len(sys.argv) >= 2:
    filename = sys.argv[1]

if len(sys.argv) == 3:
        image_name = sys.argv[2]

B=pgv.AGraph(filename) # create a new graph from file
B.layout(prog='fdp') # layout with default (neato)
B.draw(image_name) # draw png
print "Wrote " + image_name

