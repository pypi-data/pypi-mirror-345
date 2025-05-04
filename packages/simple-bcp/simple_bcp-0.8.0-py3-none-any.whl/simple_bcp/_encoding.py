import enum
from typing import Annotated

from pydantic import BaseModel, model_validator, StringConstraints


class FieldEncodingType(enum.Enum):
    NATIVE = "-n"
    CHAR = "-c"
    UNICODE = "-w"


class BcpEncodingSettings(BaseModel):
    """
    :param field_encoding_type: Specifies the encoding mode of the downloaded data fields.
    :param field_delimiter: the field delimiter of the downloaded data. Defaults to bcp default which is `\t`.
                            not supported if `field_encoding_type` is `FieldEncodingMode.NATIVE`.
    :param row_terminator: the row terminator of the downloaded data. Defaults to bcp default which is `\n`.
                           not supported if `field_encoding_type` is `FieldEncodingMode.NATIVE`.
    """
    field_encoding_type: FieldEncodingType = FieldEncodingType.NATIVE
    field_delimiter: Annotated[str, StringConstraints(min_length=1)] | None = None
    row_terminator: Annotated[str, StringConstraints(min_length=1)] | None = None

    @model_validator(mode='after')
    def __validate(self):
        if self.field_encoding_type is FieldEncodingType.NATIVE and (
                self.field_delimiter is not None or self.row_terminator is not None):
            raise ValueError(
                "field_delimiter and row_terminator are not supported when field_encoding_type is `FieldEncodingMode.NATIVE`")
        return self
