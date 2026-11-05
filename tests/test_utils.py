import pytest
from app.utils import obj_to_dict, get_server_conf, get_server_port, get_all_users_count
from tests.mock_ice import MockMeta, MockServer


class SampleSlotsClass:
    __slots__ = ["name", "value"]

    def __init__(self, name, value):
        self.name = name
        self.value = value


class SampleDictClass:
    def __init__(self, key, num):
        self.key = key
        self.num = num


def test_obj_to_dict_none():
    assert obj_to_dict(None) is None


def test_obj_to_dict_primitives():
    assert obj_to_dict("hello") == "hello"
    assert obj_to_dict(123) == 123
    assert obj_to_dict(45.67) == 45.67
    assert obj_to_dict(True) is True
    assert obj_to_dict(False) is False


def test_obj_to_dict_bytes():
    assert obj_to_dict(b"mumble") == "mumble"


def test_obj_to_dict_collections():
    assert obj_to_dict([1, "two", 3.0]) == [1, "two", 3.0]
    assert obj_to_dict((1, 2)) == [1, 2]
    assert obj_to_dict({"a": 1, "b": [2, 3]}) == {"a": 1, "b": [2, 3]}


def test_obj_to_dict_custom_objects():
    dict_obj = SampleDictClass("foo", 42)
    assert obj_to_dict(dict_obj) == {"key": "foo", "num": 42}

    slots_obj = SampleSlotsClass("bar", 99)
    assert obj_to_dict(slots_obj) == {"name": "bar", "value": 99}


def test_get_server_conf(setup_mock_ice):
    meta = setup_mock_ice
    server = meta.getServer(1)
    
    # Existing key
    assert get_server_conf(meta, server, "registername") == "Mock Server 1"
    
    # Missing server-level key falling back to meta default
    assert get_server_conf(meta, server, "timeout") == "30"
    
    # Non-existent key
    assert get_server_conf(meta, server, "unknown_key") == ""
    
    # None server
    assert get_server_conf(meta, None, "registername") == ""


def test_get_server_port(setup_mock_ice):
    meta = setup_mock_ice
    server = meta.getServer(1)
    
    # Explicit port
    assert get_server_port(meta, server) == 64738
    
    # Fallback to default port calculation
    server._conf.pop("port")
    assert get_server_port(meta, server) == 64738


def test_get_all_users_count(setup_mock_ice):
    meta = setup_mock_ice
    # Server 1 is running with 1 user, Server 2 is stopped
    assert get_all_users_count(meta) == 1
    
    # When Server 2 starts with users
    server2 = meta.getServer(2)
    server2.start()
    server2._users = [{"name": "bob", "session": 2}, {"name": "charlie", "session": 3}]
    assert get_all_users_count(meta) == 3

