from abc import ABC, abstractmethod
from typing import Callable

from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.scheduler import Scheduler


class MainScheduler(Scheduler):
    @abstractmethod
    def stop(self) -> ContinuationCertificate: ...

    @abstractmethod
    def run(
        self,
        task: Callable[[], ContinuationCertificate],
        cancellation: Cancellation | None = None,
    ) -> None: ...
