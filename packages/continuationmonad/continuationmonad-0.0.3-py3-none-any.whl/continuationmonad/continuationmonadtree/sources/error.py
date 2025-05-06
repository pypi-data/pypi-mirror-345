from abc import abstractmethod

from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave


class Error[U](ContinuationMonadLeave[U]):
    def __str__(self) -> str:
        return f"error({self.exception})"

    @property
    @abstractmethod
    def exception(self) -> Exception: ...

    def _subscribe(
        self,
        args: SubscribeArgs,
    ):
        return args.observer.on_error(args.trampoline, self.exception)
