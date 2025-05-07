from __future__ import annotations

from typing import Optional, Sequence as PySequence, cast

from relationalai.early_access.metamodel import ir, compiler as c, factory as f, types, util
from relationalai.early_access.metamodel.helpers import collect_implicit_vars

class Splinter(c.Pass):
    """
    Splits multi-headed rules into multiple rules. Additionally, infers missing Exists tasks.
    """
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        if isinstance(model.root, ir.Logical):
            final = []
            new_relations:list[ir.Relation] = []
            new_relations.extend(model.relations)
            for child in model.root.body:
                new_logicals, relation = self.split(cast(ir.Logical, child))
                final.extend(new_logicals)
                if relation:
                    new_relations.append(relation)
            return ir.Model(
                    model.engines,
                    util.FrozenOrderedSet.from_iterable(new_relations),
                    model.types,
                    ir.Logical(
                        model.root.engine,
                        model.root.hoisted,
                        tuple(final)
                    )
                )
        return model

    def split(self, node: ir.Logical) -> tuple[list[ir.Logical], Optional[ir.Relation]]:
        # Split this logical, which represents a rule, into potentially many logicals, one
        # for each head (update or output)
        effects, body = self.split_items(node.body)
        if not body:
            return [node], None

        effects_vars = collect_implicit_vars(*effects)
        implicit_vars = list(collect_implicit_vars(*body) - effects_vars)
        has_aggregate = any(isinstance(t, ir.Aggregate) for t in body)

        if len(effects) > 1:
            connection = f.relation(f"q{node.id}", [f.field("", types.Any) for v in effects_vars])
            if implicit_vars:
                assert False, "Should be unreachable"
                args = [f.exists(implicit_vars, f.logical(body))]
            else:
                args = body
            final:list[ir.Logical] = [f.logical([*args, f.derive(connection, list(effects_vars))])]
            for effect in effects:
                effect_vars = collect_implicit_vars(effect)
                lookup_vars = [(v if v in effect_vars else f.wild()) for v in effects_vars]
                final.append(f.logical([f.lookup(connection, lookup_vars), effect]))
            return final, connection

        if has_aggregate and implicit_vars:
            assert False, "Should be unreachable"
            # the implicit_vars must be in a new logical at the same level as the aggregations,
            # so that they are pushed inside the body
            aggs = util.filter_by_type(body, ir.Aggregate)
            for a in aggs:
                body.remove(a)
            return [f.logical([
                f.logical([
                    f.logical([
                        f.exists(implicit_vars, f.logical(body))
                    ]),
                   *aggs
                ]),
                *effects
            ])], None
        elif implicit_vars:
            if any(v.name != '_' for v in implicit_vars):
                assert False, "Should be unreachable"
            # add an exists for the implicit vars
            return [f.logical([f.exists(implicit_vars, f.logical(body)), *effects])], None
        else:
            return [node], None


    def split_items(self, items: PySequence[ir.Task]) -> tuple[list[ir.Task], list[ir.Task]]:
        effects = []
        body = []
        for item in items:
            if isinstance(item, (ir.Update, ir.Output)):
                effects.append(item)
            else:
                body.append(item)
        return effects, body
