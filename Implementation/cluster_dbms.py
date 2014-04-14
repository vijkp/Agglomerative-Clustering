#!/usr/bin/python
# Class for defining cluster and its nodes along with other information
import networkx as nx

class Cluster:
    """Cluster class is a group of nodes"""
    def __init__(self, lst, cl_coeff = -1):
        self.id = str(sum(lst)) + str(lst[0:10])
        self.data = lst
        self.cl_coeff = cl_coeff
    def show(self):
        print "Cluster ID:" + str(self.id) + " Elements:"+ str(self.data)+ " coeff:" + str(self.cl_coeff)


