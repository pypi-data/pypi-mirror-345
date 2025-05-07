from typing import Callable, Any, TYPE_CHECKING

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel


class Command(AbstractKernelChild, BaseModel):
    function: Callable[..., Any] = None

    def __init__(self, kernel: "AbstractKernel", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    def execute(self, arguments):
        return self.function(
            kernel=self.kernel,
            arguments=arguments
        )
