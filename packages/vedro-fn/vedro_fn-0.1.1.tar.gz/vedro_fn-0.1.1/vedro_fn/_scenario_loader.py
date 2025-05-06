import os
from asyncio import iscoroutinefunction
from pathlib import Path
from types import ModuleType
from typing import Any, List, Type, cast

from vedro import Scenario
from vedro.core import ModuleLoader
from vedro.core import ScenarioLoader as BaseScenarioLoader

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("ScenarioLoader",)


class ScenarioLoader(BaseScenarioLoader):
    def __init__(self, module_loader: ModuleLoader) -> None:
        self._module_loader = module_loader

    async def load(self, path: Path) -> List[Type[Scenario]]:
        module = await self._module_loader.load(path)
        return self._collect_scenarios(module)

    def _collect_scenarios(self, module: ModuleType) -> List[Type[Scenario]]:
        loaded = []
        for name, val in module.__dict__.items():
            if not name.startswith("_") and isinstance(val, ScenarioDescriptor):
                scenarios = self._build_vedro_scenarios(val, module)
                loaded.extend(scenarios)
        return loaded

    def _build_vedro_scenarios(self, descriptor: ScenarioDescriptor,
                               module: ModuleType) -> List[Type[Scenario]]:
        if len(descriptor.params) == 0:
            scenario_cls = self._build_vedro_scenario(descriptor, module)
            return [scenario_cls]

        scenario_cls = self._build_vedro_scenario_with_params(descriptor, module)

        scenarios = []
        for idx, _ in enumerate(descriptor.params, start=1):
            scn_name = f"Scenario_{descriptor.name}_{idx}_VedroScenario"
            scenarios.append(
                # This is a temporary and dirty workaround; to be revisited after the v2 release
                # Logic adapted from the `_Meta` class in vedro/_scenario.py
                cast(Type[Scenario], scenario_cls.__init__.__globals__[scn_name])
            )
        return scenarios

    def _build_vedro_scenario(self, descriptor: ScenarioDescriptor,
                              module: ModuleType) -> Type[Scenario]:
        scenario_cls = type(self._create_scenario_name(descriptor), (Scenario,), {
            "__module__": module.__name__,
            "__file__": self._create_module_path(module),
            "subject": self._create_subject(descriptor),
            "do": self._make_do(descriptor.fn),
        })

        for decorator in descriptor.decorators:
            scenario_cls = decorator(scenario_cls)
        return scenario_cls

    def _build_vedro_scenario_with_params(self, descriptor: ScenarioDescriptor,
                                          module: ModuleType) -> Type[Scenario]:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # type: ignore
            self.__args = args
            self.__kwargs = kwargs

        for params in reversed(descriptor.params):
            __init__ = params(__init__)

        scenario_cls = type(self._create_scenario_name(descriptor), (Scenario,), {
            "__module__": module.__name__,
            "__file__": self._create_module_path(module),
            "__init__": __init__,
            "subject": self._create_subject(descriptor),
            "do": self._make_do_with_params(descriptor.fn),
        })

        for decorator in descriptor.decorators:
            scenario_cls = decorator(scenario_cls)
        return scenario_cls

    def _create_scenario_name(self, descriptor: ScenarioDescriptor) -> str:
        return f"Scenario_{descriptor.name}"

    def _create_subject(self, descriptor: ScenarioDescriptor) -> str:
        return descriptor.name.replace("_", " ")

    def _create_module_path(self, module: ModuleType) -> str:
        return os.path.abspath(str(module.__file__))

    def _make_do(self, fn: Any) -> Any:
        if iscoroutinefunction(fn):
            async def do(self) -> None:  # type: ignore
                await fn()

            return do
        else:
            def do(self) -> None:  # type: ignore
                fn()

            return do

    def _make_do_with_params(self, fn: Any) -> Any:
        if iscoroutinefunction(fn):
            async def do(self) -> None:  # type: ignore
                await fn(*self.__args, **self.__kwargs)

            return do
        else:
            def do(self) -> None:  # type: ignore
                fn(*self.__args, **self.__kwargs)

            return do
