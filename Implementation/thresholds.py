#!/usr/bin/python

dense = False

if dense == True:
    """ thresholds for dense """
    print "picking up thresholds for dense graphs"
    jindex_threshold = 0.3
    jindex_groups = 0.75 
    neighbor_match_th = 0.3 
else:
    """ thresholds for sparse """
    print "picking up thresholds for sparse graphs"
    jindex_threshold = 0.17 
    jindex_groups = 0.75 
    neighbor_match_th = 0.25
