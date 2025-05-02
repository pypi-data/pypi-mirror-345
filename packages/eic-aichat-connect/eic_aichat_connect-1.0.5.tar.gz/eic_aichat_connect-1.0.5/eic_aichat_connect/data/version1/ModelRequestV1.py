# -*- coding: utf-8 -*-

class ModelRequestV1:
    """
    ModelRequestV1 data object.
    """

    def __init__(self, value: str = None, model_name: str = None):
        """
        Initializes a new instance of ModelRequestV1.

        :param value: Request value.
        """
        self.value = value
        self.model_name = model_name