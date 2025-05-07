from typing import Any, cast
from typing import List, Optional, Union, TYPE_CHECKING

from pydantic import BaseModel, Field, PrivateAttr

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.runner.abstract_command_runner import AbstractCommandRunner
from wexample_helpers.const.types import StringsMatch
from wexample_app.exception.command_resolver_not_found import CommandResolverNotFound
from wexample_app.exception.command_type_not_found import CommandTypeNotFound

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver


class CommandRequest(
    AbstractKernelChild,
    BaseModel
):
    name: str
    arguments: List[Union[str, int]] = Field(default_factory=list)
    path: Optional[str] = None
    type: Optional[str] = None
    _match: Optional[StringsMatch] = None
    _resolver: Optional["AbstractCommandResolver"] = PrivateAttr(default=None)
    _runner: Optional["AbstractCommandRunner"] = PrivateAttr(default=None)

    def __init__(self, kernel: "AbstractKernel", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

        self.type = self.guess_type()
        if self.type is None:
            raise CommandTypeNotFound(self.name)
            
        self.resolver = self.get_resolver()
        self.path = self.resolver.build_command_path(request=self)
        self.runner = self.guess_runner()

    @property
    def match(self) -> "StringsMatch":
        return self._match

    @match.setter
    def match(self, value: "StringsMatch") -> None:
        self._match = value

    @property
    def resolver(self) -> "AbstractCommandResolver":
        return self._resolver

    @resolver.setter
    def resolver(self, value: "AbstractCommandResolver") -> None:
        self._resolver = value

    @property
    def runner(self) -> "AbstractCommandRunner":
        return self._runner

    @runner.setter
    def runner(self, value: "AbstractCommandRunner") -> None:
        self._runner = value

    @property
    def kernel(self) -> Union["AbstractKernel", "CommandRunnerKernel"]:
        # Enforce typing
        return cast("CommandRunnerKernel", super().kernel)

    def execute(self) -> Any:
        if self.runner is None:
            return None

        command = self.runner.build_command(request=self)

        return command.execute(self.arguments) if command is not None else None

    def get_resolver(self) -> "AbstractCommandResolver":
        resolver = self.kernel.get_resolver(self.type)
        if resolver is None:
            raise CommandResolverNotFound(self.type)
        return resolver

    def guess_runner(self) -> Optional["AbstractCommandRunner"]:
        for runner in self.kernel.get_runners().values():
            if runner.will_run(self):
                return runner
        return None

    def guess_type(self) -> Optional[str]:
        for resolver in self.kernel.get_resolvers().values():
            match = resolver.supports(request=self)
            if match is not None:
                self.match = match
                return resolver.get_type()
        return None
