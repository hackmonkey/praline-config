import os
import textwrap
from dataclasses import dataclass

import pytest
from config import config_from_yaml

from praline.config import AppConfigBase
from praline.model import SecureValue


@pytest.fixture
def config_yaml() -> str:
    return textwrap.dedent(
        r"""
            env:
                my_username: "USERNAME"
            secure_env:
                my_password: "SECRET_PASSWORD"
        """
    )


@dataclass
class AppConfig(AppConfigBase):
    ...


@pytest.fixture
def setup_teardown(config_yaml):
    os.environ["USERNAME"] = "test-user"
    os.environ["SECRET_PASSWORD"] = "12345"

    AppConfig.load(config=[config_from_yaml(config_yaml)])


def test_env(setup_teardown):
    app_config: AppConfig = AppConfig.instance()
    assert str(app_config.env.get("my_username")) == "test-user"
    assert app_config.env.get("my_username").value() == "test-user"
    assert app_config.env.get("unmapped_variable") is None


def test_secure_env(setup_teardown):
    app_config: AppConfig = AppConfig.instance()
    assert str(app_config.secure_env.get("my_password")) == SecureValue.mask_str
    assert app_config.secure_env.get("my_password").value() == "12345"
    assert app_config.secure_env.get("unmapped_secure_variable") is None
