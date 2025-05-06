import os
from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ConfigLoadedEvent, ExceptionRaisedEvent
from vedro.plugins.director.rich.utils import TracebackFilter

from ._scenario_loader import ScenarioLoader

__all__ = ("VedroFn", "VedroFnPlugin",)


class VedroFnPlugin(Plugin):
    def __init__(self, config: Type["VedroFn"]) -> None:
        super().__init__(config)
        self._show_internal_calls: bool = config.show_internal_calls
        self._tb_filter: Union[TracebackFilter, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self._on_config_loaded) \
                  .listen(ExceptionRaisedEvent, self._on_exception_raised)

    def _on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        event.config.Registry.ScenarioLoader.register(  # pragma: no branch
            lambda: ScenarioLoader(module_loader=event.config.Registry.ModuleLoader()),
            self
        )

    def _on_exception_raised(self, event: ExceptionRaisedEvent) -> None:
        if self._show_internal_calls:
            return

        if self._tb_filter is None:
            vedro_scn_module = os.path.dirname(__file__)
            self._tb_filter = TracebackFilter(modules=[vedro_scn_module])

        event.exc_info.traceback = self._tb_filter.filter_tb(event.exc_info.traceback)


class VedroFn(PluginConfig):
    plugin = VedroFnPlugin
    description = "Enables a functional-style syntax for defining Vedro scenarios"

    # Show internal calls (vedro_fn) in the traceback output
    show_internal_calls = False
