# -*- coding: utf-8 -*-
import pytest

from pip_services4_components.config import ConfigParams
from pip_services4_components.context import Context
from pip_services4_components.refer import Descriptor, References
from pip_services4_config.connect import ConnectionParams
from pip_services4_data.query import FilterParams, PagingParams

from eic_aichat_connect.connectors.MockModelConnector import MockModelConnector
from eic_aichat_connect.services.ModelConnectionService import ModelConnectionService

PARAMS1 = ConnectionParams.from_tuples("user", "user1", "api", "mock", "model", "foobar")
PARAMS2 = ConnectionParams.from_tuples("user", "user2", "api", "mock", "model", "foobar")
PARAMS3 = ConnectionParams.from_tuples("user", "user3", "api", "fake_api", "model", "foobar")
PARAMS4 = ConnectionParams.from_tuples("user", "user4", "api", "mock", "model", "foobar")

class TestModelConnectionService:
    _mux: ModelConnectionService

    @classmethod
    def setup_class(cls):
        cls._mux = ModelConnectionService()

        config = ConfigParams()
        cls._mux.configure(config)

        references = References()
        cls._mux.set_references(references)
    
    @classmethod
    def teardown_class(cls):
        pass

    def test_operations(self):
        """Test the basic operations"""
        
        # Prepare list
        connectors = []

        # Test get available models
        # res0 = self._mux.get_available_models(Context(None), FilterParams(), PagingParams())
        # assert "OpenAI ChatGPT 4.5" in res0
        # assert "Perplexity Sonar" in res0

        # Test find connector with no hash_id
        connector1 = MockModelConnector(PARAMS1)
        connectors.append(connector1)
        res1 = self._mux.find_connector(connectors, PARAMS1)
        assert res1.hash_id == connector1.hash_id

        # Test find connector with hash_id
        hash1 = connector1.hash_id
        res2 = self._mux.find_connector(connectors, PARAMS1, hash1)
        assert res2.hash_id == connector1.hash_id

        # Test create connector
        res3 = self._mux.create_connector(PARAMS2)
        connectors.append(res3)
        connector2 = MockModelConnector(PARAMS2)
        assert connector2.hash_id == res3.hash_id

        # Test create connector with incorrect API param
        try:
            res4 = self._mux.create_connector(PARAMS3)
            assert False
        except KeyError as err:
            pass

        # Test find or create connector with new connector
        res5, is_new5 = self._mux.find_or_create_connector(connectors, PARAMS4)
        connectors.append(res5)
        connector3 = MockModelConnector(PARAMS4)
        assert connector3.hash_id == res5.hash_id
        assert is_new5 is True

        # Test find or create connector with existing connector
        connector4 = MockModelConnector(PARAMS4)
        res6, is_new6 = self._mux.find_or_create_connector(connectors, PARAMS4)
        assert res6.hash_id == connector4.hash_id
        assert is_new6 is False
