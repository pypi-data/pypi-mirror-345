"""
Helpers to generate Rel, many taken from the original PyRel implementation.
"""
from __future__ import annotations
import re
from relationalai.early_access.metamodel import ir, types, factory as f

# Rel primitive relations used by the compiler
# TODO: how to deal with varargs?
RelPrimitiveOuterJoin = f.relation("rel_primitive_outer_join", [])

# Mapping of IR operators to the equivalent in Rel
OPERATORS = {
    # binary
    # TODO: maybe add the binary operators

    # aggregates
    "count": "std::common::count",
    "sum": "std::common::sum",
    "avg": "std::common::mean",
    "max": "std::common::max",
    "min": "std::common::min",
}

def rel_operator(ir_op):
    """ Maps an operator from the metamodel IR into the equivalent Rel operator."""
    if ir_op in OPERATORS:
        return OPERATORS[ir_op]
    else:
        return ir_op

def rel_typename(ir_type: ir.Type):
    """ Get the name of the type to use in Rel. """
    if isinstance(ir_type, (ir.ListType, ir.SetType)):
        return rel_typename(ir_type.element_type)
    elif isinstance(ir_type, ir.ScalarType):
        if types.is_builtin(ir_type):
            return ir_type.name
        elif ir_type.super_types:
            # assuming the compiler narrowed this down somehow
            return rel_typename(ir_type.super_types.some())
        else:
            # user-defined types without a super type are user defined entities
            return 'UInt128'
    else:
        # TODO: how should we deal with Union types here?
        return 'Any'

# SEE: REL:      https://docs.relational.ai/rel/ref/lexical-symbols#keywords
#      CORE REL: https://docs.google.com/document/d/12LUQdRed7P5EqQI1D7AYG4Q5gno9uKqy32i3kvAWPCA
RESERVED_WORDS = [
    "and",
    "as",
    "bound",
    "declare",
    "def",
    "else",
    "end",
    "entity",
    "exists",
    "false",
    "for",
    "forall",
    "from",
    "ic",
    "if",
    "iff",
    "implies",
    "in",
    "module",
    "namespace",
    "not",
    "or",
    "requires",
    "then",
    "true",
    "use",
    "where",
    "with",
    "xor"
]

rel_sanitize_re = re.compile(r'[^\w:\[\]\^" ,]|^(?=\d)', re.UNICODE)
unsafe_symbol_pattern = re.compile(r"[^a-zA-Z0-9_]", re.UNICODE)

def sanitize(input_string, is_rel_name_or_symbol = False):
    # Replace non-alphanumeric characters with underscores
    if is_rel_name_or_symbol and "[" in input_string:
        string_parts = input_string.split('[', 1)
        sanitized_name_or_symbol = sanitize_identifier(string_parts[0])
        sanitized_rest = re.sub(rel_sanitize_re, "_", string_parts[1])
        sanitized = f"{sanitized_name_or_symbol}[{sanitized_rest}"
    else:
        if "::" in input_string: # TODO: This is a temp solution to avoid sanitizing the namespace
            sanitized = re.sub(rel_sanitize_re, "_", input_string)
        else:
            sanitized = sanitize_identifier(input_string)

    # Check if the resulting string is a keyword and append an underscore if it is
    if sanitized in RESERVED_WORDS:
        sanitized += "_"

    return sanitized

def sanitize_identifier(name: str) -> str:
    """
    Return a string safe to use as a top level identifier in rel, such as a variable or relation name.

    Args:
        name (str): The input identifier string.

    Returns:
        str: The sanitized identifier string.
    """

    if not name:
        return name

    safe_name = ''.join(c if c.isalnum() else '_' for c in name)
    if safe_name[0].isdigit():
        safe_name = '_' + safe_name
    if  safe_name in RESERVED_WORDS:
        safe_name = safe_name + "_" # preferring the pythonic pattern of `from_` vs `_from`
    return safe_name
