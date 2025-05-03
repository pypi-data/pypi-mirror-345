import os

import pytest
from unittest import mock

from ddsapi.api import Config, EnvVarNames


def _read_config_mock(*ar) -> dict:
    return {
        "url": "url_from_file",
        "key": "key_from_file",
        "verify": "0",
        "cachedir": "cachedir_from_file",
    }


def _read_config_mock2(*ar) -> dict:
    return {
        "url": "url_from_file",
        "key": "key_from_file",
        "verify": "0",
    }


@mock.patch.dict(os.environ, {EnvVarNames.URL: "dds-url"})
@mock.patch("ddsapi.api.read_config", return_value={})
def test_get_url_from_env_var(read_config):
    conf = Config()
    assert conf.url == "dds-url"
    assert conf.key is None
    assert conf.cachedir == os.path.expanduser(
        os.path.join("~", Config._CACHE_FILENAME)
    )
    assert conf.verify == 1


@mock.patch.dict(os.environ, {EnvVarNames.KEY: "dds-key"})
@mock.patch("ddsapi.api.read_config", return_value={})
def test_get_key_from_env_var(read_config):
    conf = Config()
    assert conf.key == "dds-key"
    assert conf.url is None
    assert conf.cachedir == os.path.expanduser(
        os.path.join("~", Config._CACHE_FILENAME)
    )
    assert conf.verify == 1


@mock.patch.dict(os.environ, {EnvVarNames.CACHEDIR: "dds-cache"})
@mock.patch("ddsapi.api.read_config", return_value={})
def test_get_cache_from_env_var(read_config):
    conf = Config()
    assert conf.cachedir == "dds-cache"
    assert conf.key is None
    assert conf.url is None
    assert conf.verify == 1


@mock.patch("ddsapi.api.read_config", _read_config_mock)
def test_read_conf_from_rc_file():
    conf = Config()
    assert conf.key == "key_from_file"
    assert conf.url == "url_from_file"
    assert conf.cachedir == "cachedir_from_file"
    assert conf.verify == 0


@mock.patch.dict(os.environ, {EnvVarNames.CACHEDIR: "dds-cache"})
@mock.patch("ddsapi.api.read_config", _read_config_mock2)
def test_conf_from_file_overwrites():
    conf = Config()
    assert conf.key == "key_from_file"
    assert conf.url == "url_from_file"
    assert conf.cachedir == "dds-cache"
    assert conf.verify == 0


@mock.patch.dict(os.environ, {EnvVarNames.KEY: "key0"})
@mock.patch("ddsapi.api.read_config", return_value={"key": "key1"})
def test_user_defined_overwrites_all(read_config):
    conf = Config(key="key2")
    assert conf.key == "key2"
    assert conf.url is None
    assert conf.cachedir == os.path.expanduser(
        os.path.join("~", Config._CACHE_FILENAME)
    )
    assert conf.verify == 1
