# -*- coding: utf-8 -*-
from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor

# from eic_aichat_connect.operations.version1.ModelConnectionOperationsV1 import ModelConnectionOperationsV1
from eic_aichat_connect.services.ModelConnectionService import ModelConnectionService

class AIChatConnectFactory(Factory):
    __ServiceDescriptor = Descriptor('aichatconnect', 'service', 'default', 'default', '1.0')
    # __OperationsDescriptor = Descriptor('aichatconnect', 'operations', 'default', 'default', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__ServiceDescriptor, ModelConnectionService)
        # self.register_as_type(self.__OperationsDescriptor, ModelConnectionOperationsV1)
