from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs


class TContinuationMonadNode(ContinuationMonadLeave):
    def _subscribe(
        self,
        args: SubscribeArgs[U],
    ) -> ContinuationCertificate:
        pass
