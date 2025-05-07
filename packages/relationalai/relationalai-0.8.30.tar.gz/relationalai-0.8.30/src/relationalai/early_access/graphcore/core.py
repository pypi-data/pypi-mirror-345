"""
Core functionality for the graphlib package.
"""

from typing import Optional
from abc import ABC, abstractmethod

from relationalai.early_access.builder import Model, Relationship
from relationalai.early_access.builder import Integer, Float
from relationalai.early_access.builder import where, define, count

class AbstractGraphCore(ABC):
    _model: Model
    # NOTE: _validate_provided_model(), called from __init__, asserts that
    #   `edge_arg._model` is a `Model`, but type checkers fail to pick
    #   that information up, necessitating this `_model: Model` and
    #   the `# type: ignore[Model]` on assignment of `_model` in __init__.

    def __init__(self, edge_arg: Relationship, node_arg: Optional[Relationship] = None):
        """
        Abstract base class for graphs, containing logic common to both
        DirectedGraphCore and UndirectedGraphCore (which inherit from this class).
        """
        self._validate_provided_edge_relationship(edge_arg)
        self._validate_provided_node_relationship(node_arg)
        self._validate_provided_model(edge_arg, node_arg)
        self._model = edge_arg._model # type: ignore[Model]
        self._edge_arg = edge_arg
        self._node_arg = node_arg

        self.is_weighted = len(edge_arg._fields) == 3

        self._define_node_relationship()
        self._define_edge_relationships()
 
        self._define_num_nodes_relationship()
        self._define_num_edges_relationship()

        self._define_neighbor_relationships()
        self._define_count_neighbor_relationships()
        self._define_common_neighbor_relationship()
        self._define_count_common_neighbor_relationship()

        self._define_degree_relationships()


    def _validate_provided_edge_relationship(self, edge_arg):
        assert isinstance(edge_arg, Relationship), \
            "The `edge` argument must be a Relationship."

        edge_arg_field_count = len(edge_arg._fields)
        edge_arg_field_types = [field.type_str for field in edge_arg._fields]

        assert edge_arg_field_count in [2, 3], \
            f"The `edge` relationship must have width two or three, " \
            f"whereas it has width {edge_arg_field_count}."
        assert edge_arg_field_types[0] == "Integer", \
            f"The `edge` relationship's first value must have type Integer, " \
            f"whereas it has type {edge_arg_field_types[0]}."
        assert edge_arg_field_types[1] == "Integer", \
            f"The `edge` relationship's second value must have type Integer, " \
            f"whereas it has type {edge_arg_field_types[1]}."
        if edge_arg_field_count == 3:
            assert edge_arg_field_types[2] == "Float", \
                f"The `edge` relationship's third value must have type Float, " \
                f"whereas it has type {edge_arg_field_types[2]}."

    def _validate_provided_node_relationship(self, node_arg):
        assert node_arg is None or isinstance(node_arg, Relationship), \
            "The `node` argument must be either a Relationship or None."

        if isinstance(node_arg, Relationship):
            node_arg_field_count = len(node_arg._fields)
            node_arg_field_types = [field.type_str for field in node_arg._fields]

            assert node_arg_field_count == 1, \
                f"The `node` relationship must have arity 1, " \
                f"whereas it has arity {node_arg_field_count}."
            assert node_arg_field_types[0] == "Integer", \
                f"The `node` relationship's value must have type Integer, " \
                f"whereas it has type {node_arg_field_types[0]}."

    def _validate_provided_model(self, edge_arg, node_arg):
        assert isinstance(edge_arg._model, Model), (
            "The `edge` relationship must be attached to a model.")
        assert node_arg is None or node_arg._model == edge_arg._model, (
            "The `node` and `edge` relationships must belong to the same model. "
            "Please ensure both relationships are defined in the same model.")


    def _define_node_relationship(self):
        """
        Define the self.node relationship, consume the provided
        self._node_arg and self._edge_arg relationships.
        """
        self.node = self._model.Relationship("{node:Integer}")

        node_a, node_b = Integer.ref(), Integer.ref()
        # Populate with any explicitly provided nodes.
        if isinstance(self._node_arg, Relationship):
                where(self._node_arg(node_a)).define(self.node(node_a))
        # Populate with all nodes implied by edges.
        ((where(self._edge_arg(node_a, node_b, Float)) if self.is_weighted else
          where(self._edge_arg(node_a, node_b)))
          .define(self.node(node_a), self.node(node_b)))

    def _define_edge_relationships(self):
        """
        Define the self.edge and self.weight relationships,
        consuming the provided self._edge_arg relationship."""
        self.edge = self._model.Relationship("{node_a:Integer} has edge to {node_b:Integer}")
        self.weight = self._model.Relationship("{node_a:Integer} has edge to {node_b:Integer} with weight {weight:Float}")
        self._populate_edge_relationships()
        
    @abstractmethod
    def _populate_edge_relationships(self):
        """
        Populate the self.edge and self.weight relationships,
        consuming the provided self._edge_arg relationship.
        DirectedGraphCore and UndirectedGraphCore must implement this method.
        """
        pass


    def _define_num_nodes_relationship(self):
        """Define the self.num_nodes relationship."""
        node_a = Integer.ref()
        self.num_nodes = self._model.Relationship("{num_nodes:Integer}")
        define(self.num_nodes(count(self.node(node_a)) | 0))

    def _define_num_edges_relationship(self):
        """Define the self.num_edges relationship."""
        self.num_edges = self._model.Relationship("{num_edges:Integer}")
        self._populate_num_edges_relationship()

    @abstractmethod
    def _populate_num_edges_relationship(self):
        """
        Populate the self.num_edges relationship, which
        DirectedGraphCore and UndirectedGraphCore must implement.
        """
        pass


    def _define_neighbor_relationships(self):
        """Define the self.[in,out]neighbor relationships."""
        self.neighbor = self._model.Relationship("{node_a:Integer} has neighbor {node_b:Integer}")
        self.inneighbor = self._model.Relationship("{node_a:Integer} has inneighbor {node_b:Integer}")
        self.outneighbor = self._model.Relationship("{node_a:Integer} has outneighbor {node_b:Integer}")

        node_a, node_b = Integer.ref(), Integer.ref()
        where(self.edge(node_a, node_b)).define(self.neighbor(node_a, node_b), self.neighbor(node_b, node_a))
        where(self.edge(node_b, node_a)).define(self.inneighbor(node_a, node_b))
        where(self.edge(node_a, node_b)).define(self.outneighbor(node_a, node_b))
        # Note that these definitions happen to work for both
        # directed and undirected graphs due to `edge` containing
        # each edge's symmetric partner in the undirected case.

    def _define_count_neighbor_relationships(self):
        """
        Define the self.count_[in,out]neighbor relationships.
        Note that these relationships differ from corresponding
        [in,out]degree relationships in that they yield empty
        rather than zero absent [in,out]neighbors.
        Primarily for internal consumption.
        """
        self.count_neighbor = self._model.Relationship("{node:Integer} has neighbor count {count:Integer}")
        self.count_inneighbor = self._model.Relationship("{node:Integer} has inneighbor count {count:Integer}")
        self.count_outneighbor = self._model.Relationship("{node:Integer} has outneighbor count {count:Integer}")

        node_a, node_b = Integer.ref(), Integer.ref()
        where(self.neighbor(node_a, node_b)).define(self.count_neighbor(node_a, count(node_b).per(node_a)))
        where(self.inneighbor(node_a, node_b)).define(self.count_inneighbor(node_a, count(node_b).per(node_a)))
        where(self.outneighbor(node_a, node_b)).define(self.count_outneighbor(node_a, count(node_b).per(node_a)))

    def _define_common_neighbor_relationship(self):
        """Define the self.common_neighbor relationship."""
        self.common_neighbor = self._model.Relationship("{node_a:Integer} and {node_b:Integer} have common neighbor {node_c:Integer}")

        node_a, node_b, node_c = Integer.ref(), Integer.ref(), Integer.ref()
        where(self.neighbor(node_a, node_c), self.neighbor(node_b, node_c)).define(self.common_neighbor(node_a, node_b, node_c))

    def _define_count_common_neighbor_relationship(self):
        """Define the self.count_common_neighbor relationship."""
        self.count_common_neighbor = self._model.Relationship("{node_a:Integer} and {node_b:Integer} have common neighbor count {count:Integer}")

        node_a, node_b, node_c = Integer.ref(), Integer.ref(), Integer.ref()
        where(self.common_neighbor(node_a, node_b, node_c)).define(self.count_common_neighbor(node_a, node_b, count(node_c).per(node_a, node_b)))


    def _define_degree_relationships(self):
        """Define the self.[in,out]degree relationships."""
        self.degree = self._model.Relationship("{node:Integer} has degree {count:Integer}")
        self.indegree = self._model.Relationship("{node:Integer} has indegree {count:Integer}")
        self.outdegree = self._model.Relationship("{node:Integer} has outdegree {count:Integer}")

        node, xcount = Integer.ref(), Integer.ref()
        where(
            self.node(node),
            _indegree := where(self.count_inneighbor(node, xcount)).select(xcount) | 0,
        ).define(self.indegree(node, _indegree))
        where(
            self.node(node),
            _outdegree := where(self.count_outneighbor(node, xcount)).select(xcount) | 0,
        ).define(self.outdegree(node, _outdegree))

        self._populate_degree_relationship()

    @abstractmethod
    def _populate_degree_relationship(self):
        """
        Populate the self.degree relationship, which
        DirectedGraphCore and UndirectedGraphCore must implement.
        """
        pass


class DirectedGraphCore(AbstractGraphCore):
    def __init__(self, edge_arg: Relationship, node_arg: Optional[Relationship] = None):
        self.is_directed = True
        super().__init__(edge_arg, node_arg)

    # Implementation of abstract method required by parent class.
    def _populate_edge_relationships(self):
        node_a, node_b, edge_weight = Integer.ref(), Integer.ref(), Float.ref() 

        if self.is_weighted:  # Weighted directed edges
            where(self._edge_arg(node_a, node_b, edge_weight)).define(
                self.weight(node_a, node_b, edge_weight),
                self.edge(node_a, node_b)
            )
        else:  # Unweighted directed edges
            where(self._edge_arg(node_a, node_b)).define(
                self.weight(node_a, node_b, 1.0),
                self.edge(node_a, node_b)
            )

    # Implementation of abstract method required by parent class.
    def _populate_num_edges_relationship(self):
        node_a, node_b = Integer.ref(), Integer.ref()
        define(self.num_edges(count(node_a, node_b, self.edge(node_a, node_b)) | 0))

    # Implementation of abstract method required by parent class.
    def _populate_degree_relationship(self):
        node, incount, outcount = Integer.ref(), Integer.ref(), Integer.ref()
        where(
            self.node(node),
            _indegree := where(self.indegree(node, incount)).select(incount) | 0,
            _outdegree := where(self.outdegree(node, outcount)).select(outcount) | 0,
        ).define(self.degree(node, _indegree + _outdegree))


class UndirectedGraphCore(AbstractGraphCore):
    def __init__(self, edge_arg: Relationship, node_arg: Optional[Relationship] = None):
        self.is_directed = False
        super().__init__(edge_arg, node_arg)

    # Implementation of abstract method required by parent class.
    def _populate_edge_relationships(self):
        node_a, node_b, edge_weight = Integer.ref(), Integer.ref(), Float.ref() 

        if self.is_weighted:  # Weighted undirected edges
            where(self._edge_arg(node_a, node_b, edge_weight)).define(
                self.weight(node_a, node_b, edge_weight),
                self.weight(node_b, node_a, edge_weight),
                self.edge(node_a, node_b),
                self.edge(node_b, node_a)
            )
        else:  # Unweighted undirected edges
            where(self._edge_arg(node_a, node_b)).define(
                self.weight(node_a, node_b, 1.0),
                self.weight(node_b, node_a, 1.0),
                self.edge(node_a, node_b),
                self.edge(node_b, node_a)
            )

    # Implementation of abstract method required by parent class.
    def _populate_num_edges_relationship(self):
        node_a, node_b = Integer.ref(), Integer.ref()
        define(self.num_edges(count(node_a, node_b, self.edge(node_a, node_b), node_a <= node_b) | 0))

    # Implementation of abstract method required by parent class.
    def _populate_degree_relationship(self):
        node, neighcount = Integer.ref(), Integer.ref()
        where(
            self.node(node),
            _degree := where(self.count_neighbor(node, neighcount)).select(neighcount) | 0,
        ).define(self.degree(node, _degree))