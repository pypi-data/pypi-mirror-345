from abc import abstractmethod
import traceback
from typing import Callable

from continuationmonad.continuationmonadtree.observer import Observer
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.utils.framesummary import FrameSummaryMixin
from continuationmonad.exceptions import ContinuationMonadOperatorException
from continuationmonad.scheduler.continuationcertificate import (
    ContinuationCertificate,
)
from continuationmonad.continuationmonadtree.deferredhandler import DeferredHandler
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadNode


class Defer[U](FrameSummaryMixin, ContinuationMonadNode[U]):
    def __str__(self) -> str:
        return "defer()"

    @property
    @abstractmethod
    def func(
        self,
    ) -> Callable[
        [Trampoline, DeferredHandler], ContinuationMonadNode[ContinuationCertificate]
    ]: ...

    def subscribe(
        self,
        args: SubscribeArgs,
    ):
        deferred_handler = DeferredHandler(
            observer=args.observer,
            weight=args.weight,
            cancellation=args.cancellation,
        )

        try:
            continuation = self.func(args.trampoline, deferred_handler)

        except ContinuationMonadOperatorException as exception:
            if args.raise_immediately:
                raise

            exception = ContinuationMonadOperatorException(
                "\n".join(
                    (
                        exception.args[0],
                        self.to_execution_exception_message(traceback.format_exc()),
                    )
                )
            )
            return args.observer.on_error(args.trampoline, exception)

        except Exception:
            if args.raise_immediately:
                raise ContinuationMonadOperatorException(
                    self.to_operator_exception_message(stack=self.stack)
                )

            exception = ContinuationMonadOperatorException(
                "\n".join(
                    (
                        self.to_execution_exception_message(traceback.format_exc()),
                        self.to_operator_exception_message(stack=self.stack),
                    )
                )
            )
            return args.observer.on_error(args.trampoline, exception)

        if isinstance(continuation, ContinuationCertificate):
            assert continuation.weight == args.weight, (
                f"{continuation.weight} does not match {args.weight}"
            )

            return continuation

        else:
            class DeferObserver(Observer):
                def on_success(self, _, item: ContinuationCertificate):
                    return item

                def on_error(self, exception: Exception) -> ContinuationCertificate:
                    return args.observer.on_error(args.trampoline, exception)


            return continuation.subscribe(args=args.copy(
                    observer=DeferObserver(),
            ))
