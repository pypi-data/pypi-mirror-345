import random
import threading
import uuid
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import BotSession
from buildgrid.server.context import current_instance, instance_context
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.threading import ContextWorker

from .properties import PropertySet, hash_from_dict

if TYPE_CHECKING:
    # Avoid circular import
    from .impl import Scheduler


LOGGER = buildgrid_logger(__name__)


class JobAssigner:
    def __init__(
        self,
        scheduler: "Scheduler",
        property_set: PropertySet,
        job_assignment_interval: float,
        priority_percentage: int,
        instance_pools: list[list[str]],
    ):
        self._lock = threading.Lock()
        # dict[frozenset[Instance], dict[Hash, dict[BotName, dict[Key, Event]]]]
        self._events: dict[frozenset[str], dict[str, dict[str, dict[str, threading.Event]]]] = {}
        self._scheduler = scheduler
        self._property_set = property_set
        # Here we allow immediately starting a new assignment if a bot is added to the lookup.
        self._new_bots_added = threading.Event()
        self.assigner = ContextWorker(
            target=self.begin, name="JobAssignment", on_shutdown_requested=self._new_bots_added.set
        )
        self.job_assignment_interval = job_assignment_interval
        self.priority_percentage = priority_percentage
        self.instance_pools = instance_pools

    def __enter__(self) -> "JobAssigner":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        self.assigner.start()

    def stop(self) -> None:
        self.assigner.stop()

    def instance_key(self, instance_name: str) -> frozenset[str]:
        for pool in self.instance_pools:
            if instance_name in pool:
                return frozenset(pool)
        return frozenset([instance_name])

    def listener_count(self, instance_name: str | None = None) -> int:
        with self._lock:
            return len(
                {
                    bot_name
                    for event_instance_names, instance_events in self._events.items()
                    if instance_name is None or instance_name in event_instance_names
                    for bot_events in instance_events.values()
                    for bot_name in bot_events
                }
            )

    @contextmanager
    def assignment_context(self, bot_session: BotSession) -> Iterator[threading.Event]:
        key = str(uuid.uuid4())
        event = threading.Event()
        worker_hashes = set(map(hash_from_dict, self._property_set.worker_properties(bot_session)))
        instance_key = self.instance_key(current_instance())
        try:
            with self._lock:
                self._events.setdefault(instance_key, {})
                for worker_hash in worker_hashes:
                    self._events[instance_key].setdefault(worker_hash, {})
                    self._events[instance_key][worker_hash].setdefault(bot_session.name, {})
                    self._events[instance_key][worker_hash][bot_session.name][key] = event
            self._new_bots_added.set()
            yield event
        finally:
            with self._lock:
                for worker_hash in worker_hashes:
                    del self._events[instance_key][worker_hash][bot_session.name][key]
                    if len(self._events[instance_key][worker_hash][bot_session.name]) == 0:
                        del self._events[instance_key][worker_hash][bot_session.name]
                    if len(self._events[instance_key][worker_hash]) == 0:
                        del self._events[instance_key][worker_hash]
                if len(self._events[instance_key]) == 0:
                    del self._events[instance_key]

    def assign_jobs(
        self, shutdown_requested: threading.Event, instance_key: frozenset[str], oldest_first: bool = False
    ) -> None:
        """Assign jobs to the currently connected workers

        This method iterates over the buckets of currently connected workers,
        and requests a number of job assignments from the scheduler to cover
        the number of workers in each bucket. Empty buckets are skipped.
        """

        with self._lock:
            worker_hashes = list(self._events.get(instance_key, {}).keys())

        random.shuffle(worker_hashes)
        for worker_hash in worker_hashes:
            if shutdown_requested.is_set():
                return

            with self._lock:
                bot_names = list(self._events.get(instance_key, {}).get(worker_hash, {}))

            if bot_names:
                if oldest_first:
                    assigned_bot_names = self._scheduler.assign_n_leases_by_age(
                        capability_hash=worker_hash, bot_names=bot_names
                    )
                else:
                    assigned_bot_names = self._scheduler.assign_n_leases_by_priority(
                        capability_hash=worker_hash, bot_names=bot_names
                    )
                with self._lock:
                    for name in assigned_bot_names:
                        for event in self._events.get(instance_key, {}).get(worker_hash, {}).get(name, {}).values():
                            event.set()

    def begin(self, shutdown_requested: threading.Event) -> None:
        while not shutdown_requested.is_set():
            oldest_first = random.randint(1, 100) > self.priority_percentage

            with self._lock:
                instance_keys = list(self._events)

            for instance_key in instance_keys:
                try:
                    # Use one instance name to report metrics on.
                    # To make this deterministic, sort and take the first value.
                    with instance_context(sorted(instance_key)[0]):
                        self.assign_jobs(shutdown_requested, instance_key, oldest_first=oldest_first)
                except Exception:
                    LOGGER.exception(
                        "Error in job assignment thread.",
                        tags=dict(instance_names=",".join(instance_key)),
                        exc_info=True,
                    )

            self._new_bots_added.wait(timeout=self.job_assignment_interval)
            self._new_bots_added.clear()
