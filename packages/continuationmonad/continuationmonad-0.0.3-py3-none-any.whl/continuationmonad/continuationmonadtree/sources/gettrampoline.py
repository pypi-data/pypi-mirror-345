from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave


class GetTrampoline(ContinuationMonadLeave[Trampoline]):
    def __str__(self) -> str:
        return 'get_trampoline()'

    def _subscribe(
        self,
        args: SubscribeArgs,
    ):
        return args.observer.on_success(args.trampoline, args.trampoline)

        # def trampoline_task():
        #     return args.observer.on_success(args.trampoline, args.trampoline)

        # return args.trampoline.schedule(
        #     task=trampoline_task,
        #     weight=args.weight,
        #     cancellation=args.cancellation,
        # )
