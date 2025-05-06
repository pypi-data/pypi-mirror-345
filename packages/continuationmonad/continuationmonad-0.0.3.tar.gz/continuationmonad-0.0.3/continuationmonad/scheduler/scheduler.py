from abc import abstractmethod

import datetime
from typing import Callable

from continuationmonad.scheduler.continuationcertificate import (
    ContinuationCertificate,
)
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.instantscheduler import InstantScheduler


class Scheduler(InstantScheduler):
    @abstractmethod
    def now(self) -> datetime.datetime: ...

    @abstractmethod
    def schedule_relative(
        self,
        duetime: float,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ) -> ContinuationCertificate: ...

    @abstractmethod
    def schedule_absolute(
        self,
        duetime: datetime.datetime,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ) -> ContinuationCertificate: ...
