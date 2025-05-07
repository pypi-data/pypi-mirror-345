from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel import ir, builtins as rel_builtins, factory as f, typer
from typing import cast, Tuple
from relationalai.early_access.metamodel.util import NameCache

from relationalai.early_access.metamodel.rewrite import Splinter, RewriteListTypes, GCUnusedRelations

# TODO: Move this into metamodel.rewrite
from relationalai.early_access.rel.rewrite import Flatten, QuantifyVars

def lqp_passes() -> list[Pass]:
    # TODO: are these all needed from the Rel emitter?
    # TODO: should there be a pass to remove aliases from output?
    return [
        RewriteListTypes(),
        GCUnusedRelations(),
        typer.Checker(),
        typer.Typer(),
        GCUnusedRelations(),
        Flatten(),
        QuantifyVars(),
        Splinter(), # Adds missing existentials + splits multi-headed rules into single rules
        NormalizeAggregates(),
        HoistAggregates(),
        UnifyDefinitions(),
    ]

# TODO: assert theres no nested nested nested aggregates
# TODO: assert theres only one aggregate per rule
# TODO: is this correct?
# Move aggregates to the same level as updates (i.e. top-level logical)
class HoistAggregates(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            new_subsubtasks = []
            for subsubtask in subtask.body:
                if not isinstance(subsubtask, ir.Logical):
                    new_subsubtasks.append(subsubtask)
                    continue

                subsubtask = cast(ir.Logical, subsubtask)
                if self.has_aggregate(subsubtask):
                    new_subsubtask, aggrs = self._hoist_aggregates(subsubtask)
                    new_subsubtasks.append(new_subsubtask)
                    new_subsubtasks.extend(aggrs)
                else:
                    new_subsubtasks.append(subsubtask)

            new_subtask = ir.Logical(
                    subtask.engine,
                    subtask.hoisted,
                    tuple(new_subsubtasks),
                )
            new_subtasks.append(new_subtask)

        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations,
            model.types,
            new_root,
        )
        return model

    def has_aggregate(self, task: ir.Task) -> bool:
        assert isinstance(task, ir.Logical)
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                return True
        return False

    def _hoist_aggregates(self, task: ir.Task) -> Tuple[ir.Task, list[ir.Aggregate]]:
        assert isinstance(task, ir.Logical)
        aggrs = []
        new_subtasks = []
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                aggrs.append(subtask)
            else:
                new_subtasks.append(subtask)
        assert len(aggrs) > 0, "should have found an aggregate"
        return (ir.Logical(
            task.engine,
            task.hoisted,
            tuple(new_subtasks),
        ), aggrs)

# Rewrites aggregates when necessary e.g. avg -> sum/count
class NormalizeAggregates(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        self.var_name_cache: NameCache = NameCache()
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            if self.has_aggregate(subtask):
                new_subtask = self._rewrite_subtask(subtask)
                new_subtasks.append(new_subtask)
            else:
                new_subtasks.append(subtask)
        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations,
            model.types,
            new_root,
        )
        return model

    def _rewrite_subtask(self, task: ir.Task) -> ir.Task:
        assert isinstance(task, ir.Logical)
        new_subtasks = []
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                assert isinstance(subtask, ir.Aggregate)
                if subtask.aggregation.name == "sum":
                    new_subtasks.append(subtask)
                elif subtask.aggregation.name == "count":
                    new_subtasks.append(subtask)
                elif subtask.aggregation.name == "avg":
                    avg_task = self._make_avg(subtask)
                    new_subtasks.append(avg_task)
                else:
                    raise NotImplementedError(f"Unsupported aggregate: {subtask.aggregation.name}")
            else:
                new_subtasks.append(subtask)

        return ir.Logical(
            task.engine,
            task.hoisted,
            tuple(new_subtasks),
        )

    def _make_avg(self, task: ir.Aggregate) -> ir.Exists:
        assert isinstance(task, ir.Aggregate)
        assert task.aggregation.name == "avg"

        # TODO: confirm input args
        assert len(task.args) == 2
        input_arg = task.args[0]
        output_arg = task.args[1]
        assert isinstance(input_arg, ir.Var), f"expected var, got {type(input_arg)}: {input_arg}"
        assert isinstance(output_arg, ir.Var), f"expected var, got {type(output_arg)}: {output_arg}"

        new_sum_name = self.var_name_cache.get_name(input_arg.id, "sum")
        new_count_name = self.var_name_cache.get_name(input_arg.id, "count")
        new_sum = ir.Var(output_arg.type, new_sum_name)
        new_count = ir.Var(output_arg.type, new_count_name)

        sum_args = tuple([input_arg, new_sum])
        # Count doesn't have an 'over' argument
        count_args = tuple([input_arg, new_count])

        sum_task = ir.Aggregate(
            task.engine,
            rel_builtins.sum,
            task.projection,
            task.group,
            sum_args,
        )
        count_task = ir.Aggregate(
            task.engine,
            rel_builtins.count,
            task.projection,
            task.group,
            count_args,
        )

        final_result = ir.Lookup(
            task.engine,
            rel_builtins.div,
            tuple([new_sum, new_count, output_arg]),
        )

        body = ir.Logical(
            task.engine,
            tuple(),
            tuple([sum_task, count_task, final_result]),
        )

        return f.exists([new_sum, new_count], body)

    def has_aggregate(self, task: ir.Task) -> bool:
        assert isinstance(task, ir.Logical)
        for subtask in task.body:
            if isinstance(subtask, ir.Aggregate):
                return True
        return False

class UnifyDefinitions(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        multidef_relations = self.get_multidef_relations(model)
        for relation in multidef_relations:
            model = self.rename_multidef(model, relation)
        return model

    def get_multidef_relations(self, model: ir.Model) -> set[ir.Relation]:
        seen = set()
        result = set()
        root = cast(ir.Logical, model.root)
        for task in root.body:
            task = cast(ir.Logical, task)
            for subtask in task.body:
                if isinstance(subtask, ir.Output):
                    name = "output"
                    if name in seen:
                        raise NotImplementedError("multiple outputs not supported yet")
                    seen.add(name)
                elif isinstance(subtask, ir.Update):
                    assert subtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subtask.relation
                    if name in seen:
                        result.add(name)
                    seen.add(name)
        return result

    def rename_multidef(self, model: ir.Model, relation: ir.Relation) -> ir.Model:
        defname = relation.name
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        new_relations = []
        total_ct = 0
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            new_subsubtasks = []
            for subsubtask in subtask.body:
                if isinstance(subsubtask, ir.Update):
                    assert subsubtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subsubtask.relation
                    if name == relation:
                        total_ct += 1
                        # TODO: this needs to be unique btw (gensym)
                        new_name = f"{defname}_{total_ct}"
                        new_subsubtask = self.rename_relation(subsubtask, new_name)
                        new_subsubtasks.append(new_subsubtask)
                        new_relation = ir.Relation(
                            new_name,
                            relation.fields,
                            relation.requires,
                        )
                        new_relations.append(new_relation)
                    else:
                        new_subsubtasks.append(subsubtask)
                else:
                    new_subsubtasks.append(subsubtask)

            new_subtask = ir.Logical(
                subtask.engine,
                subtask.hoisted,
                tuple(new_subsubtasks),
            )
            new_subtasks.append(new_subtask)
        assert total_ct > 0, f"should have found at least one definition for {defname}"

        args = []
        for field in relation.fields:
            args.append(ir.Var(field.type, field.name))

        # Also add the new definition
        final_relation = ir.Relation(
            defname,
            relation.fields,
            relation.requires,
        )
        new_update = ir.Update(
            root.engine,
            final_relation,
            tuple(args),
            ir.Effect.derive,
        )

        logical_tasks = []
        lookups = []
        for new_relation in new_relations:
            new_lookup = ir.Lookup(
                root.engine,
                new_relation,
                tuple(args),
            )
            lookups.append(new_lookup)

        disj = ir.Union(
            root.engine,
            tuple(),
            tuple(lookups),
        )
        logical_tasks.append(disj)
        logical_tasks.append(new_update)
        new_logical = ir.Logical(
            root.engine,
            root.hoisted,
            tuple(logical_tasks),
        )
        new_subtasks.append(new_logical)

        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations | new_relations,
            model.types,
            new_root,
        )
        return model

    def rename_relation(self, task: ir.Update, new_name: str) -> ir.Update:
        assert isinstance(task, ir.Update)
        assert task.effect == ir.Effect.derive, "only derive updates supported yet"
        old_relation = task.relation
        new_relation = ir.Relation(
            new_name,
            old_relation.fields,
            old_relation.requires,
        )
        new_task = ir.Update(
            task.engine,
            new_relation,
            task.args,
            task.effect,
        )
        return new_task
