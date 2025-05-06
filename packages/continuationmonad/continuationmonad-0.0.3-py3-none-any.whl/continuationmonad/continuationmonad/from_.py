import datetime
from typing import Callable, Iterable

from continuationmonad.continuationmonad.continuationmonad import ContinuationMonad
from continuationmonad.continuationmonad.init import init_continuation_monad

from continuationmonad.continuationmonadtree.deferredhandler import DeferredHandler
from continuationmonad.continuationmonadtree.init import (
    init_error,
    init_schedule_absolute,
    init_schedule_relative,
    init_zip,
    init_from_value,
    init_get_trampoline,
    init_defer,
    init_schedule_on,
)
from continuationmonad.scheduler.continuationcertificate import (
    ContinuationCertificate,
)
from continuationmonad.scheduler.instantscheduler import InstantScheduler
from continuationmonad.scheduler.scheduler import Scheduler
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.utils.framesummary import get_frame_summary


class defer[U]:
    def __new__(
        _,
        func: Callable[[Trampoline, DeferredHandler[U]], ContinuationCertificate],
    ):
        """
        Create a continuation monad that defers the subscription until a source is connected.

        The function `func` is called when the deferred continuation monad is subscribed to.
        Since no source is initially specified, the subscription can not propagate further upstream.
        The function must return a continuation certificate to maintain the monadic chain's validity.

        Args:
            func: A function that receives a subscriber object that can be stored for later connection, and
                must return a continuation certficate

        Returns:
            (ContinuationMonad[U]): A monad that will begin emitting an item once connected to a source


        ``` python
        from continuationmonad.typing import DeferredHandler

        deferred_handlers: list[DeferredHandler] = [None]  # type: ignore
        certificates: list[ContinuationCertificate] = [None] # type: ignore

        def func(_, handler: DeferredHandler):
            deferred_handlers[0] = handler
            return deferred_handlers[0]

        @do()
        def defer_and_connect():
            trampoline = yield continuationmonad.get_trampoline()

            certificates[0] = continuationmonad.fork(
                source = (
                    continuationmonad.from_(None)
                    .flat_map(lambda _: continuationmonad.from_('defer').connect(deferred_handlers))
                    .map(lambda cs: cs[0])
                ),
                scheduler=trampoline,
                weight=1,
            )

            return continuationmonad.defer(func)
        ```
        """

        return init_continuation_monad(init_defer(func=func, stack=get_frame_summary()))


def zip[U](
    sources: Iterable[ContinuationMonad[U]],
):
    """
    Create a new continuation monad from two (or more) continuation monads by combining their items
    in a tuple.

    Args:
        sources: One or more continuation monads.

    Returns:
        (ContinuationMonad[U]): A monad that emits the items of the specified sources within a tuple.


    ``` python
    c = continuationmonad.zip((
        continuationmonad.from_(1),
        continuationmonad.from_(2),
    ))
    ```
    """

    return init_continuation_monad(init_zip(children=tuple(sources)))


def error(exception: Exception):
    return init_continuation_monad(init_error(exception=exception))


def from_[U](value: U):
    return init_continuation_monad(init_from_value(value=value))


def get_trampoline():
    return init_continuation_monad(init_get_trampoline())


def schedule_on(scheduler: InstantScheduler):
    return init_continuation_monad(init_schedule_on(scheduler=scheduler))


def schedule_relative(scheduler: Scheduler, duetime: float):
    return init_continuation_monad(
        init_schedule_relative(scheduler=scheduler, duetime=duetime)
    )


def schedule_absolute(scheduler: Scheduler, duetime: datetime.datetime):
    return init_continuation_monad(
        init_schedule_absolute(scheduler=scheduler, duetime=duetime)
    )


def schedule_trampoline():
    return get_trampoline()


def tail_rec(func: Callable[[], ContinuationMonad]):
    return schedule_trampoline().flat_map(lambda _: func())
