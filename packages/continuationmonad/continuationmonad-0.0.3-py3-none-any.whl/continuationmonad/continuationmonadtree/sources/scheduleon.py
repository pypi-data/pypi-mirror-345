from abc import abstractmethod

from continuationmonad.scheduler.init import init_trampoline
from continuationmonad.scheduler.instantscheduler import InstantScheduler
from continuationmonad.scheduler.schedulers.trampoline import Trampoline
from continuationmonad.continuationmonadtree.subscribeargs import SubscribeArgs
from continuationmonad.continuationmonadtree.nodes import ContinuationMonadLeave


class ScheduleOn(ContinuationMonadLeave[None]):
    def __str__(self) -> str:
        return f"schedule_on({self.scheduler})"

    @property
    @abstractmethod
    def scheduler(self) -> InstantScheduler: ...

    def _subscribe(
        self,
        args: SubscribeArgs,
    ):
        # def trampoline_task():
        match self.scheduler:
            case Trampoline() as trampoline:

                def trampoline_task():
                    return args.observer.on_success(trampoline, trampoline)

                return trampoline.schedule(
                    task=trampoline_task,
                    weight=args.weight,
                    cancellation=args.cancellation,
                )

            case _:

                def schedule_task():
                    trampoline = init_trampoline()

                    def trampoline_task():
                        return args.observer.on_success(trampoline, trampoline)

                    return trampoline.run(
                        trampoline_task,
                        weight=args.weight,
                        cancellation=args.cancellation,
                    )

                return self.scheduler.schedule(
                    task=schedule_task,
                    weight=args.weight,
                    cancellation=args.cancellation,
                )

        # return args.trampoline.schedule(
        #     task=trampoline_task,
        #     weight=args.weight,
        #     cancellation=args.cancellation,
        # )
