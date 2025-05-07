from .. import dsl
from ..std.graphs import unwrap

# --------------------------------------------------
# Ego network
# --------------------------------------------------
def ego_network(graph, node, hops):
    if not isinstance(hops, int):
        raise TypeError(f"'hops' must be an integer, got {type(hops).__name__} instead")
    elif hops < 0:
        raise ValueError(f"'hops' must be non-negative, got {hops}")

    a, b = dsl.create_vars(2)
    dsl.global_ns.graphlib_experimental.ego_network(graph, unwrap(node), hops, a, b)
    la = graph.compute._lookup(a)
    lb = graph.compute._lookup(b)
    return (la, lb)
