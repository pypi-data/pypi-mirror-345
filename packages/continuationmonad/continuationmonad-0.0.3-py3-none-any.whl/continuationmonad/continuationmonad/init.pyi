from continuationmonad.continuationmonad.continuationmonad import ContinuationMonad
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadNode

def init_continuation_monad[U](
    child: ContinuationMonadNode[U],
) -> ContinuationMonad[U]: ...
