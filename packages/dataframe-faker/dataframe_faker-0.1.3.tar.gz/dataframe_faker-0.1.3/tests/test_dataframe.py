import datetime
import zoneinfo
from decimal import Decimal
from string import ascii_lowercase, digits

import pytest
from faker import Faker
from pyspark.sql import Row, SparkSession
from pyspark.sql.types import (
    ArrayType,
    BinaryType,
    BooleanType,
    ByteType,
    DateType,
    DayTimeIntervalType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    StringType,
    StructField,
    StructType,
    TimestampNTZType,
    TimestampType,
)

from dataframe_faker.constraints import (
    ArrayConstraint,
    BinaryConstraint,
    BooleanConstraint,
    ByteConstraint,
    DateConstraint,
    DayTimeIntervalConstraint,
    DecimalConstraint,
    DoubleConstraint,
    FloatConstraint,
    IntegerConstraint,
    LongConstraint,
    ShortConstraint,
    StringConstraint,
    StructConstraint,
    TimestampConstraint,
    TimestampNTZConstraint,
)
from dataframe_faker.dataframe import (
    ALPHABET,
    _convert_dict_to_constraint,
    _convert_schema_string_to_schema,
    _generate_fake_string,
    _validate_dtype_and_constraint,
    generate_fake_dataframe,
    generate_fake_value,
)

from .helpers import assert_schema_equal, is_valid_email

UUID_ALPHABET = ascii_lowercase + digits + "-"


def test_convert_schema_string_to_schema(spark: SparkSession) -> None:
    schema_str = (
        "id: int not null, str_col: string, struct_col: struct<arr: array<float>>"
    )

    actual = _convert_schema_string_to_schema(schema=schema_str, spark=spark)
    expected = StructType(
        [
            StructField(name="id", dataType=IntegerType(), nullable=False),
            StructField(name="str_col", dataType=StringType(), nullable=True),
            StructField(
                name="struct_col",
                dataType=StructType(
                    [
                        StructField(
                            name="arr",
                            dataType=ArrayType(elementType=FloatType()),
                            nullable=True,
                        )
                    ]
                ),
                nullable=True,
            ),
        ]
    )

    assert_schema_equal(actual=actual, expected=expected)


def test__validate_dtype_and_constraint() -> None:
    dtypes = [
        ArrayType(elementType=IntegerType()),
        BinaryType(),
        BooleanType(),
        ByteType(),
        DateType(),
        DayTimeIntervalType(),
        DecimalType(),
        DoubleType(),
        FloatType(),
        IntegerType(),
        LongType(),
        ShortType(),
        StringType(),
        StructType(),
        TimestampType(),
        TimestampNTZType(),
    ]
    constraints = [
        ArrayConstraint(),
        BinaryConstraint(),
        BooleanConstraint(),
        ByteConstraint(),
        DateConstraint(),
        DayTimeIntervalConstraint(),
        DecimalConstraint(),
        DoubleConstraint(),
        FloatConstraint(),
        IntegerConstraint(),
        LongConstraint(),
        ShortConstraint(),
        StringConstraint(),
        StructConstraint(),
        TimestampConstraint(),
        TimestampNTZConstraint(),
    ]
    for dtype, constraint in zip(dtypes, constraints):
        _validate_dtype_and_constraint(dtype=dtype, constraint=constraint)

    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=ArrayType(elementType=IntegerType()),
            constraint=IntegerConstraint(),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=ArrayType(elementType=IntegerType()),
            constraint=StructConstraint(),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=StructType(),
            constraint=IntegerConstraint(),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=StructType(),
            constraint=ArrayConstraint(),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=IntegerType(),
            constraint=StringConstraint(),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=IntegerType(),
            constraint=StructConstraint(),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=ByteType(),
            constraint=ByteConstraint(min_value=-200),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=ShortType(),
            constraint=ShortConstraint(max_value=9999999),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=IntegerType(),
            constraint=IntegerConstraint(max_value=9223372036854775),
        )
    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(
            dtype=LongType(),
            constraint=LongConstraint(min_value=-9223372036854775809),
        )

    # only checks top-level
    _validate_dtype_and_constraint(
        dtype=ArrayType(elementType=StringType()),
        constraint=ArrayConstraint(element_constraint=IntegerConstraint()),
    )

    # works with fields inside StructType as well
    _validate_dtype_and_constraint(
        dtype=StructType(fields=[StructField(name="asd", dataType=StringType())]),
        constraint=StructConstraint(),
    )

    with pytest.raises(ValueError):
        _validate_dtype_and_constraint(dtype=StringType(), constraint=None)


def test_generate_fake_value(fake: Faker) -> None:
    for _ in range(100):
        actual_list = generate_fake_value(
            dtype=ArrayType(elementType=IntegerType()),
            fake=fake,
            nullable=False,
            constraint=ArrayConstraint(
                element_constraint=IntegerConstraint(min_value=1, max_value=1),
                min_length=2,
                max_length=2,
            ),
        )
        assert isinstance(actual_list, list)
        assert len(actual_list) == 2
        assert actual_list[0] == 1
        assert actual_list[1] == 1

        actual_binary = generate_fake_value(
            dtype=BinaryType(),
            nullable=False,
            fake=fake,
            constraint=BinaryConstraint(min_length=4, max_length=4),
        )
        assert isinstance(actual_binary, bytearray)
        assert len(actual_binary) == 4

        actual_bool = generate_fake_value(
            dtype=BooleanType(), nullable=False, fake=fake
        )
        assert isinstance(actual_bool, bool)

        actual_bool = generate_fake_value(
            dtype=BooleanType(),
            nullable=False,
            fake=fake,
            constraint=BooleanConstraint(true_chance=1.0),
        )
        assert isinstance(actual_bool, bool)
        assert actual_bool

        actual_bool = generate_fake_value(
            dtype=BooleanType(),
            nullable=False,
            fake=fake,
            constraint=BooleanConstraint(true_chance=0.0),
        )
        assert isinstance(actual_bool, bool)
        assert not actual_bool

        actual_byte = generate_fake_value(
            dtype=ByteType(),
            fake=fake,
            nullable=False,
            constraint=ByteConstraint(min_value=1, max_value=5),
        )
        assert isinstance(actual_byte, int)
        assert actual_byte in range(1, 6)

        actual_date = generate_fake_value(
            dtype=DateType(),
            fake=fake,
            nullable=False,
            constraint=DateConstraint(
                min_value=datetime.date(year=2024, month=3, day=2),
                max_value=datetime.date(year=2024, month=3, day=3),
            ),
        )
        assert isinstance(actual_date, datetime.date)
        assert actual_date in [
            datetime.date(year=2024, month=3, day=2),
            datetime.date(year=2024, month=3, day=3),
        ]

        actual_daytimeinterval = generate_fake_value(
            dtype=DayTimeIntervalType(),
            fake=fake,
            nullable=False,
            constraint=DayTimeIntervalConstraint(
                min_value=datetime.timedelta(minutes=2.1),
                max_value=datetime.timedelta(minutes=2.1),
            ),
        )
        assert isinstance(actual_daytimeinterval, datetime.timedelta)
        assert actual_daytimeinterval == datetime.timedelta(minutes=2.1)

        actual_decimal = generate_fake_value(
            dtype=DecimalType(scale=3),
            fake=fake,
            nullable=False,
            constraint=DecimalConstraint(
                min_value=Decimal("5.123"), max_value=Decimal("5.123")
            ),
        )
        assert isinstance(actual_decimal, Decimal)
        assert actual_decimal == Decimal("5.123")

        actual_double = generate_fake_value(
            dtype=DoubleType(),
            fake=fake,
            nullable=False,
            constraint=DoubleConstraint(min_value=5.0, max_value=5.0),
        )
        assert isinstance(actual_double, float)
        assert actual_double == 5.0

        actual_float = generate_fake_value(
            dtype=FloatType(),
            fake=fake,
            nullable=False,
            constraint=FloatConstraint(min_value=5.0, max_value=5.0),
        )
        assert isinstance(actual_float, float)
        assert actual_float == 5.0

        actual_float = generate_fake_value(
            dtype=FloatType(),
            fake=fake,
            nullable=False,
            constraint=FloatConstraint(min_value=-1.0, max_value=1.0),
        )
        assert isinstance(actual_float, float)
        assert actual_float >= -1.0
        assert actual_float <= 1.0

        actual_int = generate_fake_value(
            dtype=IntegerType(),
            fake=fake,
            nullable=False,
            constraint=IntegerConstraint(min_value=1, max_value=5),
        )
        assert isinstance(actual_int, int)
        assert actual_int in range(1, 6)

        actual_long = generate_fake_value(
            dtype=LongType(),
            fake=fake,
            nullable=False,
            constraint=LongConstraint(min_value=30000000000, max_value=30000000005),
        )
        assert isinstance(actual_long, int)
        assert actual_long in range(30000000000, 30000000006)

        actual_short = generate_fake_value(
            dtype=ShortType(),
            fake=fake,
            nullable=False,
            constraint=ShortConstraint(min_value=1, max_value=5),
        )
        assert isinstance(actual_short, int)
        assert actual_short in range(1, 6)

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="address"),
        )
        assert isinstance(actual_string, str)
        assert len(actual_string) > 0  # Address should not be empty
        assert "\n" in actual_string  # Faker's address() typically includes newlines
        assert any(char.isdigit() for char in actual_string)  # Should contain numbers

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(
                string_type="any", min_length=16, max_length=16
            ),
        )
        assert isinstance(actual_string, str)
        assert len(actual_string) == 16
        for c in actual_string:
            assert c in ALPHABET

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="email"),
        )
        assert isinstance(actual_string, str)
        assert is_valid_email(email=actual_string)

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="first_name"),
        )
        assert isinstance(actual_string, str)

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="last_name"),
        )
        assert isinstance(actual_string, str)

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="name"),
        )
        assert isinstance(actual_string, str)

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="phone_number"),
        )
        assert isinstance(actual_string, str)

        actual_string = generate_fake_value(
            dtype=StringType(),
            fake=fake,
            nullable=False,
            constraint=StringConstraint(string_type="uuid4"),
        )
        assert isinstance(actual_string, str)
        assert len(actual_string) == 32 + 4
        for c in actual_string:
            assert c in UUID_ALPHABET
        assert actual_string.count("-") == 4
        assert [len(s) for s in actual_string.split("-")] == [8, 4, 4, 4, 12]

        actual_struct = generate_fake_value(
            dtype=StructType(
                fields=[
                    StructField(name="f1", dataType=IntegerType(), nullable=True),
                    StructField(name="g2", dataType=StringType()),
                ]
            ),
            fake=fake,
            nullable=False,
            constraint=StructConstraint(
                element_constraints={
                    "f1": IntegerConstraint(null_chance=1.0),
                    "g2": StringConstraint(string_type="email"),
                }
            ),
        )
        assert isinstance(actual_struct, dict)
        assert actual_struct["f1"] is None
        assert is_valid_email(actual_struct["g2"])

        actual_timestamp = generate_fake_value(
            dtype=TimestampType(),
            fake=fake,
            nullable=False,
            constraint=TimestampConstraint(
                min_value=datetime.datetime(
                    year=2020,
                    month=1,
                    day=1,
                    hour=3,
                    minute=1,
                    second=1,
                    microsecond=500000,
                    tzinfo=zoneinfo.ZoneInfo("Europe/Helsinki"),
                ),
                max_value=datetime.datetime(
                    year=2020,
                    month=1,
                    day=1,
                    hour=1,
                    minute=1,
                    second=10,
                    microsecond=500000,
                    tzinfo=zoneinfo.ZoneInfo("UTC"),
                ),
                tzinfo=zoneinfo.ZoneInfo("Europe/Helsinki"),
            ),
        )
        assert isinstance(actual_timestamp, datetime.datetime)
        assert actual_timestamp >= datetime.datetime(
            year=2020,
            month=1,
            day=1,
            hour=1,
            minute=1,
            second=1,
            microsecond=500000,
            tzinfo=zoneinfo.ZoneInfo("UTC"),
        )
        assert actual_timestamp <= datetime.datetime(
            year=2020,
            month=1,
            day=1,
            hour=1,
            minute=1,
            second=10,
            microsecond=500000,
            tzinfo=zoneinfo.ZoneInfo("UTC"),
        )

        actual_timestamp_ntz = generate_fake_value(
            dtype=TimestampNTZType(),
            fake=fake,
            nullable=False,
            constraint=TimestampNTZConstraint(
                min_value=datetime.datetime(
                    year=2020,
                    month=1,
                    day=1,
                    hour=1,
                    minute=1,
                    second=1,
                    microsecond=500000,
                ),
                max_value=datetime.datetime(
                    year=2020,
                    month=1,
                    day=1,
                    hour=1,
                    minute=1,
                    second=1,
                    microsecond=500000,
                ),
            ),
        )
        assert isinstance(actual_timestamp_ntz, datetime.datetime)
        assert actual_timestamp_ntz == datetime.datetime(
            year=2020,
            month=1,
            day=1,
            hour=1,
            minute=1,
            second=1,
            microsecond=500000,
        )

        actual_timestamp = generate_fake_value(dtype=TimestampType(), fake=fake)
        assert actual_timestamp.tzinfo is not None

        actual_timestamp_ntz = generate_fake_value(dtype=TimestampNTZType(), fake=fake)
        assert actual_timestamp_ntz.tzinfo is None

        actual_int = generate_fake_value(
            dtype=IntegerType(),
            fake=fake,
            nullable=False,
            constraint=IntegerConstraint(allowed_values=[3]),
        )
        expected_int = 3
        assert actual_int == expected_int

        actual_struct = generate_fake_value(
            dtype=StructType(),
            fake=fake,
            nullable=False,
            constraint=StructConstraint(allowed_values=[{"a": 1, "b": False}]),
        )
        expected_struct = {"a": 1, "b": False}
        assert actual_struct == expected_struct

        # Test with a dict constraint
        actual_struct = generate_fake_value(
            dtype=StructType(
                fields=[
                    StructField(name="f1", dataType=IntegerType(), nullable=True),
                    StructField(name="g2", dataType=StringType()),
                ]
            ),
            fake=fake,
            nullable=False,
            constraint={
                "element_constraints": {
                    "f1": {"null_chance": 1.0},
                    "g2": {"string_type": "email"},
                }
            },
        )
        assert isinstance(actual_struct, dict)
        assert actual_struct["f1"] is None
        assert is_valid_email(actual_struct["g2"])


def test_generate_fake_dataframe(spark: SparkSession, fake: Faker) -> None:
    schema_str = """
    array_col: array<integer>,
    binary_col: binary,
    boolean_col: boolean,
    byte_col: byte,
    date_col: date,
    daytimeinterval_col_1: interval day,
    daytimeinterval_col_2: interval hour to second,
    decimal_col_1: decimal(1,0),
    decimal_col_2: decimal(28,10),
    double_col: double,
    float_col: float,
    integer_col: integer,
    long_col: long,
    short_col: short,
    string_col: string,
    struct_col: struct<
        nested_integer: integer,
        nested_string: string
    >,
    timestamp_col_1: timestamp,
    timestamp_col_2: timestamp,
    timestamp_ntz_col: timestamp_ntz
    """
    rows = 100

    # Verify that generate_fake_dataframe does not blow up if constraints are not provided
    # and that it generates a DataFrame with the correct schema
    # and the expected number of rows
    actual = generate_fake_dataframe(
        schema=schema_str,
        spark=spark,
        fake=fake,
        rows=100,
    )
    assert actual.count() == rows
    assert actual.schema == spark.createDataFrame([], schema=schema_str).schema

    # Then check that constraints actually work
    actual = generate_fake_dataframe(
        schema=schema_str,
        spark=spark,
        fake=fake,
        constraints={
            "array_col": ArrayConstraint(
                element_constraint=IntegerConstraint(min_value=1, max_value=1),
                min_length=2,
                max_length=2,
            ),
            "binary_col": BinaryConstraint(min_length=4, max_length=4),
            "boolean_col": BooleanConstraint(true_chance=1.0),
            "byte_col": ByteConstraint(min_value=1, max_value=1),
            "date_col": DateConstraint(
                min_value=datetime.date(year=2020, month=1, day=1),
                max_value=datetime.date(year=2020, month=1, day=1),
            ),
            "daytimeinterval_col_1": DayTimeIntervalConstraint(
                min_value=datetime.timedelta(days=2),
                max_value=datetime.timedelta(days=2, hours=2),
            ),
            "daytimeinterval_col_2": DayTimeIntervalConstraint(
                min_value=datetime.timedelta(hours=1, seconds=1),
                max_value=datetime.timedelta(hours=1, seconds=1),
            ),
            "decimal_col_1": DecimalConstraint(
                min_value=Decimal("2.1"), max_value=Decimal("2.1")
            ),
            "decimal_col_2": DecimalConstraint(
                min_value=Decimal("1111.2222"), max_value=Decimal("1111.2222")
            ),
            "double_col": DoubleConstraint(min_value=1.0, max_value=1.0),
            "float_col": FloatConstraint(min_value=1.0, max_value=1.0),
            "integer_col": IntegerConstraint(min_value=1, max_value=1),
            "long_col": LongConstraint(min_value=30000000005, max_value=30000000005),
            "short_col": ShortConstraint(min_value=1, max_value=1),
            "string_col": StringConstraint(
                string_type="any", min_length=5, max_length=5
            ),
            "struct_col": StructConstraint(
                element_constraints={
                    "nested_integer": IntegerConstraint(min_value=1, max_value=1),
                    "nested_string": StringConstraint(null_chance=1.0),
                }
            ),
            "timestamp_col_1": TimestampConstraint(
                min_value=datetime.datetime(
                    year=2020, month=1, day=1, hour=2, minute=3, second=4, microsecond=5
                ),
                max_value=datetime.datetime(
                    year=2020, month=1, day=1, hour=2, minute=3, second=4, microsecond=5
                ),
            ),
            "timestamp_col_2": TimestampConstraint(
                min_value=datetime.datetime(
                    year=2020,
                    month=1,
                    day=1,
                    hour=2,
                    minute=3,
                    second=4,
                    microsecond=5,
                    tzinfo=zoneinfo.ZoneInfo("Europe/Helsinki"),
                ),
                max_value=datetime.datetime(
                    year=2020,
                    month=1,
                    day=1,
                    hour=2,
                    minute=3,
                    second=4,
                    microsecond=5,
                    tzinfo=zoneinfo.ZoneInfo("Europe/Helsinki"),
                ),
            ),
            "timestamp_ntz_col": TimestampNTZConstraint(
                min_value=datetime.datetime(
                    year=2021, month=1, day=1, hour=2, minute=3, second=4, microsecond=5
                ),
                max_value=datetime.datetime(
                    year=2021, month=1, day=1, hour=2, minute=3, second=4, microsecond=5
                ),
            ),
        },
        rows=rows,
    )

    actual_schema = actual.schema
    expected_schema = spark.createDataFrame([], schema=schema_str).schema
    assert_schema_equal(
        actual=actual_schema,
        expected=expected_schema,
    )

    actual_collected = actual.collect()

    actual_array_col = [row.array_col for row in actual_collected]
    expected_array_col = [[1, 1] for _ in range(rows)]
    assert actual_array_col == expected_array_col

    actual_binary_col_lens = [len(row.binary_col) for row in actual_collected]
    expected_binary_col_lens = [4 for _ in range(rows)]
    assert actual_binary_col_lens == expected_binary_col_lens

    actual_boolean_col = [row.boolean_col for row in actual_collected]
    expected_boolean_col = [True for _ in range(rows)]
    assert actual_boolean_col == expected_boolean_col

    actual_byte_col = [row.byte_col for row in actual_collected]
    expected_byte_col = [1 for _ in range(rows)]
    assert actual_byte_col == expected_byte_col

    actual_date_col = [row.date_col for row in actual_collected]
    expected_date_col = [datetime.date(year=2020, month=1, day=1) for _ in range(rows)]
    assert actual_date_col == expected_date_col

    actual_daytimeinterval_col_1 = [
        row.daytimeinterval_col_1 for row in actual_collected
    ]
    expected_daytimeinterval_col_1 = [datetime.timedelta(days=2) for _ in range(rows)]
    assert actual_daytimeinterval_col_1 == expected_daytimeinterval_col_1

    actual_daytimeinterval_col_2 = [
        row.daytimeinterval_col_2 for row in actual_collected
    ]
    expected_daytimeinterval_col_2 = [
        datetime.timedelta(hours=1, seconds=1) for _ in range(rows)
    ]
    assert actual_daytimeinterval_col_2 == expected_daytimeinterval_col_2

    actual_decimal_col_1 = [row.decimal_col_1 for row in actual_collected]
    expected_decimal_col_1 = [Decimal("2") for _ in range(rows)]
    assert actual_decimal_col_1 == expected_decimal_col_1

    actual_decimal_col_2 = [row.decimal_col_2 for row in actual_collected]
    expected_decimal_col_2 = [Decimal("1111.2222") for _ in range(rows)]
    assert actual_decimal_col_2 == expected_decimal_col_2

    actual_double_col = [row.double_col for row in actual_collected]
    expected_double_col = [1.0 for _ in range(rows)]
    assert actual_double_col == expected_double_col

    actual_float_col = [row.float_col for row in actual_collected]
    expected_float_col = [1.0 for _ in range(rows)]
    assert actual_float_col == expected_float_col

    actual_integer_col = [row.integer_col for row in actual_collected]
    expected_integer_col = [1 for _ in range(rows)]
    assert actual_integer_col == expected_integer_col

    actual_long_col = [row.long_col for row in actual_collected]
    expected_long_col = [30000000005 for _ in range(rows)]
    assert actual_long_col == expected_long_col

    actual_short_col = [row.short_col for row in actual_collected]
    expected_short_col = [1 for _ in range(rows)]
    assert actual_short_col == expected_short_col

    actual_string_col = [row.string_col for row in actual_collected]
    for val in actual_string_col:
        assert isinstance(val, str)
        assert len(val) == 5
        for c in val:
            assert c in ALPHABET

    actual_struct_col = [row.struct_col for row in actual_collected]
    expected_struct_col = [
        Row(nested_integer=1, nested_string=None) for _ in range(rows)
    ]
    assert actual_struct_col == expected_struct_col

    actual_timestamp_col_1 = [row.timestamp_col_1 for row in actual_collected]
    expected_timestamp_col_1 = [
        datetime.datetime(
            year=2020, month=1, day=1, hour=2, minute=3, second=4, microsecond=5
        )
        for _ in range(rows)
    ]
    assert actual_timestamp_col_1 == expected_timestamp_col_1

    actual_timestamp_col_2 = [
        row.timestamp_col_2.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        for row in actual_collected
    ]
    expected_timestamp_col_2 = [
        datetime.datetime(
            year=2020,
            month=1,
            day=1,
            hour=2,
            minute=3,
            second=4,
            microsecond=5,
            tzinfo=zoneinfo.ZoneInfo("Europe/Helsinki"),
        )
        for _ in range(rows)
    ]
    assert actual_timestamp_col_2 == expected_timestamp_col_2

    actual_timestamp_ntz_col = [row.timestamp_ntz_col for row in actual_collected]
    expected_timestamp_ntz_col = [
        datetime.datetime(
            year=2021, month=1, day=1, hour=2, minute=3, second=4, microsecond=5
        )
        for _ in range(rows)
    ]
    assert actual_timestamp_ntz_col == expected_timestamp_ntz_col


def test_generate_fake_string_with_custom_alphabet(fake: Faker) -> None:
    # Custom alphabet works for "any" string type
    constraint = StringConstraint(
        string_type="any", min_length=10, max_length=10, alphabet="abc123"
    )
    for _ in range(100):
        result = _generate_fake_string(fake=fake, constraint=constraint)
        assert isinstance(result, str)
        assert len(result) == 10
        for c in result:
            assert c in "abc123"

    # Omitting alphabet uses the default ALPHABET
    constraint = StringConstraint(string_type="any", min_length=10, max_length=10)
    for _ in range(100):
        result = _generate_fake_string(fake=fake, constraint=constraint)
        assert isinstance(result, str)
        assert len(result) == 10
        for c in result:
            assert c in ALPHABET

    # Custom alphabet is not used for other string types, especially "uuid4"
    constraint = StringConstraint(
        string_type="uuid4",
        alphabet="abc123",
    )
    result = _generate_fake_string(fake=fake, constraint=constraint)
    assert len(result) == 36
    assert result.count("-") == 4
    for c in result:
        assert c in UUID_ALPHABET


def test_edge_cases(spark: SparkSession, fake: Faker) -> None:
    # Test empty allowed values
    with pytest.raises(ValueError, match="Empty list of allowed values specified"):
        generate_fake_value(
            dtype=IntegerType(),
            fake=fake,
            constraint=IntegerConstraint(allowed_values=[]),
        )

    # Test unsupported dtype validation
    with pytest.raises(ValueError, match="Unsupported dtype"):
        _validate_dtype_and_constraint(
            dtype=None,  # type: ignore
            constraint=None,
        )

    # Test unsupported dtype in generate_fake_value
    class UnsupportedType:
        pass

    with pytest.raises(ValueError, match="Unsupported dtype"):
        generate_fake_value(
            dtype=UnsupportedType(),  # type: ignore
            fake=fake,
        )

    # Verify that generate_fake_dataframe works without providing Faker or constraints
    schema_str = "id: int, name: string"
    df = generate_fake_dataframe(
        schema=schema_str,
        rows=5,
        spark=spark,
    )
    assert df.count() == 5
    assert df.schema == spark.createDataFrame([], schema=schema_str).schema


def test_timestamp_edge_cases(fake: Faker) -> None:
    # Test timezone handling with NTZ timestamp when min/max values have timezones
    actual = generate_fake_value(
        dtype=TimestampNTZType(),
        fake=fake,
        constraint=TimestampNTZConstraint(
            min_value=datetime.datetime(
                year=2020, month=1, day=1, tzinfo=datetime.timezone.utc
            ),
            max_value=datetime.datetime(
                year=2020, month=1, day=1, tzinfo=datetime.timezone.utc
            ),
        ),
    )
    assert isinstance(actual, datetime.datetime)
    assert actual.tzinfo is None

    # Test timestamp generation with various timezone configurations
    actual = generate_fake_value(
        dtype=TimestampType(),
        fake=fake,
        constraint=TimestampConstraint(
            min_value=datetime.datetime(2020, 1, 1),  # No timezone
            max_value=datetime.datetime(2020, 1, 1),  # No timezone
            tzinfo=datetime.timezone.utc,  # Explicit timezone in constraint
        ),
    )
    assert isinstance(actual, datetime.datetime)
    assert actual.tzinfo == datetime.timezone.utc


def test_unknown_string_type(fake: Faker) -> None:
    # Test handling of unknown string type
    with pytest.raises(ValueError, match="Unknown string type"):
        _generate_fake_string(
            fake=fake,
            constraint=StringConstraint(string_type="non_existent_type"),  # type: ignore
        )


def test_daytime_interval_types(fake: Faker) -> None:
    # Test different DayTimeIntervalType field types
    interval = datetime.timedelta(days=2, hours=3, minutes=30, seconds=15)

    # Test DAY field type
    result = generate_fake_value(
        dtype=DayTimeIntervalType(
            startField=DayTimeIntervalType.DAY, endField=DayTimeIntervalType.DAY
        ),
        fake=fake,
        constraint=DayTimeIntervalConstraint(
            min_value=interval,
            max_value=interval,
        ),
    )
    assert isinstance(result, datetime.timedelta)
    assert result.days == interval.days
    assert result.seconds == 0  # Hours/minutes/seconds should be truncated

    # Test HOUR field type
    result = generate_fake_value(
        dtype=DayTimeIntervalType(
            startField=DayTimeIntervalType.HOUR, endField=DayTimeIntervalType.HOUR
        ),
        fake=fake,
        constraint=DayTimeIntervalConstraint(
            min_value=interval,
            max_value=interval,
        ),
    )
    assert isinstance(result, datetime.timedelta)
    assert result.seconds % 3600 == 0  # Minutes/seconds should be truncated

    # Test MINUTE field type
    result = generate_fake_value(
        dtype=DayTimeIntervalType(
            startField=DayTimeIntervalType.MINUTE, endField=DayTimeIntervalType.MINUTE
        ),
        fake=fake,
        constraint=DayTimeIntervalConstraint(
            min_value=interval,
            max_value=interval,
        ),
    )
    assert isinstance(result, datetime.timedelta)
    assert result.seconds % 60 == 0  # Only seconds should be truncated


def test_timestamp_microsecond_edge_cases(fake: Faker) -> None:
    # Test microsecond adjustment when timestamp is outside range
    min_dt = datetime.datetime(2020, 1, 1, microsecond=500000)
    max_dt = datetime.datetime(2020, 1, 1, microsecond=600000)

    # Force Faker to generate a timestamp that needs microsecond adjustment
    for _ in range(100):  # We need multiple attempts since Faker's generation is random
        result = generate_fake_value(
            dtype=TimestampType(),
            fake=fake,
            constraint=TimestampConstraint(
                min_value=min_dt,
                max_value=max_dt,
            ),
        )
        assert isinstance(result, datetime.datetime)
        assert result.microsecond >= min_dt.microsecond
        assert result.microsecond <= max_dt.microsecond


def test_convert_dict_to_constraint(fake: Faker) -> None:
    # Test basic conversion for simple types
    result = _convert_dict_to_constraint(
        constraint={"min_value": 1, "max_value": 10}, dtype=IntegerType()
    )
    assert isinstance(result, IntegerConstraint)
    assert result.min_value == 1
    assert result.max_value == 10

    # Test array type with element constraints
    result = _convert_dict_to_constraint(
        constraint={
            "min_length": 2,
            "max_length": 5,
            "element_constraint": {"min_value": 0, "max_value": 100},
        },
        dtype=ArrayType(elementType=IntegerType()),
    )
    assert isinstance(result, ArrayConstraint)
    assert result.min_length == 2
    assert result.max_length == 5
    assert isinstance(result.element_constraint, IntegerConstraint)
    assert result.element_constraint.min_value == 0  # type: ignore
    assert result.element_constraint.max_value == 100  # type: ignore

    # Test struct type with nested constraints
    result = _convert_dict_to_constraint(
        constraint={
            "element_constraints": {
                "age": {"min_value": 0, "max_value": 120},
                "name": {"string_type": "name"},
            }
        },
        dtype=StructType(
            [StructField("age", IntegerType()), StructField("name", StringType())]
        ),
    )
    assert isinstance(result, StructConstraint)
    assert isinstance(result.element_constraints["age"], IntegerConstraint)
    assert result.element_constraints["age"].min_value == 0
    assert result.element_constraints["age"].max_value == 120
    assert isinstance(result.element_constraints["name"], StringConstraint)
    assert result.element_constraints["name"].string_type == "name"

    # Test None constraint
    result = _convert_dict_to_constraint(constraint=None, dtype=IntegerType())
    assert result is None

    # Test invalid constraint type
    with pytest.raises(ValueError, match="Constraint must be a dictionary or None"):
        _convert_dict_to_constraint(constraint=[], dtype=IntegerType())  # type: ignore

    # Test unsupported dtype
    with pytest.raises(ValueError, match="Unsupported dtype"):
        _convert_dict_to_constraint(
            constraint={"min_value": 1},
            dtype=None,  # type: ignore
        )

    # Test invalid element_constraints type
    with pytest.raises(
        ValueError, match="element_constraints must be a dictionary or None"
    ):
        _convert_dict_to_constraint(
            constraint={"element_constraints": []},  # type: ignore
            dtype=StructType([StructField("field", IntegerType())]),
        )

    # Test every supported dtype with default constraints when given empty dict
    for dtype, expected_constraint in [
        (ArrayType(elementType=IntegerType()), ArrayConstraint()),
        (BinaryType(), BinaryConstraint()),
        (BooleanType(), BooleanConstraint()),
        (ByteType(), ByteConstraint()),
        (DateType(), DateConstraint()),
        (DayTimeIntervalType(), DayTimeIntervalConstraint()),
        (DecimalType(scale=2), DecimalConstraint()),
        (DoubleType(), DoubleConstraint()),
        (FloatType(), FloatConstraint()),
        (IntegerType(), IntegerConstraint()),
        (LongType(), LongConstraint()),
        (ShortType(), ShortConstraint()),
        (StringType(), StringConstraint()),
        (
            StructType(fields=[StructField(name="field", dataType=IntegerType())]),
            StructConstraint(),
        ),
        (TimestampNTZType(), TimestampNTZConstraint()),
        (TimestampType(), TimestampConstraint()),
    ]:
        result = _convert_dict_to_constraint(
            constraint={},
            dtype=dtype,
        )
        assert isinstance(result, type(expected_constraint))
        assert result == expected_constraint
