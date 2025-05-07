from relationalai.early_access.dsl.core.namespaces import Namespace
from relationalai.early_access.dsl.core.relations import RelationSignature, ExternalRelation
from relationalai.early_access.dsl.core.types.standard import DateTime, Date, PositiveInteger, Decimal, String

standard_relations = {}

parse_date_name = "parse_date"
parse_date = ExternalRelation(Namespace.top, parse_date_name, RelationSignature(String, String, Date))
standard_relations[parse_date_name] = parse_date

parse_datetime_name = "parse_datetime"
parse_datetime = ExternalRelation(Namespace.top, parse_datetime_name, RelationSignature(String, String, DateTime))
standard_relations[parse_datetime_name] = parse_datetime

parse_decimal_name = "parse_decimal"
parse_decimal = ExternalRelation(Namespace.top, parse_decimal_name, RelationSignature(PositiveInteger, PositiveInteger, String, Decimal))
standard_relations[parse_decimal_name] = parse_decimal