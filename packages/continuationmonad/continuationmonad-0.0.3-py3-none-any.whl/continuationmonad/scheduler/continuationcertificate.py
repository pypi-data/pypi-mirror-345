from __future__ import annotations
from threading import Lock

from continuationmonad.exceptions import ContinuationMonadOperatorException
from continuationmonad.utils.framesummary import FrameSummaryMixin, FrameSummary, get_frame_summary


class ContinuationCertificate(FrameSummaryMixin):
    __permission__ = False

    def __init__(self, lock: Lock, weight: int, stack: tuple[FrameSummary, ...]):
        assert self.__permission__, (
            "A certificate should uniquely be created by a scheduler implementation."
        )

        # a certificate can be verified exactly once
        self.__verified__ = False

        self._lock = lock
        self._weight = weight
        self._stack = stack

    @property
    def lock(self):
        return self._lock

    @property
    def weight(self):
        return self._weight

    def __repr__(self):
        return f"{self.__class__.__name__}(weight={self._weight}, verified={self.__verified__})"

    def verify(self, weight: int):
        """
        A continuation can be verified exactly once.
        """

        if weight != self._weight:
            traceback_msg = self.to_operator_traceback(stack=self._stack)
            raise ContinuationMonadOperatorException(
                f"The provided weight {weight} does not match the certificate weight {self._weight}."
                f"\n{traceback_msg}"
            )

        with self._lock:
            # assert not self.__verified__, 'A continuation can only be verified once.'
            p_verified = self.__verified__
            self.__verified__ = True

        if p_verified:
            traceback_msg = self.to_operator_traceback(stack=self._stack)
            raise ContinuationMonadOperatorException(
                "The certificate has already been verified."
                f"\n{traceback_msg}"
            )

    def split(self, partition: tuple[int, ...], stack: tuple[FrameSummary, ...] | None = None):
        assert sum(partition) == self._weight

        if stack is None:
            stack = get_frame_summary()

        self.verify(self.weight)

        def gen_certificates():
            for weight in partition:
                yield self.__class__(lock=self._lock, weight=weight, stack=stack)

        return tuple(gen_certificates())

    def take(self, weight: int):
        if self._weight < weight:
            traceback_msg = self.to_operator_traceback(stack=self._stack)
            raise ContinuationMonadOperatorException(
                f"{weight} is larger than {self._weight}"
                f"\n{traceback_msg}"
            )

        return self.split(
            partition=(weight, self._weight - weight), 
            stack=get_frame_summary(),
        )

    @staticmethod
    def merge(
        certificates: tuple[ContinuationCertificate, ...],
    ):
        first, *_ = certificates

        def gen_weight():
            for certificate in certificates:
                weight = certificate.weight
                certificate.verify(weight)
                yield weight

        total_weight = sum(gen_weight())

        return first.__class__(
            lock=first._lock, 
            weight=total_weight, 
            stack=get_frame_summary(),
        )
