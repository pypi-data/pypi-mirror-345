from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild

if TYPE_CHECKING:
    from src.utils.kernel import Kernel

class AbstractResponse(AbstractKernelChild, BaseModel):
    def __init__(self, /, kernel: "Kernel", **kwargs: Any) -> None:
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    @abstractmethod
    def print(self) -> str:
        # For now, simple placeholder.
        pass
