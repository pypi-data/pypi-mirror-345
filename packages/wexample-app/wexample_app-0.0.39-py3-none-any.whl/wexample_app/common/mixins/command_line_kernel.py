from __future__ import annotations

from typing import cast, Type, List, Dict, Any, TYPE_CHECKING

from pydantic import PrivateAttr

from wexample_app.const.types import CommandLineArgumentsList

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest


class CommandLineKernel:
    _sys_argv: list[str] = PrivateAttr(default_factory=list)
    _sys_argv_start_index: int = 1
    _sys_argv_end_index: int | None = None
    _core_argv: list[str] = PrivateAttr(default_factory=list)

    def _init_command_line_kernel(self):
        import sys

        self._sys_argv = sys.argv.copy()

        self._handle_core_args()

    def _get_core_args(self) -> List[Dict[str, Any]]:
        return []

    def _handle_core_args(self):
        from wexample_helpers.helpers.args import args_shift_one

        for arg_config in self._get_core_args():
            if args_shift_one(self._sys_argv, arg_config["arg"], True) is not None:
                setattr(self, arg_config["attr"], arg_config["value"])

    def exec_argv(self):
        """
        Main entrypoint from command line calls.
        May not be called by an internal script.
        """
        command_requests = self._build_command_requests_from_arguments(
            self._sys_argv[self._sys_argv_start_index:self._sys_argv_end_index]
        )

        from wexample_app.response.abstract_response import AbstractResponse
        responses: list["AbstractResponse"] = []
        for command_request in command_requests:
            responses.append(self.execute_kernel_command(command_request))

    def _build_command_requests_from_arguments(self, arguments: CommandLineArgumentsList) -> list["CommandRequest"]:
        # By default, allow one request per execution call.
        return self._build_single_command_request_from_arguments(arguments)

    def _build_single_command_request_from_arguments(self, arguments: CommandLineArgumentsList):
        from wexample_app.common.command_request import CommandRequest
        class_definition = cast(Type[CommandRequest], self._get_command_request_class())

        return [
            class_definition(
                kernel=self,
                name=arguments[0],
                arguments=arguments[1:])
        ]
