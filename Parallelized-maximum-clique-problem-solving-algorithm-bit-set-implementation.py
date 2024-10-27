import threading

class Graph:
    def __init__(self, num_vertices):
        self.N = num_vertices
        self.adj = [0] * self.N

    def add_edge(self, u, v):
        self.adj[u] |= 1 << v
        self.adj[v] |= 1 << u

def bitset_iter(bitset):
    while bitset:
        v = (bitset & -bitset).bit_length() - 1
        yield v
        bitset &= bitset - 1

def bron_kerbosch(R, P, X, adj, cliques):
    if P == 0 and X == 0:
        cliques.append(R)
        return
    for v in bitset_iter(P):
        N_v = adj[v]
        bron_kerbosch(R | (1 << v), P & N_v, X & N_v, adj, cliques)
        P &= ~(1 << v)
        X |= 1 << v

def parallel_bron_kerbosch(graph):
    cliques = []
    P = (1 << graph.N) - 1
    X = 0
    threads = []
    lock = threading.Lock()

    def worker(v):
        nonlocal P, X
        R = 1 << v
        N_v = graph.adj[v]
        local_cliques = []
        bron_kerbosch(R, P & N_v, X & N_v, graph.adj, local_cliques)
        with lock:
            cliques.extend(local_cliques)
        with lock:
            P &= ~(1 << v)
            X |= 1 << v

    for v in range(graph.N):
        t = threading.Thread(target=worker, args=(v,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return cliques

# example
graph = Graph(5)
edges = [(0,1), (0,2), (1,2), (1,3), (2,3), (3,4)]
for u, v in edges:
    graph.add_edge(u, v)

cliques = parallel_bron_kerbosch(graph)
print("max clique：")
for clique in cliques:
    nodes = [i for i in range(graph.N) if clique & (1 << i)]
    print(nodes)