from continuationmonad.continuationmonadtree.nodes import ContinuationMonadNode
from continuationmonad.scheduler.continuationcertificate import ContinuationCertificate
from continuationmonad.scheduler.init import init_main_scheduler, init_trampoline
from continuationmonad.continuationmonadtree.subscribeargs import init_subscribe_args
from continuationmonad.continuationmonadtree.observer import Observer


def run[V](source: ContinuationMonadNode[V]) -> V:
    main_scheduler = init_main_scheduler()
    trampoline = init_trampoline()

    received_exception = []
    received_item = []

    class MainObserver(Observer):
        def on_success(self, _, item: V) -> ContinuationCertificate:
            received_item.append(item)
            return main_scheduler.stop()

        def on_error(self, _, exception: Exception) -> ContinuationCertificate:
            received_exception.append(exception)
            return main_scheduler.stop()

    args = init_subscribe_args(
        observer=MainObserver(),
        trampoline=trampoline,
        weight=1,
    )

    def schedule_task():
        def trampoline_task():
            return source.subscribe(args=args)

        return trampoline.run(trampoline_task, weight=1)

    main_scheduler.run(schedule_task)

    if received_exception:
        raise received_exception[0]

    return received_item[0]
