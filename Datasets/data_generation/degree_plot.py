#!/usr/bin/python
import matplotlib.pyplot as plt
import pickle
import networkx
    degree_dist = sorted(nx.degree(graph).values(), reverse=True)
    dmax = max(degree_dist)
    hist, bin_edges =  numpy.histogram(degree_dist, range(dmax))

