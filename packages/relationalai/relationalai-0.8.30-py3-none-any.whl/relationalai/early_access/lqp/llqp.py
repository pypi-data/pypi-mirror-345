from abc import ABC, abstractmethod
from typing import Union, Sequence

from colorama import Style, Fore

from . import ir

class StyleConfig(ABC):
    @abstractmethod
    def SIND(self, ) -> str: pass

    @abstractmethod
    def LPAREN(self, ) -> str: pass
    @abstractmethod
    def RPAREN(self, ) -> str: pass

    @abstractmethod
    def LBRACKET(self, ) -> str: pass
    @abstractmethod
    def RBRACKET(self, ) -> str: pass

    # String of level indentations for LLQP.
    @abstractmethod
    def indentation(self, level: int) -> str: pass

    # Styled keyword x.
    @abstractmethod
    def kw(self, x: str) -> str: pass

    # Styled user provided name, e.g. variables.
    @abstractmethod
    def uname(self, x: str) -> str: pass

    # Styled type annotation, e.g. ::INT.
    @abstractmethod
    def type_anno(self, x: str) -> str: pass

# Some basic components and how they are to be printed.
class Unstyled(StyleConfig):
    # Single INDentation.
    def SIND(self, ): return "    "

    def LPAREN(self, ): return "("
    def RPAREN(self, ): return ")"

    def LBRACKET(self, ): return "["
    def RBRACKET(self, ): return "]"

    # String of level indentations for LLQP.
    def indentation(self, level: int) -> str:
        return self.SIND() * level

    # Styled keyword x.
    def kw(self, x: str) -> str:
        return x

    # Styled user provided name, e.g. variables.
    def uname(self, x: str) -> str:
        return x

    # Styled type annotation, e.g. ::INT.
    def type_anno(self, x: str) -> str:
        return x

class Styled(StyleConfig):
    def SIND(self, ): return "    "

    def LPAREN(self, ): return Style.DIM + "(" + Style.RESET_ALL
    def RPAREN(self, ): return Style.DIM + ")" + Style.RESET_ALL

    def LBRACKET(self, ): return Style.DIM + "[" + Style.RESET_ALL
    def RBRACKET(self, ): return Style.DIM + "]" + Style.RESET_ALL

    def indentation(self, level: int) -> str:
        return self.SIND() * level

    def kw(self, x: str) -> str:
        return Fore.YELLOW + x + Style.RESET_ALL

    def uname(self, x: str) -> str:
        return Fore.WHITE + x + Style.RESET_ALL

    # Styled type annotation, e.g. ::INT.
    def type_anno(self, x: str) -> str:
        return Style.DIM + x + Style.RESET_ALL

# Call to_llqp on all nodes, each of which with indent_level, separating them
# by delim.
def list_to_llqp(nodes: Sequence[ir.LqpNode], indent_level: int, delim: str, styled: bool) -> str:
    return delim.join(map(lambda n: to_llqp(n, indent_level, styled), nodes))

# Produces "(terms term1 term2 ...)" (all on one line) indented at indent_level.
def terms_to_llqp(terms: Sequence[ir.Term], indent_level: int, styled: bool) -> str:
    conf = Styled() if styled else Unstyled()

    ind = conf.indentation(indent_level)

    llqp = ""
    if len(terms) == 0:
        llqp = ind + conf.LPAREN() + conf.kw("terms") + conf.RPAREN()
    else:
        llqp = ind + conf.LPAREN() + conf.kw("terms") + " " + list_to_llqp(terms, 0, " ", styled) + conf.RPAREN()

    return llqp

def program_to_llqp(node: ir.LqpProgram, styled: bool = True) -> str:
    conf = Styled() if styled else Unstyled()

    # TODO: is this true? and in general for the other things can they be missing?
    reads_portion = ""
    if len(node.outputs) == 0:
        reads_portion += conf.indentation(2) + conf.LPAREN() + conf.kw("reads") + conf.RPAREN() +" ;; no outputs" + "\n"
    else:
        reads_portion += conf.indentation(2) + conf.LPAREN() + conf.kw("reads") + "\n"

        for (name, rel_id) in node.outputs:
            reads_portion +=\
                f"{conf.indentation(3)}" +\
                conf.LPAREN() +\
                conf.kw("output") + " " +\
                f":{conf.uname(name)} " +\
                f"{to_llqp(rel_id, 0, styled)}" +\
                conf.RPAREN()

        reads_portion += conf.RPAREN()

    delim = "\n\n"
    writes_portion = f"{list_to_llqp(node.defs, 5, delim, styled)}"


    return\
    conf.indentation(0) + conf.LPAREN() + conf.kw("transaction") + "\n" +\
    conf.indentation(1) + conf.LPAREN() + conf.kw("epoch") + "\n" +\
    conf.indentation(2) + conf.LPAREN() + conf.kw("local_writes") + "\n" +\
    conf.indentation(3) + conf.LPAREN() + conf.kw("define") + "\n" +\
    conf.indentation(4) + conf.LPAREN() + conf.kw("fragment") + " " + conf.uname(":f1") + "\n" +\
    writes_portion +\
    conf.RPAREN() + conf.RPAREN() + conf.RPAREN() +\
    "\n" +\
    reads_portion +\
    conf.RPAREN() + conf.RPAREN()

def to_llqp(node: Union[ir.LqpNode, ir.PrimitiveType], indent_level: int, styled: bool = True) -> str:
    conf = Styled() if styled else Unstyled()

    ind = conf.indentation(indent_level)
    llqp = ""

    if isinstance(node, ir.Def):
        llqp += ind + conf.LPAREN() + conf.kw("def") + " " + to_llqp(node.name, 0, styled) + "\n"
        llqp += to_llqp(node.body, indent_level + 1, styled) + "\n"
        if len(node.attrs) == 0:
            llqp += ind + conf.SIND() + conf.LPAREN() + conf.kw("attrs") + conf.RPAREN() + conf.RPAREN()
        else:
            llqp += ind + conf.SIND() + conf.LPAREN() + conf.kw("attrs") + "\n"
            llqp += list_to_llqp(node.attrs, indent_level + 2, "\n", styled) + "\n"
            llqp += ind + conf.SIND() + conf.RPAREN() + conf.RPAREN()

    elif isinstance(node, ir.Loop):
        llqp += ind + conf.LPAREN() + conf.kw("loop") + node.temporal_var + "\n"
        llqp += ind + conf.SIND() + conf.LPAREN() + conf.kw("inits") + "\n"
        llqp += list_to_llqp(node.inits, indent_level + 2, "\n", styled) + "\n"
        llqp += ind + conf.SIND() + conf.RPAREN() + "\n"
        llqp += ind + conf.SIND() + conf.LPAREN() + conf.kw("body") + "\n"
        llqp += to_llqp(node.body, indent_level + 2, styled) + "\n"
        llqp += ind + conf.SIND() + conf.RPAREN() + conf.RPAREN()

    elif isinstance(node, ir.Abstraction):
        llqp += ind + conf.LPAREN() + conf.LBRACKET() + list_to_llqp(node.vars, 0, " ", styled) + conf.RBRACKET() + "\n"
        llqp += to_llqp(node.value, indent_level + 1, styled) + conf.RPAREN()

    elif isinstance(node, ir.Exists):
        llqp += ind + conf.LPAREN() + conf.kw("exists") + " " + conf.LBRACKET() + list_to_llqp(node.body.vars, 0, ", ", styled) + conf.RBRACKET() + "\n"
        llqp += to_llqp(node.body.value, indent_level + 1, styled) + conf.RPAREN()

    elif isinstance(node, ir.Reduce):
        llqp += ind + conf.LPAREN() + conf.kw("reduce") + "\n"
        llqp += to_llqp(node.op, indent_level + 1, styled) + "\n"
        llqp += to_llqp(node.body, indent_level + 1, styled) + "\n"
        llqp += terms_to_llqp(node.terms, indent_level + 1, styled) + conf.RPAREN()

    elif isinstance(node, ir.Conjunction):
        llqp += ind + conf.LPAREN() + conf.kw("and") + "\n"
        llqp += list_to_llqp(node.args, indent_level + 1, "\n", styled) + conf.RPAREN()

    elif isinstance(node, ir.Disjunction):
        llqp += ind + conf.LPAREN() + conf.kw("or") + "\n"
        llqp += list_to_llqp(node.args, indent_level + 1, "\n", styled) + conf.RPAREN()

    elif isinstance(node, ir.Not):
        llqp += ind + conf.LPAREN() + conf.kw("not") + "\n"
        llqp += to_llqp(node.arg, indent_level + 1, styled) + conf.RPAREN()

    elif isinstance(node, ir.Ffi):
        llqp += ind + conf.LPAREN() + conf.kw("ffi") + " " + ":" + node.name + "\n"
        llqp += ind + conf.SIND() + conf.LPAREN() + conf.kw("args") + "\n"
        llqp += list_to_llqp(node.args, indent_level + 2, "\n", styled) + "\n"
        llqp += ind + conf.SIND() + conf.RPAREN() + "\n"
        llqp += terms_to_llqp(node.terms, indent_level + 1, styled) + conf.RPAREN()

    elif isinstance(node, ir.Atom):
        llqp += f"{ind}{conf.LPAREN()}{conf.kw('atom')} {to_llqp(node.name, 0, styled)} {list_to_llqp(node.terms, 0, ' ', styled)}{conf.RPAREN()}"

    elif isinstance(node, ir.Pragma):
        llqp += f"{ind}{conf.LPAREN()}{conf.kw('pragma')} :{conf.uname(node.name)} {terms_to_llqp(node.terms, 0, styled)}{conf.RPAREN()}"

    elif isinstance(node, ir.Primitive):
        llqp += f"{ind}{conf.LPAREN()}{conf.kw('primitive')} :{conf.uname(node.name)} {list_to_llqp(node.terms, 0, ' ', styled)}{conf.RPAREN()}"

    elif isinstance(node, ir.JustTrue):
        llqp += ind + conf.LPAREN() + conf.kw("true") + conf.RPAREN()

    elif isinstance(node, ir.JustFalse):
        llqp += ind + conf.LPAREN() + conf.kw("false") + conf.RPAREN()

    elif isinstance(node, ir.RelAtom):
        llqp += f"{ind}{conf.LPAREN()}{conf.kw('relatom')} {node.name} {list_to_llqp(node.terms, 0, ' ', styled)}{conf.RPAREN()}"

    elif isinstance(node, ir.Var):
        llqp += ind + conf.uname(node.name) + conf.type_anno("::" + type_to_llqp(node.type))

    elif isinstance(node, ir.Constant):
        llqp += ind
        if isinstance(node.value, str):
            llqp += "\"" + node.value + "\""
        else:
            # suffices to just dump the value?
            llqp += str(node.value)

    elif isinstance(node, ir.Attribute):
        llqp += ind
        llqp += conf.LPAREN() + conf.kw("attribute") + " "
        llqp += ":" + node.name + " "
        if len(node.args) == 0:
            llqp += conf.LPAREN() + conf.kw("args") + conf.RPAREN()
        else:
            llqp += conf.LPAREN() + conf.kw("args") + " "
            llqp += list_to_llqp(node.args, 0, " ", styled)
            llqp += conf.RPAREN()
        llqp += conf.RPAREN()

    elif isinstance(node, ir.RelationId):
        llqp += f"{ind}:{conf.uname(str(node.id))}"

    elif isinstance(node, ir.PrimitiveType):
        llqp += ind + node.name

    else:
        raise NotImplementedError(f"to_llqp not implemented for {type(node)}.")

    return llqp

def type_to_llqp(node: ir.RelType) -> str:
    assert isinstance(node, ir.PrimitiveType), "Only support primitive types for now"
    return node.name
