from dataclasses import replace
from typing import override
from dataclassabc import dataclassabc

from continuationmonad.continuationmonad.continuationmonad import ContinuationMonad
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadNode


@dataclassabc(frozen=True, slots=True)
class ContinuationMonadImpl(ContinuationMonad):
    child: ContinuationMonadNode

    def __str__(self) -> str:
        return f"ContinuationMonad({self.child})"

    @override
    def copy(self, /, **changes) -> ContinuationMonad:
        return replace(self, **changes)


def init_continuation_monad(child: ContinuationMonadNode):
    return ContinuationMonadImpl(child=child)
