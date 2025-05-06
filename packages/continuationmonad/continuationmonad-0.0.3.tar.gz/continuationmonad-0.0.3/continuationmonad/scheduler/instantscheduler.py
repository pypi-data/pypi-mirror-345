from abc import ABC, abstractmethod
from threading import Lock
from typing import Callable

from continuationmonad.utils.framesummary import FrameSummary, to_operator_traceback
from continuationmonad.exceptions import ContinuationMonadOperatorException
from continuationmonad.scheduler.cancellation import Cancellation
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate


class InstantScheduler(ABC):
    # @property
    # @abstractmethod
    # def lock(self) -> RLock: ...

    @abstractmethod
    def schedule(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        cancellation: Cancellation | None = None,
    ) -> ContinuationCertificate: ...

    def _execute_task(
        self,
        task: Callable[[], ContinuationCertificate],
        weight: int,
        stack: tuple[FrameSummary, ...],
        cancellation: Cancellation | None = None,
    ):
        # if task it cancelled, retrieve certificate from is_cancelled
        if cancellation and (
            certificate := cancellation.is_cancelled()
        ):
            source = cancellation

        else:
            # call scheduled task
            certificate = task()
            source = task

        try:
            certificate.verify(weight=weight)

        except Exception:
            traceback_msg = to_operator_traceback(stack=stack)
            raise ContinuationMonadOperatorException(
                f"The certificate returned by {source} could not be verified."
                f"\n{traceback_msg}"
            )

    def _create_certificate(
        self,
        weight: int,
        stack: tuple[FrameSummary, ...],
    ):
        _ContinuationCertificate = type(
            ContinuationCertificate.__name__,
            ContinuationCertificate.__mro__,
            ContinuationCertificate.__dict__ | {"__permission__": True},
        )
        return _ContinuationCertificate(lock=Lock(), weight=weight, stack=stack)
