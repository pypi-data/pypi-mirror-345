import networkx as nx
import matplotlib.pyplot as mpl_p
from itertools import product


def set_graph(n=4, kind="circular"):
    if kind == "linear":
        return linear_graph(n)
    elif kind == "circular":
        return circular_graph(n)


def linear_graph(n=4):
    graph = nx.Graph()
    graph.add_nodes_from([i for i in range(n)])
    graph.add_edges_from([[i, i+1] for i in range(n-1)])
    return graph


def circular_graph(n=4):
    graph = nx.Graph()
    graph.add_nodes_from([i for i in range(n)])
    graph.add_edges_from([[i, (i+1)%n] for i in range(n)])
    return graph


def draw_graph(graph, with_labels=True):
    nx.draw(graph, with_labels=with_labels)
    mpl_p.show()
