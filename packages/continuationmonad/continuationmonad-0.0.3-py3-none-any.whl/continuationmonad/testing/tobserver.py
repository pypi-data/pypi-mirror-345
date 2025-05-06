from dataclasses import dataclass

from continuationmonad.continuationmonadtree.observer import Observer
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.mainschedulermixin import MainScheduler
from continuationmonad.scheduler.schedulers.trampoline import Trampoline


@dataclass(frozen=False)
class TObserver[U](Observer[U]):
    received_item: U | None
    received_exception: Exception | None
    main_scheduler: MainScheduler

    def on_success(self, trampoline: Trampoline, item: U) -> ContinuationCertificate:
        self.received_item = item
        return self.main_scheduler.stop()

    def on_error(self, trampoline: Trampoline, exception: Exception) -> ContinuationCertificate:
        self.received_exception = exception
        return self.main_scheduler.stop()


def init_test_observer(main_scheduler: MainScheduler):
    return TObserver(
        received_item=None,
        received_exception=None,
        main_scheduler=main_scheduler,
    )
