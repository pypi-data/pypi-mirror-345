"""
Rewrite list types to tuple or scalar types depending on how they are used.
"""
from dataclasses import dataclass, field
from typing import List, cast

from relationalai.early_access.metamodel import ir, visitor, compiler

@dataclass
class RewriteListTypes(compiler.Pass):
    """
    Rewrite list types to tuple or scalar types depending on how they are used.
    """
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        v = RewriteListTypesVisitor()
        result = v.walk(model)
        return result

@dataclass
class RewriteListTypesVisitor(visitor.DeprecatedPass):
    """
    A pass that fixes the types of Aggregate nodes, replacing lists with tuples of the correct length.
    """
    new_relations: List[ir.Relation] = field(default_factory=list, init=False)
    new_types: List[ir.Type] = field(default_factory=list, init=False)

    def handle_model(self, model: ir.Model, parent: None):
        result = super().handle_model(model, parent)
        return model.reconstruct(
            result.engines,
            result.relations | self.new_relations,
            result.types | self.new_types,
            result.root,
            result.annotations,
        )

    def handle_lookup(self, node: ir.Lookup, parent: ir.Node):
        if len(node.relation.fields) != len(node.args):
            return node

        # Handle the simple varargs case: one list field and all the rest are scalar.
        # Currently this pattern is only used for `rel_primitive_hash_tuple`.
        # and `rel_primitive_solverlib_fo_appl`.
        list_field_indexes = [i for i in range(len(node.relation.fields)) if isinstance(node.relation.fields[i].type, ir.ListType)]
        if len(list_field_indexes) == 1:
            # There exactly one list field, rewrite it to a tuple type.
            i = list_field_indexes[0]
            assert isinstance(node.relation.fields[i].type, ir.ListType)
            scalar_field_count = len(node.relation.fields) - 1
            tuple_len = len(node.args) - scalar_field_count
            if tuple_len >= 0:
                # Flatten the list field into separate scalar fields.
                f = node.relation.fields[i]
                ft = cast(ir.ListType, f.type)
                new_fields = (
                    list(node.relation.fields[0:i]) +
                    [ir.Field(f"{f.name}@{j}", ft.element_type, f.input) for j in range(tuple_len)] +
                    list(node.relation.fields[i+1:])
                )
                new_relation = ir.Relation(node.relation.name, tuple(new_fields), node.relation.requires, node.relation.annotations)
                self.new_relations.append(new_relation)
                return ir.Lookup(node.engine, new_relation, node.args)

        return node

    def handle_aggregate(self, node: ir.Aggregate, parent: ir.Node):
        if len(node.aggregation.fields) < 3:
            return node

        projection_field = node.aggregation.fields[0]
        group_field = node.aggregation.fields[1]
        changed = False

        if isinstance(projection_field.type, ir.ListType):
            new_type = ir.TupleType(tuple([projection_field.type.element_type] * len(node.projection)))
            self.new_types.append(new_type)
            changed = True
            projection_field = ir.Field(
                projection_field.name,
                new_type,
                projection_field.input,
            )

        if isinstance(group_field.type, ir.ListType):
            new_type = ir.TupleType(tuple([group_field.type.element_type] * len(node.group)))
            self.new_types.append(new_type)
            changed = True
            group_field = ir.Field(
                group_field.name,
                new_type,
                group_field.input,
            )

        if changed:
            new_aggregation = ir.Relation(
                node.aggregation.name,
                tuple([projection_field, group_field] + list(node.aggregation.fields[2:])),
                node.aggregation.requires,
                node.aggregation.annotations,
            )
            self.new_relations.append(new_aggregation)

            return ir.Aggregate(
                node.engine,
                new_aggregation,
                node.projection,
                node.group,
                node.args,
            )

        return node