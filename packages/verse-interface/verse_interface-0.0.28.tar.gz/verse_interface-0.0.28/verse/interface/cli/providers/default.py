import signal
import sys
from typing import Any

from verse.core import ArgParser, Context, Operation, Provider
from verse.core.spec import SpecBuilder


class Default(Provider):
    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        signal.signal(signal.SIGINT, self._signal_handler)
        self._print_welcome()
        while True:
            try:
                statement = input("> ")
                if statement.strip():
                    try:
                        if statement == "?":
                            component_name = (
                                self.get_component().component._get_name()
                            )
                            spec_builder = SpecBuilder()
                            component_spec = spec_builder.build_component_spec(
                                component_name=component_name
                            )
                            spec_builder.print(component_spec)
                        else:
                            operation = ArgParser.convert_execute_operation(
                                statement, None
                            )
                            output = self.get_component().component.__run__(
                                operation=operation
                            )
                            print(output)
                    except Exception as e:
                        print(f"{type(e).__name__}: {e}")
            except EOFError:
                print("\nExiting!")
                sys.exit(0)

    async def __arun__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        signal.signal(signal.SIGINT, self._signal_handler)
        self._print_welcome()
        while True:
            try:
                statement = input("> ")
                if statement.strip():
                    try:
                        if statement == "?":
                            component_name = (
                                self.get_component().component._get_name()
                            )
                            spec_builder = SpecBuilder()
                            component_spec = spec_builder.build_component_spec(
                                component_name=component_name
                            )
                            spec_builder.print(component_spec)
                        else:
                            operation = ArgParser.convert_execute_operation(
                                statement, None
                            )
                            output = (
                                await self.get_component().component.__arun__(
                                    operation=operation
                                )
                            )
                            print(output)
                    except Exception as e:
                        print(f"{type(e).__name__}: {e}")
            except EOFError:
                print("\nExiting!")
                sys.exit(0)

    def _print_welcome(self):
        print("Welcome to Verse CLI. Use Verse QL to run operations.")

    def _signal_handler(self, signal, frame):
        print("\nExiting!")
        sys.exit(0)
