
from __future__ import annotations
from relationalai.early_access.metamodel import types, factory as f

# Rel Annotations as IR Relations (to be used in IR Annotations)
arrow = f.relation("no_inline", [])
no_diagnostics = f.relation("no_diagnostics", [f.field("code", types.Symbol)])
no_inline = f.relation("no_inline", [])
# inner_loop_non_stratified

annotations = [
    arrow,
    no_diagnostics,
    no_inline,
]
