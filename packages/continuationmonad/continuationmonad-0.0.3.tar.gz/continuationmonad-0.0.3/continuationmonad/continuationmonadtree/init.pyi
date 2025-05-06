import datetime
from typing import Callable, Iterable

from continuationmonad.continuationmonadtree.sources.scheduleabsolute import ScheduleAbsolute
from continuationmonad.continuationmonadtree.sources.schedulerelative import ScheduleRelative
from continuationmonad.scheduler.scheduler import Scheduler
from continuationmonad.utils.framesummary import FrameSummary
from continuationmonad.scheduler.continuationcertificate import (
    ContinuationCertificate,
)
from continuationmonad.scheduler.instantscheduler import InstantScheduler
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.continuationmonadtree.deferredhandler import DeferredHandler
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadNode
from continuationmonad.continuationmonadtree.operations.zip import Zip
from continuationmonad.continuationmonadtree.sources.scheduleon import ScheduleOn
from continuationmonad.continuationmonadtree.operations.connect import (
    Connect,
)
from continuationmonad.continuationmonadtree.operations.defer import (
    Defer,
)
from continuationmonad.continuationmonadtree.operations.flatmap import FlatMap
from continuationmonad.continuationmonadtree.sources.gettrampoline import (
    GetTrampoline,
)
from continuationmonad.continuationmonadtree.operations.map import Map
from continuationmonad.continuationmonadtree.sources.fromvalue import FromValue

def init_connect[U](
    child: ContinuationMonadNode[U],
    handlers: Iterable[DeferredHandler[U]],
) -> Connect[U]: ...
def init_defer[U](
    func: Callable[[Trampoline, DeferredHandler[U]], ContinuationCertificate],
    stack: tuple[FrameSummary, ...],
) -> Defer[U]: ...
def init_flat_map[U, V](
    child: ContinuationMonadNode[U],
    func: Callable[[U], ContinuationMonadNode[V]],
    stack: tuple[FrameSummary, ...],
) -> FlatMap[U, V]: ...
def init_error(exception: Exception) -> FromValue[None]: ...
def init_from_value[U](value: U) -> FromValue[U]: ...
def init_get_trampoline() -> GetTrampoline: ...
def init_map[U, V](
    child: ContinuationMonadNode[U],
    func: Callable[[U], V],
    stack: tuple[FrameSummary, ...],
) -> Map[U, V]: ...
def init_schedule_on(
    scheduler: InstantScheduler,
) -> ScheduleOn: ...
def init_schedule_relative(
    duetime: float,
    scheduler: Scheduler,
) -> ScheduleRelative: ...
def init_schedule_absolute(
    duetime: datetime.datetime,
    scheduler: Scheduler,
) -> ScheduleAbsolute: ...

class init_zip[U]:
    def __new__(
        _,
        children: tuple[ContinuationMonadNode[U], ...],
    ) -> Zip[tuple[U, ...]]: ...
