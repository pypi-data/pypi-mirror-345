from pathlib import Path
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from vedro.core import Config
from vedro.events import ConfigLoadedEvent

from ._utils import dispatcher, vedro_fn

__all__ = ("dispatcher",)  # fixtures


@pytest.mark.usefixtures(vedro_fn.__name__)
async def test_register_scenario_loader(*, dispatcher):
    with given:
        config_ = Mock(Config)
        event = ConfigLoadedEvent(Path("."), config_)

    with when:
        await dispatcher.fire(event)

    with then:
        assert config_.Registry.ScenarioLoader.register.assert_called_once() is None
        assert len(config_.mock_calls) == 1
