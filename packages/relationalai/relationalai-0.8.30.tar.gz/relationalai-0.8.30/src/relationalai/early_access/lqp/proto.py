from typing import Union

from . import ir

from relationalai.lqp.v1 import logic_pb2, fragments_pb2, transactions_pb2

# pyright complains that *_pb2.Whatever is not a known attribute, so
# extract the classes with getattr.
__pb_Transaction = getattr(transactions_pb2, "Transaction")
__pb_Define = getattr(transactions_pb2, "Define")
__pb_Write = getattr(transactions_pb2, "Write")
__pb_Output = getattr(transactions_pb2, "Output")
__pb_Read = getattr(transactions_pb2, "Read")
__pb_Epoch = getattr(transactions_pb2, "Epoch")
__pb_Read = getattr(transactions_pb2, "Read")

__pb_Fragment = getattr(fragments_pb2, "Fragment")
__pb_FragmentId = getattr(fragments_pb2, "FragmentId")

__pb_Declaration = getattr(logic_pb2, "Declaration")
__pb_Def = getattr(logic_pb2, "Def")
__pb_Loop = getattr(logic_pb2, "Loop")
__pb_LoopIndex = getattr(logic_pb2, "LoopIndex")
__pb_Attribute = getattr(logic_pb2, "Attribute")
__pb_Abstraction = getattr(logic_pb2, "Abstraction")
__pb_Term = getattr(logic_pb2, "Term")
__pb_Var = getattr(logic_pb2, "Var")
__pb_Constant = getattr(logic_pb2, "Constant")
__pb_Formula = getattr(logic_pb2, "Formula")
__pb_Exists = getattr(logic_pb2, "Exists")
__pb_Reduce = getattr(logic_pb2, "Reduce")
__pb_Conjunction = getattr(logic_pb2, "Conjunction")
__pb_Disjunction = getattr(logic_pb2, "Disjunction")
__pb_Not = getattr(logic_pb2, "Not")
__pb_FFI = getattr(logic_pb2, "FFI")
__pb_Atom = getattr(logic_pb2, "Atom")
__pb_RelAtom = getattr(logic_pb2, "RelAtom")
__pb_Pragma = getattr(logic_pb2, "Pragma")
__pb_Primitive = getattr(logic_pb2, "Primitive")
__pb_True = getattr(logic_pb2, "True")
__pb_False = getattr(logic_pb2, "False")
__pb_RelationId = getattr(logic_pb2, "RelationId")
__pb_PrimitiveValue = getattr(logic_pb2, "PrimitiveValue")
__pb_PrimitiveType = getattr(logic_pb2, "PrimitiveType")
__pb_RelType = getattr(logic_pb2, "RelType")

# Converts an LQP program to an LQP proto Transaction.
def lqp_program_to_proto(program: ir.LqpProgram):
    return __pb_Transaction(
        epochs = [
            __pb_Epoch(
                local_writes = [
                    __pb_Write(
                        define = __pb_Define(
                            fragment = __pb_Fragment(
                                id = __pb_FragmentId(id = bytes(404)),
                                declarations = [
                                    __as_declaration(lqp_node_to_proto(d)) for d in program.defs
                                ],
                            )
                        )
                    )
                ],
                reads = [
                    __pb_Read(
                        output = __pb_Output(
                            name = name,
                            relation_id = lqp_node_to_proto(rid),
                        )
                    ) for (name, rid) in program.outputs
                ],
            )
        ],
    )

TermOption = Union[__pb_Var, __pb_Constant]
# Creates a proto Term out of termish (an option for Term).
def __as_term(termish: TermOption):
    pb_term = __pb_Term()
    if isinstance(termish, __pb_Var):
        pb_term.var.CopyFrom(termish)
    else:
        assert isinstance(termish, __pb_Constant)
        pb_term.constant.CopyFrom(termish)

    return pb_term

FormulaOption = Union[
    __pb_Exists, __pb_Reduce, __pb_Conjunction, __pb_Disjunction, __pb_Not,
    __pb_FFI, __pb_Atom, __pb_Pragma, __pb_Primitive, __pb_True, __pb_False,
]
# Creates a proto Formula out of formulaish (an option for Formula).
def __as_formula(formulaish: FormulaOption):
    pb_formula = __pb_Formula()
    if isinstance(formulaish, __pb_Exists):
        pb_formula.exists.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Reduce):
        pb_formula.reduce.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Conjunction):
        pb_formula.conjunction.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Disjunction):
        pb_formula.disjunction.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Not):
        setattr(pb_formula, "not", formulaish)
    elif isinstance(formulaish, __pb_FFI):
        pb_formula.ffi.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Atom):
        pb_formula.atom.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_RelAtom):
        pb_formula.rel_atom.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Pragma):
        pb_formula.pragma.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_Primitive):
        pb_formula.primitive.CopyFrom(formulaish)
    elif isinstance(formulaish, __pb_True):
        pb_formula.true_val.CopyFrom(formulaish)
    else:
        assert isinstance(formulaish, __pb_False)
        pb_formula.true_val.CopyFrom(formulaish)

    return pb_formula

DeclarationOption = Union[__pb_Def, __pb_Loop]
# Creates a proto Declaration out of declarationish (an option for Declaration).
def __as_declaration(declarationish: DeclarationOption):
    pb_declaration = __pb_Declaration()
    if isinstance(declarationish, __pb_Def):
        getattr(pb_declaration, "def").CopyFrom(declarationish)
    else:
        assert isinstance(declarationish, __pb_Loop)
        pb_declaration.loop.CopyFrom(declarationish)

    return pb_declaration

# Produce proto out of LQP node recursively.
# TODO: should PrimitiveType be an LqpNode?
def lqp_node_to_proto(node: Union[ir.LqpNode, ir.PrimitiveType]):
    if isinstance(node, ir.Def):
        return __pb_Def(
            name = lqp_node_to_proto(node.name),
            body = lqp_node_to_proto(node.body),
            attrs = [lqp_node_to_proto(attr) for attr in node.attrs]
        )

    # elif isinstance(node, Declaration):
    #     Ignore: we match on the "concrete" children of Declaration.

    elif isinstance(node, ir.Loop):
        return __pb_Loop(
            temporal_var = __pb_LoopIndex(node.temporal_var),
            inits = [lqp_node_to_proto(init) for init in node.inits],
            body = lqp_node_to_proto(node.body),
        )

    elif isinstance(node, ir.Abstraction):
        return __pb_Abstraction(
            vars = [lqp_node_to_proto(var) for var in node.vars],
            value = __as_formula(lqp_node_to_proto(node.value)),
        )

    # elif isinstance(node, ir.Formula):
    #     Ignore: we match on the "concrete" children of Formula.

    elif isinstance(node, ir.Exists):
        return __pb_Exists(
            body = lqp_node_to_proto(node.body)
        )

    elif isinstance(node, ir.Reduce):
        return __pb_Reduce(
            op = lqp_node_to_proto(node.op),
            body = lqp_node_to_proto(node.body),
            terms = [__as_term(lqp_node_to_proto(term)) for term in node.terms],
        )

    elif isinstance(node, ir.Conjunction):
        return __pb_Conjunction(
            args = [__as_formula(lqp_node_to_proto(arg)) for arg in node.args],
        )

    elif isinstance(node, ir.Disjunction):
        return __pb_Disjunction(
            args = [__as_formula(lqp_node_to_proto(arg)) for arg in node.args],
        )

    elif isinstance(node, ir.Not):
        return __pb_Not(
            arg = __as_formula(lqp_node_to_proto(node.arg))
        )

    elif isinstance(node, ir.Ffi):
        return __pb_FFI(
            name = node.name,
            args = [lqp_node_to_proto(arg) for arg in node.args],
            terms = [__as_term(lqp_node_to_proto(term)) for term in node.terms]
        )

    elif isinstance(node, ir.Atom):
        return __pb_Atom(
            name = lqp_node_to_proto(node.name),
            terms = [__as_term(lqp_node_to_proto(term)) for term in node.terms],
        )

    elif isinstance(node, ir.Pragma):
        return __pb_Pragma(
            name = node.name,
            terms = [__as_term(lqp_node_to_proto(term)) for term in node.terms],
        )

    elif isinstance(node, ir.Primitive):
        return __pb_Primitive(
            name = node.name,
            terms = [__as_term(lqp_node_to_proto(term)) for term in node.terms],
        )

    elif isinstance(node, ir.JustTrue):
        return __pb_True()

    elif isinstance(node, ir.JustFalse):
        return __pb_False()

    elif isinstance(node, ir.RelAtom):
        return __pb_RelAtom(
            name = node.name,
            terms = [__as_term(lqp_node_to_proto(term)) for term in node.terms],
        )

    # elif isinstance(node, ir.Term):
    #     Ignore: we match on the "concrete" children of Term.

    elif isinstance(node, ir.Var):
        return __pb_Var(
            name = node.name,
            type = lqp_type_to_proto(node.type),
        )

    elif isinstance(node, ir.Constant):
        # To put inside the constant.
        pb_primitive_value = __pb_PrimitiveValue()
        if isinstance(node.value, str):
            pb_primitive_value.string_value = node.value
        elif isinstance(node.value, int):
            pb_primitive_value.int_value = node.value
        elif isinstance(node.value, float):
            pb_primitive_value.float_value = node.value
        else:
            raise NotImplementedError(
                f"Proto transformation not implemented for {type(node.value)}."
            )
        return __pb_Constant(value = pb_primitive_value)

    elif isinstance(node, ir.Attribute):
        return __pb_Attribute(
            name = node.name,
            args = [lqp_node_to_proto(arg) for arg in node.args],
        )

    elif isinstance(node, ir.RelationId):
        return __pb_RelationId(
            id_low = 0x0000000000000000ffffffffffffffff & node.id,
            id_high = node.id >> 64,
        )

    else:
        raise NotImplementedError(
            f"Proto transformation not implemented for {type(node)}."
        )

def lqp_primitive_to_proto(node: ir.PrimitiveType):
    if node == ir.PrimitiveType.STRING:
        return __pb_PrimitiveType.PRIMITIVE_TYPE_STRING
    elif node == ir.PrimitiveType.INT:
        return __pb_PrimitiveType.PRIMITIVE_TYPE_INT
    elif node == ir.PrimitiveType.FLOAT:
        return __pb_PrimitiveType.PRIMITIVE_TYPE_FLOAT
    elif node == ir.PrimitiveType.UINT128:
        return __pb_PrimitiveType.PRIMITIVE_TYPE_UINT128
    elif node == ir.PrimitiveType.UNKNOWN:
        # TODO: this is wrong
        return __pb_PrimitiveType.PRIMITIVE_TYPE_INT
    else:
        raise NotImplementedError(
            f"Proto transformation not implemented for {node}."
        )

def lqp_type_to_proto(node: ir.RelType):
    if isinstance(node, ir.PrimitiveType):
        return __pb_RelType(
            primitive_type = lqp_primitive_to_proto(node)
        )

    elif isinstance(node, ir.ValueType):
        raise NotImplementedError(
            f"Proto transformation not implemented for {type(node)}."
        )
    else:
        raise NotImplementedError(
            f"Proto transformation not implemented for {type(node)}."
        )
