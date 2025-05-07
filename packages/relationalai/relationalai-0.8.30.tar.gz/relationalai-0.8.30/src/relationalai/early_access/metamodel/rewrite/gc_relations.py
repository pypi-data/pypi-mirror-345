"""
Garbage collection pass that removes unused types and relations from the model.
"""
from dataclasses import dataclass

from relationalai.early_access.metamodel import ir, visitor, compiler


@dataclass
class GCUnusedRelations(compiler.Pass):
    """
    A pass that removes unused types and relations from the model.
    """
    def rewrite(self, model: ir.Model, cache=None) -> ir.Model:
        relations = visitor.collect_by_type(ir.Relation, *model.engines, model.root, *model.annotations)
        types = visitor.collect_by_type(ir.Type, *model.engines, *relations, model.root, *model.annotations)
        return ir.Model(
            model.engines,
            relations.frozen(),
            types.frozen(),
            model.root,
            model.annotations,
        )