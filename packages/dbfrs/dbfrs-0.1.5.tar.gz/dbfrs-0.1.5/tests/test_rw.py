import dbfrs

input_data = [
    ("John", "Doe", 33, True),
    ("Jane", "Smith", 44, False),
]


def test_write_and_read():
    fields = dbfrs.Fields()
    fields.add_character_field("first_name", 20)
    fields.add_character_field("last_name", 20)
    fields.add_numeric_field("age", 20, 1)
    fields.add_logical_field("is_happy")

    dbfrs.write_dbf(fields, input_data, "test.dbf")

    fields = dbfrs.get_dbf_fields("test.dbf")
    a = fields[0].name

    count = dbfrs.get_record_count("test.dbf")
    data = dbfrs.load_dbf("test.dbf")

    assert count == len(input_data)
    assert data == input_data


def test_field_type_character():
    field = dbfrs.Field.new_character("name", 20)

    assert field.name == "name"
    assert field.type == dbfrs.FieldType.Character
    assert field.size == 20
    assert field.decimals == 0

    assert str(field.type) == "C"
    assert repr(field.type) == "FieldType.Character"


def test_field_type_numeric():
    field = dbfrs.Field.new_numeric("age", 20, 1)

    assert field.name == "age"
    assert field.type == dbfrs.FieldType.Numeric
    assert field.size == 20
    assert field.decimals == 1

    assert str(field.type) == "N"
    assert repr(field.type) == "FieldType.Numeric"


def test_field_type_logical():
    field = dbfrs.Field.new_logical("is_happy")

    assert field.name == "is_happy"
    assert field.type == dbfrs.FieldType.Logical
    assert field.size == 1
    assert field.decimals == 0

    assert str(field.type) == "L"
    assert repr(field.type) == "FieldType.Logical"
