from abc import abstractmethod

from continuationmonad.scheduler.scheduler import Scheduler
from continuationmonad.scheduler.init import init_trampoline
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave


class ScheduleRelative(ContinuationMonadLeave[None]):
    def __str__(self) -> str:
        return f"schedule_relative({self.scheduler}, {self.duetime})"

    @property
    @abstractmethod
    def duetime(self) -> float: ...

    @property
    @abstractmethod
    def scheduler(self) -> Scheduler: ...

    def _subscribe(
        self,
        args: SubscribeArgs,
    ):
        # def trampoline_task():
        def schedule_task():
            trampoline = init_trampoline()

            def trampoline_task():
                return args.observer.on_success(trampoline, trampoline)

            return trampoline.run(
                trampoline_task,
                weight=args.weight,
                cancellation=args.cancellation,
            )

        return self.scheduler.schedule_relative(
            duetime=self.duetime,
            task=schedule_task,
            weight=args.weight,
            cancellation=args.cancellation,
        )
