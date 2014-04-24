#!/usr/bin/python
# Class for defining cluster and its nodes along with other information

class Cluster:
    """Cluster class is a group of nodes"""
    def __init__(self, id,  lst, neighbor_list = [], cl_coeff = -1):
        self.id = id
        self.data = lst
        self.cl_coeff = cl_coeff
        self.neighbor_list = neighbor_list
    def show(self):
        print "Cluster ID:" + str(self.id) + " Elements:"+ str(self.data)+ " Neighbor list:" + str(self.neighbor_list) + " coeff:" + str(self.cl_coeff)

class nQueryResult:
    """Result of neo4j query"""
    def __init__(self, nodeid, result):
        self.node = nodeid
        self.data = result
    def show(self):
        print "nodeid {} result {}".format(self.node, self.data)
