from abc import ABC, abstractmethod
from typing import Callable
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.schedulers.trampoline import Trampoline


class Observer[U](ABC):
    @abstractmethod
    def on_success(
        self,
        trampoline: Trampoline,
        item: U,
    ) -> ContinuationCertificate: ...
    @abstractmethod
    def on_error(
        self,
        trampoline: Trampoline,
        exception: Exception,
    ) -> ContinuationCertificate: ...


def init_anonymous_observer[U](
    on_success: Callable[[Trampoline, U], ContinuationCertificate],
    on_error: Callable[[Trampoline, Exception], ContinuationCertificate] | None = None,
):
    if on_error is None:
        def on_error_func(trampoline: Trampoline, exception: Exception) -> ContinuationCertificate:
            raise exception
    else:
        on_error_func = on_error

    class AnonymousObserver(Observer):
        def on_success(self, trampoline: Trampoline, item: U) -> ContinuationCertificate:
            return on_success(trampoline, item)

        def on_error(self, trampoline: Trampoline, exception: Exception) -> ContinuationCertificate:
            return on_error_func(trampoline, exception)
        
    return AnonymousObserver()
