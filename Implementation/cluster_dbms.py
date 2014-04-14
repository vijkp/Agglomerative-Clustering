#!/usr/bin/python
# Class for defining cluster and its nodes along with other information
import networkx as nx

class Cluster:
    """Cluster class is a group of nodes"""
    def __init__(self, lst, clcoeff = 0):
        self.id = str(sum(lst)) + str(lst[0:10])
        self.data = lst
        self.clcoeff = clcoeff
    def show(self):
        print "Cluster ID:" + str(self.id) + " Elements:"+ str(self.data)+ " coeff:" + str(self.clcoeff)


