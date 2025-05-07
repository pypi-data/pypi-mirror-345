import os.path
from typing import Optional
from typing import TYPE_CHECKING

from wexample_app.runner.abstract_command_runner import AbstractCommandRunner

if TYPE_CHECKING:
    from wexample_app.common.command import Command
    from wexample_app.common.command_request import CommandRequest


class PythonCommandRunner(AbstractCommandRunner):

    def will_run(self, request: "CommandRequest") -> bool:
        from pathlib import Path
        from wexample_helpers.const.globals import FILE_EXTENSION_PYTHON

        path = request.resolver.build_command_path(request)
        if path is None:
            return False
        
        file_path = Path(path)
        file_extension = file_path.suffix.lower()

        return file_extension == f".{FILE_EXTENSION_PYTHON}"

    def build_command(self, request: "CommandRequest") -> Optional["Command"]:
        import importlib.util
        from wexample_app.common.command import Command

        path = request.resolver.build_command_path(request)

        if not os.path.exists(path):
            return None

        # Import module and load function.
        spec = importlib.util.spec_from_file_location(path, path)

        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        function = getattr(module, request.resolver.build_command_function_name(request), None)

        return Command(
            kernel=self.kernel,
            function=function
        ) if function is not None else None