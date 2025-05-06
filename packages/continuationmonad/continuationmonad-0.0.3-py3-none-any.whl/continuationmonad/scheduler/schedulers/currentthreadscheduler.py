from abc import abstractmethod
import heapq
from threading import Condition, Lock
from typing import Callable, Deque, override
import datetime

from continuationmonad.scheduler.scheduledtask import DelayedScheduledTask, ScheduledTask
from continuationmonad.utils.framesummary import get_frame_summary
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.scheduler import Scheduler


class CurrentThreadScheduler(Scheduler):
    @property
    @abstractmethod
    def immediate_tasks(
        self,
    ) -> Deque[ScheduledTask]: ...

    @property
    @abstractmethod
    def delayed_tasks(
        self,
    ) -> list[DelayedScheduledTask]: ...

    @property
    @abstractmethod
    def lock(self) -> Lock: ...

    @property
    @abstractmethod
    def delayed_task_lock(self) -> Lock: ...

    @property
    @abstractmethod
    def condition(self) -> Condition: ...

    @property
    @abstractmethod
    def idle(self) -> bool: ...

    @idle.setter
    @abstractmethod
    def idle(selfc, val: bool): ...

    def _start_loop(self):
        while True:
            if self.immediate_tasks:
                entry = self.immediate_tasks.popleft()

                self._execute_task(
                    task=entry.task,
                    weight=entry.weight,
                    stack=entry.stack,
                    cancellation=entry.cancellation,
                )

            elif self.delayed_tasks:

                schedule_due = False
                entry = None

                with self.delayed_task_lock:
                    entry = self.delayed_tasks[0]
                    if datetime.timedelta(0) <= datetime.datetime.now() - entry.duetime:
                        entry = heapq.heappop(self.delayed_tasks)
                        schedule_due = True


                if schedule_due:
                    self.immediate_tasks.append(entry)

                else:
                    timedelta = (entry.duetime - datetime.datetime.now()).total_seconds()
                    if 0 < timedelta:
                        with self.condition:
                            self.condition.wait(timedelta)

            else:
                with self.lock:
                    if self.immediate_tasks or self.delayed_tasks:
                        pass

                    else:
                        self.idle = True
                        break

    @override
    def now(self):
        return datetime.datetime.now()

    @override
    def schedule(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        # stack = get_frame_summary()

        # self.immediate_tasks.append((task, weight, cancellation, stack))

        entry = ScheduledTask(
            task=task,
            weight=weight,
            cancellation=cancellation,
            stack=get_frame_summary()
        )

        self.immediate_tasks.append(entry)

        with self.lock:
            idle = self.idle
            self.idle = False

            self.condition.notify()

        if idle:
            self._start_loop()

        return self._create_certificate(
            weight=weight,
            stack=get_frame_summary(),
        )

    @override
    def schedule_relative(
        self,
        duetime: float,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        duetime_datetime = datetime.datetime.now() + datetime.timedelta(seconds=duetime)

        return self.schedule_absolute(
            duetime=duetime_datetime,
            task=task,
            weight=weight,
            cancellation=cancellation,
        )

    @override
    def schedule_absolute(
        self,
        duetime: datetime.datetime,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        entry = DelayedScheduledTask(
            duetime=duetime,
            task=task,
            weight=weight,
            cancellation=cancellation,
            stack=get_frame_summary()
        )

        with self.delayed_task_lock:
            heapq.heappush(self.delayed_tasks, entry)

        with self.lock:
            idle = self.idle
            self.idle = False

            self.condition.notify()

        if idle:
            self._start_loop()

        return self._create_certificate(
            weight=weight,
            stack=get_frame_summary(),
        )
