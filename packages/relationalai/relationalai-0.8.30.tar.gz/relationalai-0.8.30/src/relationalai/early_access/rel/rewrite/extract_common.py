from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from relationalai.early_access.metamodel import ir, factory as f, helpers
from relationalai.early_access.metamodel.compiler import Pass, group_tasks
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.rel import metamodel_utils
from relationalai.early_access.rel.rewrite import flatten
from relationalai.early_access.rel.dependency import AnalysisContext, Frame, ctx_frame

class ExtractCommon(Pass):
    """
    Pass to analyze Logical bodies and extract lookups in their own Logical if it makes
    sense. The heuristic is that, if there are multiple lookups, and there are also multiple
    sibling nested logicals that will eventually be extracted by Flatten, then it makes
    sense to extract these logicals into their own "rule", and then make the original body
    just lookup this common rule.

    From:
        Logical
            Logical
                lookup1
                lookup2
                Logical1 ...
                Logical2 ...
    To:
        Logical
            Logical
                lookup1
                lookup2
                derive common
            Logical
                lookup common
                Logical1 ...
                Logical2 ...
    """

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        # create the dependency analysis context
        ctx = AnalysisContext(model.root)

        # rewrite the root
        replacement = self.handle(model.root, ctx)

        # the new root contains the extracted top level logicals and the rewritten root
        if ctx.top_level:
            new_root = ir.Logical(model.root.engine, tuple(), tuple(ctx.top_level + [replacement]))
        else:
            new_root = replacement

        # create the new model, updating relations and root
        return ir.Model(
            model.engines,
            OrderedSet.from_iterable(model.relations).update(ctx.relations).frozen(),
            model.types,
            new_root
        )

    #--------------------------------------------------
    # IR handlers
    #--------------------------------------------------

    def handle(self, task: ir.Task, ctx: AnalysisContext):
        # currently we only extract if it's a sequence of Logicals, but we could in the
        # future support other intermediate nodes
        if isinstance(task, ir.Logical):
            return self.handle_logical(task, ctx)
        else:
            return task

    def handle_logical(self, task: ir.Logical, ctx: AnalysisContext):
        # create frame to process the children
        with ctx_frame(ctx, task) as frame:
            # process the original body
            groups = group_tasks(task.body, {
                "binders": helpers.BINDERS,
                "composites": helpers.COMPOSITES
            })
            composites = groups["composites"]

            # the new body of the rewritten task
            body:OrderedSet[ir.Task] = ordered_set()

            # quick check to see if it's worth doing more analysis; we only want to extract
            # common binders if there are multiple, and there are also multiple composites
            # that will be extracted by the flatten pass later (so that they can share the
            # extracted logic).
            plan = None
            if len(groups["binders"]) > 1 and len(composites) > 1:
                extractables = flatten.extractables(composites)
                # only makes sense to extract common if more than one nested composite will be extracted
                if len(extractables) > 1:
                    # make a plan to extract common tasks from the logical
                    plan = self._create_extraction_plan(composites, extractables, frame)
                    if plan and len(plan.common_body) > 1:
                        # plan is worthwhile, extract the common body and add the connection to the body
                        exposed_vars = plan.exposed_vars.list
                        plan.common_reference = f.lookup(metamodel_utils.extract(task, plan.common_body, exposed_vars, ctx, "common"), exposed_vars)
                        # if we are not distributing the reference, add to the main body
                        if not plan.distribute_common_reference:
                            body.add(plan.common_reference)

            # recursively handle children
            for child in task.body:
                # skip children that were extracted
                if plan and child in plan.common_body:
                    continue

                # no plan or child is not a composite, so just add the handled to the body
                if not plan or child not in composites:
                    body.add(self.handle(child, ctx))
                    continue

                # there is a plan and the child is in composites, so...
                replacement = self.handle(child, ctx)
                # this child needs either extra local dependencies or the common reference
                if child in plan.local_dependencies or plan.distribute_common_reference:
                    # the new body will have maybe the common reference and the local deps
                    replacement_body = ordered_set()
                    if plan.distribute_common_reference:
                        replacement_body.add(plan.common_reference)
                    if child in plan.local_dependencies:
                        replacement_body.update(plan.local_dependencies[child])

                    if isinstance(replacement, ir.Logical):
                        # if the replacements is a logical, we can just add to the body
                        body.add(replacement.reconstruct(
                            replacement.engine, replacement.hoisted,
                            tuple(replacement_body.update(replacement.body).list),
                            replacement.annotations
                        ))
                    else:
                        # anything else is now wrapped in a logical so that we can add the
                        # local dependencies
                        hoisted = replacement.hoisted if isinstance(replacement, helpers.COMPOSITES) else []
                        body.add(f.logical(replacement_body.add(replacement).list, hoisted, replacement.engine))
                else:
                    # child does not need extras in the body, just add it to the main body
                    body.add(replacement)

            return ir.Logical(task.engine, task.hoisted, tuple(body))

    @dataclass
    class ExtractionPlan():
        # tasks to extract to the body of the common logical
        common_body: OrderedSet[ir.Task]
        # variables to be exposed by the common logical
        exposed_vars: OrderedSet[ir.Var]
        # map from nested composite to the tasks in the common body that still need to be
        # included in its body, because it contains variables not exposed by the common logical
        local_dependencies: dict[ir.Task, OrderedSet[ir.Task]]
        # whether the common reference should be distributed to composites
        distribute_common_reference: bool
        # a reference to the common connection created for this plan, if any
        common_reference: Optional[ir.Task] = None



    def _create_extraction_plan(self, composites: OrderedSet[ir.Task], extractables: list[ir.Task], frame: Frame):
        """
        Compute a plan to extract tasks in this frame that are common dependencies
        across these composite tasks.
        """
        # compute intersection of task dependencies and inputs
        sample = composites.some()
        deps = frame.task_dependencies(sample)
        if deps is None:
            return None
        common_body = OrderedSet.from_iterable(deps)
        exposed_vars = OrderedSet.from_iterable(frame.task_inputs(sample))

        # now extract from the original sets
        for composite in composites:
            if composite == sample:
                continue

            # compute sibling dependencies
            for task in common_body:
                if task not in frame.task_dependencies(composite):
                    common_body.remove(task)
            # compute common input vars
            t_inputs = frame.task_inputs(composite)
            # exposed_vars.update(t_inputs)
            for v in exposed_vars:
                if v not in t_inputs:
                    exposed_vars.remove(v)

        # no vars in common, not worth to extract
        if not exposed_vars:
            return None

        # pull the transitive closure of the intersected tasks in the common body
        chasing = True
        while(chasing):
            chasing = False
            for task in common_body:
                for hop in frame.task_dependencies(task):
                    if isinstance(hop, helpers.BINDERS) and hop not in common_body:
                        common_body.add(hop)
                        chasing = True

        # for each composite, check if there are additional tasks needed, because the task
        # depends on it but it is not exposed by the vars
        local_dependencies: dict[ir.Task, OrderedSet[ir.Task]] = dict()
        for composite in composites:
            local = self._compute_local_dependencies(frame, composite, common_body, exposed_vars)
            if local:
                local_dependencies[composite] = local

        # distribute the common reference only if all of the composites are extractable
        return ExtractCommon.ExtractionPlan(common_body, exposed_vars, local_dependencies, len(extractables) == len(composites))

    def _compute_local_dependencies(self, frame: Frame, composite: ir.Task, common_body: OrderedSet[ir.Task], exposed_vars: OrderedSet[ir.Var]):
        """
        The tasks in common_body will be extracted into a logical that will expose the exposed_vars.
        Compute which additional dependencies are needed specifically to this composite, because
        it depends on some tasks that are extracted to common_body but not exposed by exposed_vars.
        """

        # vars exposed by exposed vars + tasks added to the local body
        vars_exposed = OrderedSet.from_iterable(exposed_vars)
        # working list of vars we still need to fulfill
        vars_needed = (frame.task_inputs(composite) - vars_exposed)
        if not vars_needed:
            return None

        # this is a greedy algorigthm that uses the first task in the common body that provides
        # a variable needed; it may result in sub-optimal extraction, but should be correct
        local_body = ordered_set()
        while(vars_needed):
            v = vars_needed.pop()
            for x in common_body:
                if x not in local_body:
                    # an x that is not yet in local_body can fulfill v
                    x_outputs = frame.task_outputs(x)
                    if v in x_outputs:
                        # add it to local_body and add its outputs to vars exposed
                        local_body.add(x)
                        vars_exposed.add(x_outputs)
                        # but add its inputs the vars now needed
                        vars_needed.update(frame.task_inputs(x) - vars_exposed)
        return local_body
