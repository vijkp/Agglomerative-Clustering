#!/usr/bin/python
import pickle
import sys
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx


def main():
    
    #provide path to data pickle file and clustered output file
    if len(sys.argv) < 3:
        print "Error: Invalid arguments!"
        print "./plot_graph <imagefilename.png> <path_data_file.pckl> <path_clustered_output_file.pckl> [dpi]"
        return

    data_file = sys.argv[2]
    fd = open(data_file, "r")
    graph = pickle.load(fd)
    nodes =  graph.nodes()
    edges = graph.edges()
    print "Total nodes: {}".format(graph.number_of_nodes())
    print "Total edges: {}".format(graph.number_of_edges())
 
    if len(sys.argv) == 5:
        inputdpi = sys.arvg[4]
    else:
        inputdpi = 500

    image_file = sys.argv[1]
    image_file_before = "before_" + image_file
    image_file_after =  "after_" + image_file

        # Now plot 
    plt.axis('off')
    #nx.write_dot(graph, "sample.dot")
    #agraph = nx.to_agraph(graph)
#    agraph.layout(prog='neato', args='overlap=false') 
#    agraph.draw('test_graph.png')
    ncolor1 = (1.0, 0.91891891891891897, 0.0, 1.0) 
    ncolor2 = (1.0, 0.36777954425013254, 0.0, 1.0)
    ncolor3 = (1.0, 0.91891891891891897, 0.0, 1.0)
    ncolor4 = (0.55113937466878637, 1.0, 0.0, 1.0)
    ncolor5 = (0.0, 1.0, 0.0, 1.0)
    ncolor6 = (0.0, 1.0, 0.54817625975121254, 1.0)
    ncolor7 = (0.0, 0.92391304347826042, 1.0, 1.0)
    ncolor8 = (0.0, 0.36977834612105687, 1.0, 1.0)
    ncolor9 = (0.16304347826086973, 0.0, 1.0, 1.0)
    position = nx.graphviz_layout(graph, prog='sfdp')
    nx.draw_networkx_nodes(graph, position, node_size=10, node_color=ncolor4, linewidths=0.6)
    nx.draw_networkx_edges(graph, position, alpha=0.2)
    plt.savefig(image_file_before, bbox_inces='tight', dpi=inputdpi)
    print "image saved as {}".format(image_file_before)
    
    if len(sys.argv) > 3:
        cm = plt.get_cmap('gist_rainbow')
        output_file = sys.argv[3]
        fo = open(output_file, "r")
        # Load and print clusters
        clusters = pickle.load(fo)
        reverse_mapping_dict = {}
        NUM_COLORS = len(clusters) + 1
        count = 1
        for cls in clusters:
            #print "Cluster-{} Nodes:{} {}".format(count, len(cls), cls)
            print "Cluster-{} Nodes:{}".format(count, len(cls))
            for node in cls:
                reverse_mapping_dict[node] = cm(1.*count/NUM_COLORS)
            #print cm(1.*count/NUM_COLORS)
            count += 1
        exit(1)
        
        # Generate colors for each cluster
        color_array = []
        for node in nodes:
            color_array.append(reverse_mapping_dict[str(node)])
        nx.draw_networkx_nodes(graph, position, node_size=10, node_color=color_array, vmin=0, vmax=10, linewidths=0.6, cmap='RdYlGn')
        nx.draw_networkx_edges(graph, position, alpha=0.2)
        plt.savefig(image_file_after, bbox_inces='tight', dpi=inputdpi)
        print "image saved as {}".format(image_file_after)

    return

if __name__ == "__main__":
    main()
