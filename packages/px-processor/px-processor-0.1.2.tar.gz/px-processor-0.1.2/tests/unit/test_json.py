import pytest
from pydantic import BaseModel

from src.processor import InvalidInputError
from src.processor.json.main import JSONValidator


class TestModel(BaseModel):
    name: str
    age: int

def test_valid_json() -> None:
    input_data: dict[str, str |int] = {"name": "John", "age": 30}
    validator = JSONValidator(model=TestModel, input_=input_data)
    assert validator.validate() is True
    assert validator.data.name == "John"
    assert validator.data.age == 30

def test_invalid_json_missing_field() -> None:
    input_data: dict[str, str] = {"name": "John"}
    with pytest.raises(expected_exception=InvalidInputError) as exc_info:
        JSONValidator(model=TestModel, input_=input_data)
    assert "Mandatory field age in input" in str(exc_info.value)

def test_invalid_json_wrong_type() -> None:
    input_data: dict[str, str] = {"name": "John", "age": "thirty"}
    with pytest.raises(expected_exception=InvalidInputError) as exc_info:
        JSONValidator(model=TestModel, input_=input_data)
    assert "Mandatory field age in input" in str(exc_info.value)

def test_invalid_json_extra_field() -> None:
    input_data: dict[str, str | int] = {"name": "John", "age": 30, "extra": "field"}
    validator = JSONValidator(model=TestModel, input_=input_data)
    assert validator.validate() is True
    assert validator.data.name == "John"
    assert validator.data.age == 30

def test_empty_json() -> None:
    input_data: dict[str, str] = {}
    with pytest.raises(expected_exception=InvalidInputError) as exc_info:
        JSONValidator(model=TestModel, input_=input_data)
    assert "Mandatory field name in input" in str(exc_info.value)
    assert "Mandatory field age in input" in str(exc_info.value)

def test_multiple_errors() -> None:
    input_data: dict[str, int | str] = {"name": 123, "age": "thirty"}
    with pytest.raises(InvalidInputError) as exc_info:
        JSONValidator(TestModel, input_data)
    assert "Mandatory field name in input" in str(exc_info.value)
    assert "Mandatory field age in input" in str(exc_info.value)
