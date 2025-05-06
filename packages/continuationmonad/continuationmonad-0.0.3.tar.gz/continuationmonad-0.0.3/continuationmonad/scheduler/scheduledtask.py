

from dataclasses import dataclass, field
import datetime
from typing import Callable

from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.utils.framesummary import FrameSummary


@dataclass
class ScheduledTask:
    task: Callable[[], ContinuationCertificate] = field(compare=False)
    weight: int = field(compare=False)
    cancellation: Cancellation | None = field(compare=False)
    stack: tuple[FrameSummary, ...] = field(compare=False)


@dataclass(order=True)
class DelayedScheduledTask(ScheduledTask):
    duetime: datetime.datetime

@dataclass(order=True)
class VirtualScheduledTask(ScheduledTask):
    duetime: float
