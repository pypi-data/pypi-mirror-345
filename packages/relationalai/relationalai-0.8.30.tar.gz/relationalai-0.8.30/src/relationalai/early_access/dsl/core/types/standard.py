from relationalai.early_access.dsl.core.types.constrained.subtype import ValueSubtype
from relationalai.early_access.dsl.core.types.unconstrained import UnconstrainedValueType, UnconstrainedNumericType

standard_value_types = {}

# Hash types
Hash = UnconstrainedValueType('Hash')
standard_value_types[Hash.name()] = Hash

# Boolean types
Boolean = UnconstrainedNumericType('Boolean')
standard_value_types[Boolean.name()] = Boolean

# Decimal types
#
Decimal = UnconstrainedNumericType('Decimal')
standard_value_types[Decimal.name()] = Decimal

UnsignedDecimal = ValueSubtype('UnsignedDecimal')
standard_value_types[UnsignedDecimal.name()] = UnsignedDecimal
with UnsignedDecimal:
    x = Decimal()
    x >= 0

PositiveDecimal = ValueSubtype('PositiveDecimal')
standard_value_types[PositiveDecimal.name()] = PositiveDecimal
with PositiveDecimal:
    x = UnsignedDecimal()
    x != 0

# Floating-point types
#
Float = UnconstrainedNumericType('Float')
standard_value_types[Float.name()] = Float
Double = UnconstrainedNumericType('Double')  # A float64 in Rel
standard_value_types[Double.name()] = Double

# Integer types
#
BigInteger = UnconstrainedNumericType('BigInteger')  # 128-bit integer
standard_value_types[BigInteger.name()] = BigInteger

BigUnsignedInteger = ValueSubtype('BigUnsignedInteger')
standard_value_types[BigUnsignedInteger.name()] = BigUnsignedInteger
with BigUnsignedInteger:
    x = BigInteger()
    x >= 0

BigPositiveInteger = ValueSubtype('BigPositiveInteger')
standard_value_types[BigPositiveInteger.name()] = BigPositiveInteger
with BigPositiveInteger:
    x = BigUnsignedInteger()
    x != 0

Integer = UnconstrainedNumericType('Integer')
standard_value_types[Integer.name()] = Integer

UnsignedInteger = ValueSubtype('UnsignedInteger')
standard_value_types[UnsignedInteger.name()] = UnsignedInteger
with UnsignedInteger:
    x = Integer()
    x >= 0

PositiveInteger = ValueSubtype('PositiveInteger')
standard_value_types[PositiveInteger.name()] = PositiveInteger
with PositiveInteger:
    x = UnsignedInteger()
    x != 0

# Date types
#
Date = UnconstrainedValueType('Date')
standard_value_types[Date.name()] = Date

# DateTime types
#
DateTime = UnconstrainedValueType('DateTime')
standard_value_types[DateTime.name()] = DateTime

RowId = UnconstrainedNumericType('RowId')
standard_value_types[RowId.name()] = RowId

# String types
#
String = UnconstrainedValueType('String')
standard_value_types[String.name()] = String

Any = UnconstrainedValueType('Any')
standard_value_types[Any.name()] = Any

Symbol = UnconstrainedValueType('Symbol')
standard_value_types[Symbol.name()] = Symbol
