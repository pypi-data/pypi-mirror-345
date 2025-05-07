from __future__ import annotations

import dataclasses

import typing_extensions as typing

import sila.server as sila

from .custom_data_type import CustomDataType


@dataclasses.dataclass
class DataTypeDefinition(sila.data_types.DataTypeDefinition):
    """
    A data type definition.

    Args:
      identifier: The identifier of the data type definition.
      display_name: The display name of the data type definition.
      description: The description of the data type definition.
      fields_by_identifier: A dictionary mapping field identifiers to field names.
      factory: A factory function to create instances of the custom data type.
      data_type: The data type of the data type definition.
    """

    fields_by_identifier: dict[str, str] = dataclasses.field(repr=False, default_factory=dict)

    factory: type[CustomDataType] = dataclasses.field(repr=False, default=CustomDataType)

    def __post_init__(self, data_type: sila.data_types.DataType):
        super().__post_init__(data_type)

        self.identifiers_by_field = {field: identifier for identifier, field in self.fields_by_identifier.items()}

    @typing.override
    def encode(self, value: CustomDataType | dict, field_number: int | None = None) -> bytes:
        values = dataclasses.asdict(value) if isinstance(value, CustomDataType) else value
        values = {self.identifiers_by_field.get(field, field): value for field, value in values.items()}

        if isinstance(self.message.elements[0].data_type, sila.data_types.Structure):
            values = {self.identifier: values}

        return super().encode(values, field_number=field_number)

    @typing.override
    def decode(self, data: bytes) -> CustomDataType:
        values = super().decode(data)

        if isinstance(self.message.elements[0].data_type, sila.data_types.Structure):
            values = values.get(self.identifier, values)

        values = {self.fields_by_identifier.get(identifier, identifier): value for identifier, value in values.items()}

        return self.factory(**values)
