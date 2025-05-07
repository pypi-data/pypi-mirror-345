from relationalai.early_access.lqp import ir as lqp
from typing import Sequence
import hashlib


# TODO: this is NOT a good hash its just to get things working for now to get
# a stable id.

"""
Hashes an LQP node to a 128-bit integer.
"""
def lqp_hash(node) -> int:
    if isinstance(node, lqp.LqpNode):
        return hash_to_uint128(_lqp_hash(node))
    else:
        h = _lqp_hash_fn(node)
        return hash_to_uint128(h)

def _lqp_hash(node: lqp.LqpNode) -> int:
    if isinstance(node, lqp.Abstraction):
        h1 = _lqp_hash_list(node.vars)
        h2 = _lqp_hash(node.value)
        return _lqp_hash_fn((h1, h2))
    elif isinstance(node, lqp.Conjunction):
        h1 = _lqp_hash_list(node.args)
        return _lqp_hash_fn((h1,))
    elif isinstance(node, lqp.Var):
        return _lqp_hash_fn((node.name, node.type))
    elif isinstance(node, lqp.Constant):
        return _lqp_hash_fn((node.value,))
    elif isinstance(node, lqp.Primitive):
        h1 = _lqp_hash_fn(node.name)
        h2 = _lqp_hash_list(node.terms)
        return _lqp_hash_fn((h1, h2))
    elif isinstance(node, lqp.Reduce):
        h1 = _lqp_hash(node.op)
        h2 = _lqp_hash(node.body)
        h3 = _lqp_hash_list(node.terms)
        return _lqp_hash_fn((h1, h2, h3))
    elif isinstance(node, lqp.Atom):
        h1 = _lqp_hash(node.name)
        h2 = _lqp_hash_list(node.terms)
        return _lqp_hash_fn((h1, h2))
    elif isinstance(node, lqp.RelationId):
        return _lqp_hash_fn((node.id,))
    else:
        raise NotImplementedError(f"Unsupported LQP node type: {type(node)}")

# TODO: this is NOT a good hash its just to get things working for now to get
# a stable id.
def _lqp_hash_fn(node) -> int:
    return int.from_bytes(hashlib.sha256(str(node).encode()).digest(), byteorder='big', signed=False)

def _lqp_hash_list(node: Sequence[lqp.LqpNode]) -> int:
    hashes = [_lqp_hash(n) for n in node]
    return _lqp_hash_fn(tuple(hashes))

def hash_to_uint128(h: int) -> int:
    return h % (2**128)  # Ensure it's within the 128-bit range
