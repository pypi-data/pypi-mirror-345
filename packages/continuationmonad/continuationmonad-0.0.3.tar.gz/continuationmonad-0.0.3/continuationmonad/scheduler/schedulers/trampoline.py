from __future__ import annotations

from abc import abstractmethod
from typing import Callable, Deque, override

from continuationmonad.utils.framesummary import FrameSummary, get_frame_summary
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.instantscheduler import InstantScheduler


class Trampoline(InstantScheduler):
    @property
    @abstractmethod
    def queue(self) -> Deque[
        tuple[
            Callable[[], ContinuationCertificate],
            int,
            Cancellation | None,
            tuple[FrameSummary, ...]
        ]
    ]: ...
    
    def run(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        first_certificate = self.schedule(task=task, weight=weight, cancellation=cancellation)

        while self.queue:
            queued_task, queued_weight, queued_cancel_task, stack = self.queue.popleft()

            self._execute_task(
                task=queued_task,
                weight=queued_weight,
                stack=stack,
                cancellation=queued_cancel_task,
            )

        return first_certificate

    @override
    def schedule(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ):
        stack = get_frame_summary()

        self.queue.append((task, weight, cancellation, stack))

        return self._create_certificate(
            weight=weight,
            stack=get_frame_summary(),
        )

