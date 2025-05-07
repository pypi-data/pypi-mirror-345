import warnings

import owlready2

from relationalai.early_access.dsl.core.types.standard import String, Float, Integer, Date, DateTime
from relationalai.early_access.dsl.core.utils import to_pascal_case
from relationalai.early_access.dsl.ontologies.models import Model
from relationalai.early_access.dsl.types.entities import EntityType
from owlready2 import owl, get_ontology
from datetime import datetime, date
import re


class OwlAdapter:

    def __init__(self, owl_file_path: str):
        self.ontology = get_ontology(owl_file_path).load()
        self._prefix = f"{self.ontology.name}."
        self._reading_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        self.model = self._bootstrap_model()
        self._add_classes()
        self._add_object_properties()
        self._add_datatype_properties()
        self._add_individuals()

    def _clean_name(self, name: str):
        cs = name.removeprefix(self._prefix)
        return cs

    @staticmethod
    def _is_root_class(ontology_class):
        return not ontology_class.is_a or (owl.Thing in ontology_class.is_a)

    @staticmethod
    def _is_functional(object_property):
        return owl.FunctionalProperty in object_property.is_a

    @staticmethod
    def _is_inverse_functional(object_property):
        return owl.InverseFunctionalProperty in object_property.is_a

    def _get_reading(self, relationship_name: str):
        return self._reading_pattern.sub(' ', relationship_name).lower()

    def _get_mandatory_participation(self, c):
        properties = []
        pattern = r'Inverse\((.*?)\)'

        if c is not None:
            for isa in c.is_a:
                if "some" in str(isa):
                    match = re.search(pattern, str(isa.property))
                    if match:
                        result = match.group(1)
                        properties.append(self._clean_name(result + "-"))
                    else:
                        properties.append(self._clean_name(str(isa.property)))
        return properties

    @staticmethod
    def _xsd_type_to_rel_type(tp):
        mapping = {
            str: String,
            int: Integer,
            float: Float,
            date: Date,
            datetime: DateTime
        }
        return mapping.get(tp, String)

    @staticmethod
    def _get_covering_subclasses(c):
        result = []
        for ec in c.equivalent_to:
            if "|" in str(ec):
                for cs in ec.Classes:
                    result.append(cs)
        return result

    def _get_disjoint_classes(self, c):
        disjoints = []
        pattern = re.compile(r'Not\((.*?)\)')

        for isa in c.is_a:
            match = pattern.search(str(isa))
            if match:
                disjoints.append(self._clean_name(match.group(1)))
            else:
                disjoints.append(self._clean_name(str(getattr(isa, 'property', isa))))

        return disjoints

    def _has_disjoint_sub_types(self, c):
        ecu = sorted([self._clean_name(str(ec)) for ec in self._get_covering_subclasses(c)])
        for ec in self._get_covering_subclasses(c):
            ecu_compare = [str(df) for df in self._get_disjoint_classes(ec)]
            ecu_compare.append(self._clean_name(str(ec)))
            if not ecu == sorted(ecu_compare):
                return False
        return True

    def _bootstrap_model(self) -> Model:
        model_name = re.sub(r'(?<!^)(?=[A-Z])', '_', self.ontology.name).lower()
        md = Model(model_name + "Model")

        # IRI ValueType declaration - this will be used as preferred identifier for all entity types
        iri = md.value_type("IRI", String)
        # OWL Things Entity declaration - all the root classes will be subtype of OWL Thing
        # This is needed because in Owl individuals can have more than one type; in such
        # cases we will assign them the generic OWL Thing type.
        md.entity_type("OWLThing", iri)
        return md

    # Classes and Subclasses
    def _add_classes(self):
        owl_thing_entity = self.model.lookup_concept("OWLThing")
        owl_thing_subclasses = []
        for ontology_class in list(self.ontology.classes()):
            if self.validate_class(ontology_class):
                class_name = self._clean_name(str(ontology_class))
                class_entity = self.model.lookup_concept(class_name)

                if class_entity is None:
                    # Classes that do not have any super type are identified by the IRI value type
                    # Re-declaring the identifier here even if it is technically inherited from OWL Thing as this
                    # class is just a placeholder, and we might drop it later

                    class_entity = self.model.entity_type(class_name)
                    if self._is_root_class(ontology_class):
                        owl_thing_subclasses.append(class_entity)

                # SubClasses
                subclasses = []
                for sub_class in list(ontology_class.subclasses()):
                    if self.validate_class(sub_class):
                        sub_class_name = self._clean_name(str(sub_class))
                        sub_class_entity = self.model.lookup_concept(sub_class_name)
                        if sub_class_entity is None:
                            sub_class_entity = self.model.entity_type(sub_class_name)
                        subclasses.append(sub_class_entity)

                # Check for inclusive or exclusive type arrows
                if subclasses and self._has_disjoint_sub_types(ontology_class) and self._get_covering_subclasses(
                        ontology_class):
                    self.model.subtype_arrow(class_entity, subclasses, True)
                elif subclasses and self._get_covering_subclasses(ontology_class):
                    self.model.subtype_arrow(class_entity, subclasses, False, True)
                elif subclasses:
                    self.model.subtype_arrow(class_entity, subclasses)

        if owl_thing_entity is not None:
            self.model.subtype_arrow(owl_thing_entity, owl_thing_subclasses)

    # Object Properties
    def _add_object_properties(self):
        for op in list(self.ontology.object_properties()):
            object_property_name = self._clean_name(str(op))
            # In OWL, in general domains and ranges can be defined as union or intersection of multiple classes.
            # This has no direct translation to our model, thus we can only cover the cases where the domains and
            # ranges are single expression. We need to check for this here.
            if self._validate_domain_and_range(op):
                d = self._clean_name(str(op.domain[0]))
                domain_entity = self.model.lookup_concept(d)
                r = self._clean_name(str(op.range[0]))
                range_entity = self.model.lookup_concept(r)

                inverse_property_name = ""
                if op.inverse_property is not None:
                    inverse_property_name = self._clean_name(str(op.inverse_property))
                inv_rel_name = r.capitalize() + to_pascal_case(inverse_property_name) + d.capitalize()
                inv_rel_entity = self.model.lookup_relationship(inv_rel_name)
                if inv_rel_entity is None:
                    with self.model.relationship() as rel:
                        # Check for functionality and mandatory participation for the domain
                        if object_property_name in self._get_mandatory_participation(
                                op.domain[0]) and self._is_functional(op):
                            rel.role(domain_entity, mandatory=True, unique=True)
                        elif self._is_functional(op):
                            rel.role(domain_entity, unique=True)
                        else:
                            rel.role(domain_entity, name=object_property_name)
                        # Check for functionality and mandatory participation for the range
                        if object_property_name + '-' in self._get_mandatory_participation(
                                op.range[0]) and self._is_inverse_functional(op):
                            rel.role(range_entity, mandatory=True, unique=True)
                        elif self._is_inverse_functional(op):
                            rel.role(range_entity, unique=True)
                        else:
                            rel.role(range_entity)

                    # Readings
                    rel.relation(rel.role_at(0), self._get_reading(object_property_name), rel.role_at(1))
                    if inverse_property_name != "":
                        rel.relation(rel.role_at(1), self._get_reading(inverse_property_name), rel.role_at(0))

                    if not self._is_functional(op) and not self._is_inverse_functional(op):
                        self.model.unique(rel.role_at(0), rel.role_at(1))

    # Datatype Properties
    def _add_datatype_properties(self):
        for dp in list(self.ontology.data_properties()):
            if self._validate_domain_and_range(dp):
                datatype_property_name = to_pascal_case(self._clean_name(str(dp)))
                data_type_entity = self.model.lookup_concept(datatype_property_name)
                if data_type_entity is None and len(dp.range) == 1:
                    r = dp.range[0]
                    xsd_type = self._xsd_type_to_rel_type(r)
                    data_type_entity = self.model.value_type(datatype_property_name, xsd_type)
                else:
                    data_type_entity = self.model.value_type(datatype_property_name, String)

                d = self._clean_name(str(dp.domain[0]))
                domain_entity = self.model.lookup_concept(d)

                with self.model.relationship(domain_entity, "has", data_type_entity) as rel:
                    self.model.unique(rel.role_at(0), rel.role_at(1))

    # Individuals
    def _add_individuals(self):
        for idv in list(self.ontology.individuals()):
            iri = idv.namespace.base_iri + idv.name
            individual_class = ""
            if len(idv.is_a) == 1:
                individual_class = self._clean_name(str(idv.is_a[0]))
            else:
                individual_class += "OWLThing"
            entity_type = self.model.lookup_concept(individual_class)
            if isinstance(entity_type, EntityType):
                entity_type._add_instance(iri)

    @staticmethod
    def _validate_domain_and_range(op):
        if len(op.domain) == 0:
            warnings.warn(f"Missing domain for {str(op)}, it won't be translated.")
            return False
        elif len(op.domain) > 1:
            warnings.warn(f"Unsupported complex expression in the domain of {str(op)}, it won't be translated.")
            return False
        elif len(op.range) == 0:
            warnings.warn(f"Missing range for {str(op)}, it won't be translated.")
            return False
        elif len(op.range) > 1:
            warnings.warn(
                f"Unsupported complex expression in the range of {str(op)}, it won't be translated.")
            return False
        else:
            return True

    @staticmethod
    def validate_class(c):
        super_classes_count = 0
        for sup_c in c.is_a:
            if isinstance(sup_c, owlready2.EntityClass):
                super_classes_count += 1
        if super_classes_count > 1:
            warnings.warn(f"{str(c)} has multiple parents")
            return False
        else:
            return True
