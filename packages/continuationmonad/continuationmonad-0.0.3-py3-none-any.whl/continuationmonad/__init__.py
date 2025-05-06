from continuationmonad.scheduler.init import (
    init_current_thread_scheduler as _init_current_thread_scheduler,
    init_event_loop_scheduler as _init_event_loop_scheduler,
    init_main_scheduler as _init_main_scheduler,
    init_trampoline as _init_trampoline,
    init_virtual_time_scheduler as _init_virtual_time_scheduler,
)
from continuationmonad.continuationmonadtree.subscribeargs import (
    init_subscribe_args as _init_subscribe_args,
)
from continuationmonad.continuationmonad.init import (
    init_continuation_monad as _init_continuation_monad,
)
from continuationmonad.continuationmonadtree.observer import (
    init_anonymous_observer as _init_anonymous_observer,
)
from continuationmonad.continuationmonad.from_ import (
    defer as _defer,
    get_trampoline as _get_trampoline,
    error as _error,
    from_ as _from_value,
    zip as _zip,
    schedule_on as _schedule_on,
    schedule_relative as _schedule_relative,
    schedule_absolute as _schedule_absolute,
    schedule_trampoline as _schedule_trampoline,
    tail_rec as _tail_rec,
)
from continuationmonad.continuationmonad.to import (
    fork as _fork,
    run as _run,
)


init_subscribe_args = _init_subscribe_args


# Schedulers
############

init_current_thread_scheduler = _init_current_thread_scheduler
init_event_loop_scheduler = _init_event_loop_scheduler
init_main_scheduler = _init_main_scheduler
init_trampoline = _init_trampoline
init_virtual_time_scheduler = _init_virtual_time_scheduler


init_anonymous_observer = _init_anonymous_observer

# Create continuation source
############################

error = _error
from_ = _from_value
get_trampoline = _get_trampoline
schedule_trampoline = _schedule_trampoline
schedule_on = _schedule_on
schedule_relative = _schedule_relative
schedule_absolute = _schedule_absolute
tail_rec = _tail_rec


# Create continuation from others
#################################

# accumulate = _accumulate
defer = _defer
zip = _zip


# Fork continuation monad on trampoline
#######################################

fork = _fork
run = _run


# Implement your own operator
#############################

from_node = _init_continuation_monad
