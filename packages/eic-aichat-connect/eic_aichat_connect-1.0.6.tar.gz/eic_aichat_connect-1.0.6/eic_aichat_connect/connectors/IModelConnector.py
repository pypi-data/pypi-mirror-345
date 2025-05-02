# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from ..data.version1.ModelRequestV1 import ModelRequestV1
from ..data.version1.ModelResponseV1 import ModelResponseV1

class IModelConnector(ABC):

    @abstractmethod
    def execute_request(self, model_request: ModelRequestV1) -> ModelResponseV1:
        raise NotImplementedError("Method from interface definition")
