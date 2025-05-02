# -*- coding: utf-8 -*-
from pip_services4_commons.convert import TypeCode
from pip_services4_data.validate import ObjectSchema

class ModelResponseV1Schema(ObjectSchema):
    """
    Schema to validate ModelResponseV1 defined object.
    """

    def __init__(self):
        """
        Creates an instance of schema.
        """
        super().__init__()

        self.with_optional_property('value', TypeCode.String)