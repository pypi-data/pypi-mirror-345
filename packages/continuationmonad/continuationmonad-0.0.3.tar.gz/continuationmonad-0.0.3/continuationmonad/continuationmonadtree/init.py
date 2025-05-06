import datetime
from typing import Callable, Iterable
from dataclassabc import dataclassabc

from continuationmonad.continuationmonadtree.sources.scheduleabsolute import ScheduleAbsolute
from continuationmonad.continuationmonadtree.sources.schedulerelative import (
    ScheduleRelative,
)
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
from continuationmonad.continuationmonadtree.sources.error import (
    Error,
)
from continuationmonad.continuationmonadtree.operations.map import Map
from continuationmonad.continuationmonadtree.sources.fromvalue import FromValue


@dataclassabc(frozen=True)
class ConnectImpl(Connect):
    child: ContinuationMonadNode
    handlers: Iterable[DeferredHandler]


def init_connect(child, handlers):
    return ConnectImpl(
        child=child,
        handlers=handlers,
    )


@dataclassabc(frozen=True)
class DeferImpl[_](Defer):  # hide Impl classes in init.pyi for type hinting
    func: Callable[[Trampoline, DeferredHandler], ContinuationCertificate]
    stack: tuple[FrameSummary, ...]


def init_defer(
    func: Callable[[Trampoline, DeferredHandler], ContinuationCertificate],
    stack: tuple[FrameSummary, ...],
):
    return DeferImpl(
        func=func,
        stack=stack,
    )


@dataclassabc(frozen=True)
class FlatMapImpl[_, __](FlatMap):
    child: ContinuationMonadNode
    func: Callable[[None], ContinuationMonadNode]
    stack: tuple[FrameSummary, ...]


def init_flat_map(
    child: ContinuationMonadNode,
    func: Callable[[None], ContinuationMonadNode],
    stack: tuple[FrameSummary, ...],
):
    return FlatMapImpl(
        child=child,
        func=func,
        stack=stack,
    )


@dataclassabc(frozen=True)
class GetTrampolineImpl(GetTrampoline):
    pass


def init_get_trampoline():
    return GetTrampolineImpl()


@dataclassabc(frozen=True)
class ZipImpl[_](Zip):
    children: tuple[ContinuationMonadNode, ...]


def init_zip(children: Iterable[ContinuationMonadNode]):
    children = tuple(children)

    match len(children):
        case 0:
            raise AssertionError(
                "No continuation monads provided. Cannot create a continuation monad."
            )

        case 1:
            return children

        case _:
            return ZipImpl(children=children)


@dataclassabc(frozen=True)
class MapImpl[_, __](Map):
    child: ContinuationMonadNode
    func: Callable
    stack: tuple[FrameSummary, ...]


def init_map(child, func, stack):
    return MapImpl(
        child=child,
        func=func,
        stack=stack,
    )


@dataclassabc(frozen=True)
class ErrorImpl[_](Error):
    exception: Exception


def init_error(exception):
    return ErrorImpl(exception)


@dataclassabc(frozen=True)
class FromValueImpl[_](FromValue):
    value: None


def init_from_value(value):
    return FromValueImpl(value)


@dataclassabc(frozen=True)
class ScheduleOnImpl(ScheduleOn):
    scheduler: InstantScheduler


def init_schedule_on(
    scheduler: InstantScheduler,
):
    return ScheduleOnImpl(
        scheduler=scheduler,
    )


@dataclassabc(frozen=True)
class ScheduleRelativeImpl(ScheduleRelative):
    duetime: float
    scheduler: Scheduler


def init_schedule_relative(
    scheduler: Scheduler,
    duetime: float,
):
    return ScheduleRelativeImpl(
        scheduler=scheduler,
        duetime=duetime,
    )

@dataclassabc(frozen=True)
class ScheduleAbsoluteImpl(ScheduleAbsolute):
    duetime: datetime.datetime
    scheduler: Scheduler


def init_schedule_absolute(
    scheduler: Scheduler,
    duetime: datetime.datetime,
):
    return ScheduleAbsoluteImpl(
        scheduler=scheduler,
        duetime=duetime,
    )

