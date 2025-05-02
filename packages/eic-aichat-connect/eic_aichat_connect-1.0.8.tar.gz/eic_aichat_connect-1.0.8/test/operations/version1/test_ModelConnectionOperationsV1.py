# # -*- coding: utf-8 -*-
# import pytest

# from pip_services4_components.config import ConfigParams
# from pip_services4_components.refer import Descriptor, References
# from pip_services4_config.connect import ConnectionParams

# from eic_aichat_connect.data.version1.ModelRequestV1 import ModelRequestV1
# #from eic_aichat_connect.data.version1.ModelResponseV1 import ModelResponseV1
# from eic_aichat_connect.operations.version1.ModelConnectionOperationsV1 import ModelConnectionOperationsV1
# from eic_aichat_connect.services.ModelConnectionService import ModelConnectionService

# PARAMS1 = ConnectionParams.from_tuples("foo", "bar")
# PARAMS2 = ConnectionParams.from_tuples("api", "mock", "model", "foobar")
# PARAMS3 = ConnectionParams.from_tuples("user", "user3", "api", "fake_api", "model", "foobar")
# PARAMS4 = ConnectionParams.from_tuples("user", "user4", "api", "mock", "model", "foobar")
# PARAMS5 = ConnectionParams.from_tuples("user", "user5")

# REQ1 = ModelRequestV1(value="foobar")
# REQ2 = ModelRequestV1(value="another request")

# class TestModelConnectionOperationsV1:
#     _mux: ModelConnectionService
#     _operations: ModelConnectionOperationsV1

#     @classmethod
#     def setup_class(cls):
#         cls._mux = ModelConnectionService()
#         cls._operations = ModelConnectionOperationsV1()

#         config = ConfigParams()
#         cls._operations.configure(config)

#         references = References.from_tuples(
#             Descriptor('aichatconnect', 'service', 'default', 'default', '1.0'), cls._mux,
#             Descriptor('aichatconnect', 'operations', 'default', 'default', '1.0'), cls._operations
#         )
#         cls._operations.set_references(references)
    
#     @classmethod
#     def teardown_class(cls):
#         pass

#     def test_operations(self):
#         """Test the basic operations"""

#         # Test get available models
#         # res0 = self._operations.get_available_models()
#         # assert "OpenAI ChatGPT 4.5" in res0
#         # assert "Perplexity Sonar" in res0

#         # Test execute request with missing params
#         res1 = self._operations.execute_request(PARAMS1, REQ1)
#         assert "ConnectionParams missing values for keys:" in res1
#         res2 = self._operations.execute_request(PARAMS2, REQ1)
#         assert "ConnectionParams missing values for keys: ['user']" in res2

#         # Test execute request with incorrect API param
#         res3 = self._operations.execute_request(PARAMS3, REQ1)
#         assert "API fake_api not found" in res3

#         # Test execute request with new connector
#         res4 = self._operations.execute_request(PARAMS4, REQ1)
#         assert "You requested: foobar" in res4
#         assert len(self._operations._connectors) == 1

#         # Test execute request with existing connector
#         res5 = self._operations.execute_request(PARAMS4, REQ2)
#         assert "You requested: another request" in res5
#         assert len(self._operations._connectors) == 1

#         # Test execute default request with no API or model params
#         # res6 = self._operations.execute_default_request(PARAMS5, REQ1)
#         # assert "OpenAI not implemented yet" in res6
#         # assert len(self._operations._connectors) == 2

#         # # Test execute default request with existing API and model params
#         # res7 = self._operations.execute_default_request(PARAMS4, REQ1)
#         # assert "OpenAI not implemented yet" in res7
#         # assert len(self._operations._connectors) == 3
