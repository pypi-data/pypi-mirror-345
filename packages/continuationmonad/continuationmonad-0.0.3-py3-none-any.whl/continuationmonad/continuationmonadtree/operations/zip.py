from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Lock, RLock

from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.continuationmonadtree.observer import Observer
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import (
    MultiChildrenContinuationMonadNode,
)


# States
########


class ZipState: ...


@dataclass(frozen=True, slots=True)
class AwaitUpstreamStateMixin[U](ZipState):
    certificates: tuple[ContinuationCertificate, ...]
    values: dict[int, U]


@dataclass(frozen=True, slots=True)
class InitState(AwaitUpstreamStateMixin):
    pass


@dataclass(frozen=True, slots=True)
class AwaitFurtherState(AwaitUpstreamStateMixin):
    certificate: ContinuationCertificate


@dataclass(frozen=True, slots=True)
class OnSuccessState[U](ZipState):
    values: dict[int, U]


@dataclass(frozen=True, slots=True)
class TerminatedStateMixin(ZipState):
    """Flowable either completed, errored, or cancelled"""
    certificates: dict[int, ContinuationCertificate]


@dataclass(frozen=True, slots=True)
class OnErrorState(TerminatedStateMixin):
    pass


@dataclass(frozen=True, slots=True)
class HasTerminatedState(TerminatedStateMixin):
    """Has previously been terminated"""

    certificate: ContinuationCertificate


# Transitions
#############


class ZipTransition(ABC):
    @abstractmethod
    def get_state(self) -> ZipState: ...


@dataclass
class InitTransition(ZipTransition):
    counter: int
    certificates: tuple[ContinuationCertificate, ...]

    def get_state(self):
        return InitState(
            certificates=self.certificates,
            values={},
        )


@dataclass
class OnNextTransition[U](ZipTransition):
    id: int
    child: ZipTransition
    item: U

    def get_state(self):
        match state := self.child.get_state():
            case AwaitUpstreamStateMixin(
                certificates=certificates,
                values=values,
            ):
                values = values | {self.id: self.item}
                if certificates:
                    return AwaitFurtherState(
                        certificate=certificates[0],
                        certificates=certificates[1:],
                        values=values,
                    )
                else:
                    return OnSuccessState(values=values)

            case TerminatedStateMixin(certificates):
                return HasTerminatedState(
                    certificate=certificates[self.id],
                    certificates={id: c for id, c in certificates.items() if id != self.id},
                )

            case _:
                raise Exception(f"Unexpected state {state}")


@dataclass
class OnErrorTransition(ZipTransition):
    id: int
    n_children: int
    child: ZipTransition

    def get_state(self):
        match state := self.child.get_state():
            case AwaitUpstreamStateMixin(
                certificates=certificates,
                values=values,
            ):
                received_ids = tuple(values.keys())
                awaiting_ids = tuple(id for id in range(self.n_children) if id not in received_ids)
                return OnErrorState(
                    certificates=dict(zip(awaiting_ids, certificates)),
                )
            
            case TerminatedStateMixin(certificates=certificates):
                return HasTerminatedState(
                    certificate=certificates[self.id],
                    certificates={id: c for id, c in certificates.items() if id != self.id},
                )

            case _:
                raise Exception(f"Unexpected state {state}")


@dataclass
class SharedZipMemory:
    observer: Observer
    transition: ZipTransition
    lock: Lock


@dataclass
class ZipObserver[U](Observer[U]):
    id: int
    shared: SharedZipMemory

    def on_success(self, trampoline: Trampoline, item: U) -> ContinuationCertificate:
        transition = OnNextTransition(
            id=self.id,
            child=None,  # type: ignore
            item=item,
        )

        with self.shared.lock:
            transition.child = self.shared.transition
            self.shared.transition = transition

        match state := transition.get_state():
            case OnSuccessState(values=values):
                _, zipped_values = zip(*sorted(values.items()))
                return self.shared.observer.on_success(trampoline, zipped_values)

            case AwaitFurtherState(certificate=certificate):
                return certificate
            
            case TerminatedStateMixin(certificate=certificate):
                return certificate

            case _:
                raise Exception(f"Unexpected state {state}")

    def on_error(self, trampoline: Trampoline, exception: Exception) -> ContinuationCertificate:
        transition = OnErrorTransition(
            id=self.id,
            child=None,  # type: ignore
        )

        with self.shared.lock:
            transition.child = self.shared.transition
            self.shared.transition = transition

        match state := transition.get_state():
            case OnErrorState():
                return self.shared.observer.on_error(trampoline, exception)
            
            case TerminatedStateMixin(certificate=certificate):
                return certificate

            case _:
                raise Exception(f"Unexpected state {state}")


class Zip[U](MultiChildrenContinuationMonadNode[U, tuple[U, ...]]):
    def __str__(self) -> str:
        return f"zip({self.children})"

    def subscribe(
        self,
        args: SubscribeArgs,
    ) -> ContinuationCertificate:
        
        shared = SharedZipMemory(
            observer=args.observer,
            transition=None,
            lock=Lock(),
        )

        def gen_certificates():
            for id, child in enumerate(self.children):

                observer = ZipObserver[U](
                    id=id,
                    shared=shared,
                )

                yield child.subscribe(args=args.copy(
                    observer=observer,
                ))

        certificates = tuple(gen_certificates())

        shared.transition = InitTransition(
            counter=len(self.children),
            certificates=certificates[1:],
        )

        return certificates[0]
