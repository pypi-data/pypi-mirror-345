from __future__ import annotations

from dataclasses import dataclass, replace

from continuationmonad.continuationmonadtree.observer import Observer
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.schedulers.trampoline import Trampoline


@dataclass
class SubscribeArgs[U]:
    observer: Observer[U]

    # weight of the continuation certificate returned by the subscribe method
    weight: int

    # Allows to cancel the continuation. The cancellation is not executed immediately, 
    # but only when a new task associated with the continuation is scheduled.
    cancellation: Cancellation | None

    # ensure that no item is emitted before subscribe method returns
    trampoline: Trampoline

    raise_immediately: bool

    def copy[V](
        self, /,
        observer: Observer[V] | None = None,
        cancellation: Cancellation | None = None,
        trampoline: Trampoline | None = None,
        weight: int | None = None,
    ) -> SubscribeArgs[V]:
        def gen_args():
            if observer is not None:
                yield 'observer', observer
            if cancellation is not None:
                yield 'cancellation', cancellation
            if trampoline is not None:
                yield 'trampoline', trampoline
            if weight is not None:
                yield 'weight', weight

        args = dict(gen_args())
        return replace(self, **args)


def init_subscribe_args[U](
    observer: Observer[U],
    trampoline: Trampoline,
    weight: int,
    cancellation: Cancellation | None = None,
    raise_immediately: bool | None = None,
):
    if raise_immediately is None:
        raise_immediately = True

    return SubscribeArgs(
        observer=observer,
        weight=weight,
        cancellation=cancellation,
        trampoline=trampoline,
        raise_immediately=raise_immediately,
    )
