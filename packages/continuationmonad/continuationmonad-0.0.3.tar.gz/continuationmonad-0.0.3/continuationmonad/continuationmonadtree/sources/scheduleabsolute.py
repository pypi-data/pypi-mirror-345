from abc import abstractmethod
import datetime

from continuationmonad.scheduler.scheduler import Scheduler
from continuationmonad.scheduler.init import init_trampoline
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave


class ScheduleAbsolute(ContinuationMonadLeave[None]):
    def __str__(self) -> str:
        return f"schedule_absolute({self.scheduler}, {self.duetime})"

    @property
    @abstractmethod
    def duetime(self) -> datetime.datetime: ...

    @property
    @abstractmethod
    def scheduler(self) -> Scheduler: ...

    def _subscribe(
        self,
        args: SubscribeArgs,
    ):
        def schedule_task():
            trampoline = init_trampoline()

            def trampoline_task():
                return args.observer.on_success(trampoline, trampoline)

            return trampoline.run(
                trampoline_task,
                weight=args.weight,
                cancellation=args.cancellation,
            )

        return self.scheduler.schedule_absolute(
            duetime=self.duetime,
            task=schedule_task,
            weight=args.weight,
            cancellation=args.cancellation,
        )
