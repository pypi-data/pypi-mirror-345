from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from vedro import Scenario
from vedro.core import Dispatcher

from vedro_fn._scenario_loader import ScenarioLoader as Loader

from ._utils import dispatcher, loader, run_scenarios, tmp_scn_dir

__all__ = ("loader", "tmp_scn_dir", "dispatcher",)  # fixtures


async def test_load_parameterized_scenario(*, loader: Loader, tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            from vedro import params
            from vedro_fn import scenario

            @scenario([
                params("Bob"),
                params("Alice"),
            ])
            def create_user(username):
                pass
        '''))

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 2

        for idx, scenario in enumerate(scenarios, start=1):
            assert issubclass(scenario, Scenario)
            assert scenario.subject == "create user"
            assert scenario.__name__ == f"Scenario_create_user_{idx}_VedroScenario"


async def test_load_parameterized_scenarios(*, loader: Loader, tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            from vedro import params
            from vedro_fn import scenario

            @scenario([params("Bob"), params("Alice")])
            def create_user(username):
                pass

            @scenario([params("Bob"), params("Alice")])
            async def update_user(username):
                pass
        '''))

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 4

        for idx, scenario in enumerate(scenarios[:2], start=1):
            assert issubclass(scenario, Scenario)
            assert scenario.subject == "create user"
            assert scenario.__name__ == f"Scenario_create_user_{idx}_VedroScenario"

        for idx, scenario in enumerate(scenarios[2:], start=1):
            assert issubclass(scenario, Scenario)
            assert scenario.subject == "update user"
            assert scenario.__name__ == f"Scenario_update_user_{idx}_VedroScenario"


@pytest.mark.parametrize("fn_def", ["def", "async def"])
async def test_run_passed_parameterized_scenario(fn_def: str, *, loader: Loader,
                                                 tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro import params
            from vedro_fn import scenario
            @scenario([params("Bob"), params("Alice")])
            {fn_def} create_user(username):
                assert username
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == report.passed == 2


@pytest.mark.parametrize("fn_def", ["def", "async def"])
async def test_run_failed_parameterized_scenario(fn_def: str, *, loader: Loader,
                                                 tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro import params
            from vedro_fn import scenario
            @scenario([params("Bob"), params("Alice")])
            {fn_def} create_user(username):
                assert username == "Bob"
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == 2
        assert report.passed == 1
        assert report.failed == 1


@pytest.mark.parametrize("fn_def", ["def", "async def"])
async def test_run_skipped_parameterized_scenario(fn_def: str, *, loader: Loader,
                                                  tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro import params, skip
            from vedro_fn import scenario
            @scenario[skip]([params("Bob"), params("Alice")])
            {fn_def} create_user(username):
                assert username
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == report.skipped == 2


async def test_run_partially_skipped_parameterized_scenario(*, loader: Loader, tmp_scn_dir: Path,
                                                            dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            from vedro import params, skip
            from vedro_fn import scenario
            @scenario([
                params[skip]("Bob"),
                params("Alice"),
            ])
            def create_user(username):
                assert username
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == 2
        assert report.passed == 1
        assert report.skipped == 1
