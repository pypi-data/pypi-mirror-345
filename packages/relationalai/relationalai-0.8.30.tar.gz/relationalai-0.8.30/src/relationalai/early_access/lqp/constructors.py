from relationalai.early_access.lqp import ir as lqp

def mk_and(args: list[lqp.Formula]) -> lqp.Formula:
    # Flatten nested conjunctions
    if any(isinstance(arg, lqp.Conjunction) for arg in args):
        final_args = []
        for arg in args:
            if isinstance(arg, lqp.Conjunction):
                final_args.extend(arg.args)
            else:
                final_args.append(arg)
        args = final_args

    if len(args) == 1:
        return args[0]

    return lqp.Conjunction(args)

def mk_or(args: list[lqp.Formula]) -> lqp.Formula:
    # Flatten nested disjunctions
    if any(isinstance(arg, lqp.Disjunction) for arg in args):
        final_args = []
        for arg in args:
            if isinstance(arg, lqp.Disjunction):
                final_args.extend(arg.args)
            else:
                final_args.append(arg)
        args = final_args

    if len(args) == 1:
        return args[0]

    return lqp.Disjunction(args)

def mk_abstraction(vars: list[lqp.Var], value: lqp.Formula) -> lqp.Abstraction:
    return lqp.Abstraction(vars, value)

def mk_exists(vars: list[lqp.Var], value: lqp.Formula) -> lqp.Formula:
    if len(vars) == 0:
        return value
    abstr = mk_abstraction(vars, value)
    return lqp.Exists(abstr)
