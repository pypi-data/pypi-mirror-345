from abc import abstractmethod
import datetime
import heapq
from threading import Lock
from typing import Callable, Deque, override

from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.mainschedulermixin import MainScheduler
from continuationmonad.scheduler.scheduledtask import VirtualScheduledTask, ScheduledTask
from continuationmonad.scheduler.scheduler import Scheduler
from continuationmonad.utils.framesummary import get_frame_summary


class VirtualTimeScheduler(Scheduler):
    @property
    @abstractmethod
    def immediate_tasks(
        self,
    ) -> Deque[ScheduledTask]: ...

    @property
    @abstractmethod
    def delayed_tasks(
        self,
    ) -> list[VirtualScheduledTask]: ...

    @property
    @abstractmethod
    def lock(self) -> Lock: ...

    @property
    @abstractmethod
    def delayed_task_lock(self) -> Lock: ...

    @property
    @abstractmethod
    def start_datetime(self) -> datetime.datetime: ...

    @property
    @abstractmethod
    def time(self) -> float: ...

    @time.setter
    @abstractmethod
    def time(self, val: float): ...

    @property
    @abstractmethod
    def idle(self) -> bool: ...

    @idle.setter
    @abstractmethod
    def idle(selfc, val: bool): ...

    @override
    def now(self):
        return self.start_datetime + datetime.timedelta(seconds=self.time)

    @override
    def schedule(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        entry = ScheduledTask(
            task=task,
            weight=weight,
            cancellation=cancellation,
            stack=get_frame_summary()
        )

        self.immediate_tasks.append(entry)

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
        entry = VirtualScheduledTask(
            duetime=self.time + duetime,
            task=task,
            weight=weight,
            cancellation=cancellation,
            stack=get_frame_summary()
        )

        with self.delayed_task_lock:
            heapq.heappush(self.delayed_tasks, entry)

        return self._create_certificate(
            weight=weight,
            stack=get_frame_summary(),
        )

    @override
    def schedule_absolute(
        self,
        duetime: datetime.datetime,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        duetime_time = (duetime - self.start_datetime).total_seconds()

        return self.schedule_relative(
            duetime=duetime_time,
            task=task,
            weight=weight,
            cancellation=cancellation,
        )

    def advance_to(self, time: float):
        with self.lock:
            idle = self.idle
            self.idle = False

        assert idle

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
                # print('delayed tasks!')

                schedule_due = False
                entry = None

                with self.delayed_task_lock:
                    entry = self.delayed_tasks[0]
                    if entry.duetime <= self.time:
                        entry = heapq.heappop(self.delayed_tasks)
                        schedule_due = True


                if schedule_due:
                    self.immediate_tasks.append(entry)

                elif entry.duetime <= time:
                    self.time = entry.duetime
                    
                else:
                    self.idle = True
                    break

            else:
                with self.lock:
                    if self.immediate_tasks or self.delayed_tasks:
                        pass

                    else:
                        self.idle = True
                        break


class MainVirtualTimeScheduler(MainScheduler, VirtualTimeScheduler):
    @property
    @abstractmethod
    def is_stopped(self) -> bool: ...

    @is_stopped.setter
    @abstractmethod
    def is_stopped(selfc, val: bool): ...


    def stop(self):
        """
        The stop function is capable of creating the finishing Continuation
        """

        with self.lock:
            if self.is_stopped:
                raise Exception("Scheduler can only be stopped once.")
            self.is_stopped = True

        return self._create_certificate(weight=1, stack=get_frame_summary())

    def run(
        self,
        task: Callable[[], ContinuationCertificate],
        cancellation: Cancellation | None = None,
    ) -> None:
        
        with self.lock:
            if not self.is_stopped:
                raise Exception("Scheduler can only be run once.")
            self.is_stopped = False
        
        self.schedule(task=task, weight=1, cancellation=cancellation)
