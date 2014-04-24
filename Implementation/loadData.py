import os
import csv
import itertools
import sys
import graphlab as gl
import numpy as np
import pandas as pd
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#import scipy
global g

def getNeighbour(nodeId):
    S=g.get_edges(src_ids=[str(nodeId)])
    return list(S['__dst_id'])

def startGraphlab(filename):
    global g
    #filename = sys.argv[1] #give path to csv file
    #filename = "/home/ubuntu/java_jni/dataset-final/sparse/edges-20k/edges-20k-gldata.csv"
    sf = gl.SFrame.read_csv(filename, column_type_hints={'id1': str, 'id2': str})
    g = gl.Graph()
    #make graph undirected
    g = g.add_edges(sf, src_field='id1', dst_field='id2')
    g = g.add_edges(sf, src_field='id2', dst_field='id1')
    g.summary()
    #num_nodes = int(sys.argv[2])#enter number of nodes in graph
    '''
    for i in xrange(0, 30):
        print i
        S=g.get_edges(src_ids=[str(i)])
        print i
        print list(S['__dst_id'])
    '''
