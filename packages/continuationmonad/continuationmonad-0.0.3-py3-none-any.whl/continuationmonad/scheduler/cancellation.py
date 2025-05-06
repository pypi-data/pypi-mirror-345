from abc import ABC, abstractmethod
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate


class Cancellation(ABC):
    """Used to cancel a task scheduled on a scheduler."""

    @abstractmethod
    def is_cancelled(self) -> ContinuationCertificate | None:
        ...
