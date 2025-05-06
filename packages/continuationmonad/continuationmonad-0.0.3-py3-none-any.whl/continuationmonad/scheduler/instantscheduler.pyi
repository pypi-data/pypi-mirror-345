from typing import Callable, overload

from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import (
    ContinuationCertificate,
)
from continuationmonad.utils.framesummary import FrameSummary

class InstantScheduler:
    @overload
    def schedule(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
    ) -> ContinuationCertificate: ...
    @overload
    def schedule(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None,
    ) -> ContinuationCertificate: ...
    def _create_certificate(
        self, 
        weight: int, 
        stack: tuple[FrameSummary, ...]
    ) -> ContinuationCertificate: ...
    def _execute_task(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        stack: tuple[FrameSummary, ...],
        cancellation: Cancellation | None,
    ) -> None: ...
