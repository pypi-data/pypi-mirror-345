from dataclasses import dataclass
from typing import Callable
from continuationmonad.continuationmonadtree.observer import (
    Observer,
    init_anonymous_observer,
)
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.init import init_trampoline
from continuationmonad.scheduler.instantscheduler import InstantScheduler
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.continuationmonadtree.subscribeargs import init_subscribe_args
from continuationmonad.continuationmonadtree.to import run as _run
from continuationmonad.continuationmonad.continuationmonad import ContinuationMonad


@dataclass
class ForkObserver(Observer[ContinuationCertificate]):
    on_error_func: Callable[[Exception], ContinuationMonad[ContinuationCertificate]]
    cancellation: Cancellation | None
    weight: int

    def on_success(self, _, item: ContinuationCertificate):
        return item

    def on_error(
        self, trampoline: Trampoline, exception: Exception
    ) -> ContinuationCertificate:
        args = init_subscribe_args(
            observer=init_anonymous_observer(
                on_success=lambda _, c: c,
            ),
            trampoline=trampoline,
            cancellation=self.cancellation,
            weight=self.weight,
        )

        return self.on_error_func(exception).subscribe(
            args=args,
        )


def fork(
    source: ContinuationMonad[ContinuationCertificate],
    on_error: Callable[[Exception], ContinuationMonad[ContinuationCertificate]],
    scheduler: InstantScheduler,
    weight: int,
    cancellation: Cancellation | None = None,
) -> ContinuationCertificate:
    match scheduler:
        case Trampoline() as trampoline:
            args = init_subscribe_args(
                observer=ForkObserver(
                    on_error_func=on_error,
                    cancellation=cancellation,
                    weight=weight,
                ),
                trampoline=trampoline,
                cancellation=cancellation,
                weight=weight,
            )

            def trampoline_task():
                return source.subscribe(args=args)

            return trampoline.schedule(
                trampoline_task,
                weight=weight,
                cancellation=cancellation,
            )

        case _:

            def schedule_task():
                trampoline = init_trampoline()

                args = init_subscribe_args(
                    observer=ForkObserver(
                        on_error_func=on_error,
                        cancellation=cancellation,
                        weight=weight,
                    ),
                    trampoline=trampoline,
                    cancellation=cancellation,
                    weight=weight,
                )

                def trampoline_task():
                    return source.subscribe(args=args)

                return trampoline.run(
                    trampoline_task, weight=weight, cancellation=cancellation
                )

            return scheduler.schedule(
                task=schedule_task,
                weight=weight,
                cancellation=cancellation,
            )


def run[V](source: ContinuationMonad[V]) -> V:
    return _run(source.child)
