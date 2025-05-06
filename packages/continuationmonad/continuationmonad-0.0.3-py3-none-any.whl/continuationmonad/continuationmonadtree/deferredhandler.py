from dataclasses import dataclass

from continuationmonad.continuationmonadtree.observer import Observer
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.schedulers.trampoline import Trampoline


@dataclass
class DeferredHandler[U]:
    observer: Observer[U]
    weight: int
    cancellation: Cancellation | None

    def resume(self, trampoline: Trampoline, value: U):
        return self.observer.on_success(trampoline, value)
