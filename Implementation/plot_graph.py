#!/usr/bin/python
import pickle
import sys
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx


def main():
    
    #provide path to data pickle file and clustered output file
    if len(sys.argv) < 4:
        print "Error: Invalid arguments!"
        print "./plot_graph <path_data_file.pckl> <path_clustered_output_file.pckl> <imagefilename.png> [dpi]"
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

    image_file = sys.argv[3]
    image_file_before = "before_" + image_file
    image_file_after =  "after_" + image_file
    if len(sys.argv) == 5:
        inputdpi = sys.arvg[4]
    else:
        inputdpi = 1000
    # Now plot 
    plt.axis('off')
    nx.write_dot(graph, "sample.dot")
    agraph = nx.to_agraph(graph)
#    agraph.layout(prog='neato', args='overlap=false') 
#    agraph.draw('test_graph.png')
    
    exit(1)
    position = nx.graphviz_layout(graph, prog='sfdp', args='overlap=false')
    nx.draw_networkx_nodes(graph, position, node_size=10, color='b')
    nx.draw_networkx_edges(graph, position, alpha=0.2)
    plt.savefig(image_file_before, bbox_inces='tight', dpi=inputdpi)
    print "image saved as {}".format(image_file_before)
    
    nx.draw_networkx_nodes(graph, position, node_size=10, node_color=color_array)
    nx.draw_networkx_edges(graph, position, alpha=0.2)
    plt.savefig(image_file_after, bbox_inces='tight', dpi=inputdpi)
    print "image saved as {}".format(image_file_after)

    return

if __name__ == "__main__":
    main()
