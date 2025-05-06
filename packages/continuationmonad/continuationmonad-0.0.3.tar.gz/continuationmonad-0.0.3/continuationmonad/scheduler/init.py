from __future__ import annotations

from collections import deque
import datetime
from threading import Condition, Lock, Thread
from typing import Deque

from dataclassabc import dataclassabc

from continuationmonad.scheduler.scheduledtask import DelayedScheduledTask, ScheduledTask, VirtualScheduledTask
from continuationmonad.scheduler.schedulers.currentthreadscheduler import (
    CurrentThreadScheduler,
)
from continuationmonad.scheduler.schedulers.eventloopscheduler import (
    EventLoopScheduler,
    MainScheduler,
)
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.scheduler.schedulers.virtualtimescheduler import MainVirtualTimeScheduler, VirtualTimeScheduler


# def init_main_trampoline():
#     return MainTrampoline()


@dataclassabc
class CurrentThreadSchedulerImpl(CurrentThreadScheduler):
    immediate_tasks: Deque[ScheduledTask]
    delayed_tasks: list[DelayedScheduledTask]
    lock: Lock
    delayed_task_lock: Lock
    condition: Condition
    idle: bool


def init_current_thread_scheduler():
    lock = Lock()
    delayed_task_lock = Lock()

    return CurrentThreadSchedulerImpl(
        immediate_tasks=deque(),
        delayed_tasks=[],
        lock=lock,
        delayed_task_lock=delayed_task_lock,
        condition=Condition(lock),
        idle=True,
    )


@dataclassabc(frozen=False)
class EventLoopSchedulerImpl(EventLoopScheduler):
    immediate_tasks: Deque[ScheduledTask]
    delayed_tasks: list[DelayedScheduledTask]
    lock: Lock
    delayed_task_lock: Lock
    condition: Condition
    is_stopped: bool


@dataclassabc(frozen=False)
class MainSchedulerImpl(EventLoopSchedulerImpl, MainScheduler):
    pass


def init_event_loop_scheduler():
    lock = Lock()
    delayed_task_lock = Lock()

    scheduler = EventLoopSchedulerImpl(
        immediate_tasks=deque(),
        delayed_tasks=[],
        lock=lock,
        delayed_task_lock=delayed_task_lock,
        condition=Condition(lock),
        is_stopped=False,
    )

    Thread(target=scheduler.start_loop, daemon=True).start()

    return scheduler
    

def init_main_scheduler():
    lock = Lock()
    delayed_task_lock = Lock()

    return MainSchedulerImpl(
        immediate_tasks=deque(),
        delayed_tasks=[],
        lock=lock,
        delayed_task_lock=delayed_task_lock,
        condition=Condition(lock),
        is_stopped=False,
    )


@dataclassabc(frozen=True)
class TrampolineImpl(Trampoline):
    queue: Deque[ScheduledTask]


def init_trampoline():
    return TrampolineImpl(
        queue=deque(),
    )


@dataclassabc(frozen=False)
class VirtualTimeSchedulerImpl(VirtualTimeScheduler):
    immediate_tasks: Deque[ScheduledTask]
    delayed_tasks: list[VirtualScheduledTask]
    lock: Lock
    delayed_task_lock: Lock
    time: float
    idle: bool
    start_datetime: datetime.datetime


@dataclassabc(frozen=False)
class MainVirtualTimeSchedulerImpl(VirtualTimeSchedulerImpl, MainVirtualTimeScheduler):
    is_stopped: bool


def init_virtual_time_scheduler(
    is_main: bool | None = None,
):
    if is_main is None:
        is_main = False

    if is_main:
        return MainVirtualTimeSchedulerImpl(
            immediate_tasks=deque(),
            delayed_tasks=[],
            lock=Lock(),
            delayed_task_lock= Lock(),
            idle=True,
            time=0,
            is_stopped=True,
            start_datetime=datetime.datetime.now(),
        )
    
    else:
        return VirtualTimeSchedulerImpl(
            immediate_tasks=deque(),
            delayed_tasks=[],
            lock=Lock(),
            delayed_task_lock= Lock(),
            idle=True,
            time=0,
            start_datetime=datetime.datetime.now(),
        )
