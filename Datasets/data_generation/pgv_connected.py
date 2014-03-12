#!/usr/bin/env python
import pygraphviz as pgv

B=pgv.AGraph('data.dot') # create a new graph from file
B.layout(prog='fdp') # layout with default (neato)
B.draw('simple.png') # draw png
print "Wrote simple.png"

