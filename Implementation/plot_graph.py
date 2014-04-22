#!/usr/bin/python
import pickle
import sys
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx


def main():
    
    #provide path to data pickle file and clustered output file
    if len(sys.argv) != 3:
        print "Error: Invalid arguments!"
        print "./plot_graph <path_data_file.pckl> <path_clustered_output_file.pckl>"
        return

    data_file = sys.argv[1]
    output_file = sys.argv[2]
    fd = open(data_file, "r")
    fo = open(output_file, "r")
    graph = pickle.load(fd)
    nodes =  graph.nodes()
    edges = graph.edges()
    print "Total nodes: {}".format(graph.number_of_nodes())
    print "Total edges: {}".format(graph.number_of_edges())

    # Load and print clusters
    clusters = pickle.load(fo)
    reverse_mapping_dict = {}
    count = 1
    for cls in clusters:
        print "Cluster-{} Nodes:{} {}".format(count, len(cls), cls)
        for node in cls:
            reverse_mapping_dict[node] = count
        count += 1
    
    # Generate colors for each cluster
    color_array = []
    for node in nodes:
        color_array.append(int(reverse_mapping_dict[str(node)]))

    image_file = "output.png"
    # Now plot 
    plt.axis('off')
    position = nx.graphviz_layout(graph, prog='sfdp')
    nx.draw_networkx_nodes(graph, position, node_size=20, node_color=color_array)
    nx.draw_networkx_edges(graph, position, alpha=0.2)
    plt.savefig(image_file, bbox_inces='tight', dpi=1000)
    print "image saved as {}".format(image_file)
     
    return

if __name__ == "__main__":
    main()
