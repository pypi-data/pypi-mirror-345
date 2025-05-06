from abc import abstractmethod

from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave


class FromValue[U](ContinuationMonadLeave[U]):
    def __str__(self) -> str:
        return f"from_value({self.value})"

    @property
    @abstractmethod
    def value(self) -> U: ...

    def _subscribe(
        self,
        args: SubscribeArgs,
    ):
        return args.observer.on_success(args.trampoline, self.value)

        # def trampoline_task():
        #     return args.observer.on_success(args.trampoline, self.value)

        # return args.trampoline.schedule(
        #     task=trampoline_task,
        #     weight=args.weight,
        #     cancellation=args.cancellation,
        # )
