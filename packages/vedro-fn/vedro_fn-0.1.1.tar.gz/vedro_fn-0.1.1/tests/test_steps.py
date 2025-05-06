import pytest

from vedro_fn import given, then, when
from vedro_fn._scenario_steps import Step


@pytest.mark.parametrize("step", [given, when, then])
def test_step_context_manager(step: Step):
    with given as cm:
        assert cm is None


@pytest.mark.asyncio
@pytest.mark.parametrize("step", [given, when, then])
async def test_step_async_context_manager(step: Step):
    async with given as cm:
        assert cm is None


@pytest.mark.parametrize("step", [given, when, then])
def test_step_call(step: Step):
    step_ = step("step")

    with step_ as cm:
        assert cm is None
        assert step_._name == "step"

    assert step_._name is None
