from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from vedro import Scenario
from vedro.core import Dispatcher

from vedro_fn._scenario_loader import ScenarioLoader as Loader

from ._utils import dispatcher, loader, run_scenarios, tmp_scn_dir

__all__ = ("loader", "tmp_scn_dir", "dispatcher",)  # fixtures


@pytest.mark.parametrize("decorator", ["@scenario", "@scenario()"])
async def test_load_scenario(decorator: str, *, loader: Loader, tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro_fn import scenario
            {decorator}
            def create_user():
                pass
        '''))

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 1
        assert issubclass(scenarios[0], Scenario)
        assert scenarios[0].subject == "create user"
        assert scenarios[0].__name__ == "Scenario_create_user"


async def test_load_scenarios(*, loader: Loader, tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            from vedro_fn import scenario
            @scenario()
            def create_user():
                pass
            @scenario()
            async def update_user():
                pass
        '''))

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 2

        assert issubclass(scenarios[0], Scenario)
        assert scenarios[0].subject == "create user"
        assert scenarios[0].__name__ == "Scenario_create_user"

        assert issubclass(scenarios[1], Scenario)
        assert scenarios[1].subject == "update user"
        assert scenarios[1].__name__ == "Scenario_update_user"


@pytest.mark.parametrize("decorator", ["@scenario", "@scenario()"])
@pytest.mark.parametrize("fn_def", ["def", "async def"])
async def test_run_passed_scenario(decorator: str, fn_def: str, *,
                                   loader: Loader, tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro_fn import scenario
            {decorator}
            {fn_def} create_user():
                assert True
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == report.passed == 1


@pytest.mark.parametrize("decorator", ["@scenario", "@scenario()"])
@pytest.mark.parametrize("fn_def", ["def", "async def"])
async def test_run_failed_scenario(decorator: str, fn_def: str, *,
                                   loader: Loader, tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro_fn import scenario
            {decorator}
            {fn_def} create_user():
                assert False
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == report.failed == 1


@pytest.mark.parametrize("decorator", ["@scenario[skip]", "@scenario[skip]()"])
@pytest.mark.parametrize("fn_def", ["def", "async def"])
async def test_run_skipped_scenario(decorator: str, fn_def: str, *,
                                    loader: Loader, tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            from vedro import skip
            from vedro_fn import scenario
            {decorator}
            {fn_def} create_user():
                assert False
        '''))

        scenarios = await loader.load(path)

    with when:
        report = await run_scenarios(scenarios, dispatcher, project_dir=tmp_scn_dir)

    with then:
        assert report.total == report.skipped == 1
