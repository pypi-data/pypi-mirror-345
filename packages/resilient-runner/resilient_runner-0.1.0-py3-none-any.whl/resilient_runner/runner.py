import asyncio
import time
import logging
import random
import statistics
from collections import deque
from typing import (
    Any,
    Callable,
    Coroutine,
    List,
    Tuple,
    Dict,
    Optional,
    TypeAlias,
    Deque,
)
from dataclasses import dataclass


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(task_id)s] %(message)s"
)
log = logging.getLogger(__name__)


class SimpleTaskIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "task_id"):
            record.task_id = "[Unknown]"
        return True


for f in log.filters[:]:
    if type(f).__name__ == "TaskIdFilter":
        log.removeFilter(f)


log.addFilter(SimpleTaskIdFilter())


AsyncTaskFunc: TypeAlias = Callable[..., Coroutine[Any, Any, Any]]


@dataclass
class TaskResultBase:
    task_id: int
    duration: float
    total_attempts_made: int


@dataclass
class TaskSuccess(TaskResultBase):
    status: str = "success"
    result: Any = None


@dataclass
class TaskFailure(TaskResultBase):
    error: BaseException | str = None
    status: str = "failed"


@dataclass
class RunningTaskInfo:
    task: asyncio.Task
    start_time: float


class ResilientTaskRunner:
    def __init__(
        self,
        max_concurrency: int = 10,
        max_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
        default_attempt_timeout_seconds: Optional[float] = 30.0,
        enable_dynamic_timeouts: bool = True,
        min_completed_for_stats: int = 5,
        completed_duration_history_size: int = 50,
        straggler_percentile: float = 90.0,
        straggler_factor: float = 2.5,
    ):
        if not isinstance(max_concurrency, int) or max_concurrency <= 0:
            raise ValueError("max_concurrency must be a positive integer")
        if not isinstance(max_attempts, int) or max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer")
        if not isinstance(retry_delay_seconds, (int, float)) or retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be non-negative")
        if default_attempt_timeout_seconds is not None and (
            not isinstance(default_attempt_timeout_seconds, (int, float))
            or default_attempt_timeout_seconds <= 0
        ):
            raise ValueError(
                "default_attempt_timeout_seconds must be None or a positive number"
            )

        self.max_concurrency = max_concurrency
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.default_attempt_timeout_seconds = default_attempt_timeout_seconds

        self.enable_dynamic_timeouts = enable_dynamic_timeouts
        self.min_completed_for_stats = min_completed_for_stats
        self.completed_duration_history_size = completed_duration_history_size
        self.straggler_percentile = straggler_percentile
        self.straggler_factor = straggler_factor

        self._tasks_to_run: List[Tuple[int, AsyncTaskFunc, tuple, dict]] = []
        self._results: Dict[int, TaskSuccess | TaskFailure] = {}
        self._next_task_id = 0
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._logger = logging.LoggerAdapter(log, {"task_id": "Runner"})
        self._completed_durations: Deque[float] = deque(
            maxlen=self.completed_duration_history_size
        )
        self._state_lock = asyncio.Lock()

    def add_task(self, func: AsyncTaskFunc, *args, **kwargs):
        """Adds a task to the runner's queue."""
        task_id = self._next_task_id
        self._next_task_id += 1
        self._tasks_to_run.append((task_id, func, args, kwargs))
        self._logger.debug(f"Added Task-{task_id} ({func.__name__}) to queue.")

    async def _get_dynamic_attempt_timeout(self) -> Optional[float]:
        """Calculates timeout based on recent completed tasks, falls back to default."""
        if not self.enable_dynamic_timeouts:
            return self.default_attempt_timeout_seconds

        async with self._state_lock:
            if len(self._completed_durations) < self.min_completed_for_stats:
                return self.default_attempt_timeout_seconds
            try:
                percentile_duration = statistics.quantiles(
                    self._completed_durations, n=100
                )[int(self.straggler_percentile)]
                dynamic_timeout = percentile_duration * self.straggler_factor
                return dynamic_timeout
            except statistics.StatisticsError:
                self._logger.warning(
                    "Monitor: Could not calculate statistics for dynamic timeout."
                )
                return self.default_attempt_timeout_seconds
            except Exception as e:
                self._logger.error(
                    f"Error calculating dynamic timeout: {e}", exc_info=True
                )
                return self.default_attempt_timeout_seconds

    async def _worker(
        self, task_id: int, func: AsyncTaskFunc, args: tuple, kwargs: dict
    ):
        """Manages the execution attempts, timeouts, and retries for a single task."""
        task_logger = logging.LoggerAdapter(log, {"task_id": f"Task-{task_id}"})
        start_time = time.monotonic()
        exec_start_time = 0.0
        total_attempts_made = 0
        final_status = "unknown"
        error_detail: Optional[BaseException | str] = None
        result_detail: Any = None

        try:
            async with self._semaphore:
                exec_start_time = time.monotonic()
                task_logger.info(
                    f"Starting execution (concurrency: {self.max_concurrency - self._semaphore._value}/{self.max_concurrency})"
                )

                last_exception = None
                current_attempt_timeout = await self._get_dynamic_attempt_timeout()

                for attempt in range(self.max_attempts):
                    total_attempts_made = attempt + 1
                    task_logger.debug(
                        f"Starting attempt {total_attempts_made}/{self.max_attempts} with timeout {current_attempt_timeout}s"
                    )

                    try:
                        async with asyncio.timeout(current_attempt_timeout):
                            result_detail = await func(*args, **kwargs)
                            final_status = "success"
                            task_logger.debug(
                                f"Attempt {total_attempts_made} succeeded."
                            )
                            break

                    except asyncio.TimeoutError as e:
                        last_exception = e
                        task_logger.warning(
                            f"Attempt {total_attempts_made} timed out after {current_attempt_timeout}s."
                        )

                    except asyncio.CancelledError as e:
                        last_exception = e
                        task_logger.error(
                            f"Attempt {total_attempts_made} cancelled externally."
                        )
                        final_status = "cancelled"
                        error_detail = e
                        break

                    except Exception as e:
                        last_exception = e
                        task_logger.warning(
                            f"Attempt {total_attempts_made} failed with {type(e).__name__}: {e}"
                        )

                    if final_status == "success" or final_status == "cancelled":
                        break

                    if total_attempts_made < self.max_attempts:
                        if current_attempt_timeout is not None:
                            current_attempt_timeout *= 2
                            task_logger.info(
                                f"Increasing timeout for next attempt to {current_attempt_timeout}s"
                            )

                        delay = self.retry_delay_seconds * (2**attempt)
                        delay += random.uniform(-delay * 0.1, delay * 0.1)
                        delay = max(0, delay)
                        task_logger.info(f"Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
                    else:
                        task_logger.error(
                            f"Failed after maximum {self.max_attempts} attempts."
                        )
                        if isinstance(last_exception, asyncio.TimeoutError):
                            final_status = "failed_timeout"
                        elif isinstance(last_exception, asyncio.CancelledError):
                            final_status = "cancelled"
                        else:
                            final_status = "failed_exception"
                        error_detail = last_exception
                        break

        except Exception as e:
            final_status = "error_worker"
            error_detail = e
            task_logger.error(f"Worker error: {type(e).__name__}: {e}", exc_info=True)

        finally:
            end_time = time.monotonic()
            duration = end_time - start_time
            task_logger.info(
                f"Finished with status '{final_status}' in {duration:.2f}s after {total_attempts_made} attempts"
            )

            async with self._state_lock:
                if final_status == "success" and exec_start_time > 0:
                    exec_duration = end_time - exec_start_time
                    self._completed_durations.append(exec_duration)

            if final_status == "success":
                self._results[task_id] = TaskSuccess(
                    task_id=task_id,
                    duration=duration,
                    result=result_detail,
                    total_attempts_made=total_attempts_made,
                )
            else:
                self._results[task_id] = TaskFailure(
                    task_id=task_id,
                    duration=duration,
                    status=final_status,
                    error=error_detail,
                    total_attempts_made=total_attempts_made,
                )

    async def run(self) -> Tuple[List[TaskSuccess], List[TaskFailure]]:
        if not self._tasks_to_run:
            self._logger.warning("No tasks added to run.")
            return [], []
        self._semaphore = asyncio.Semaphore(self.max_concurrency)
        self._results = {}
        async with self._state_lock:
            self._completed_durations.clear()
        self._logger.info(f"Starting runner for {len(self._tasks_to_run)} tasks...")
        worker_tasks = []
        for task_id, func, args, kwargs in self._tasks_to_run:
            coro = self._worker(task_id, func, args, kwargs)
            worker_tasks.append(asyncio.create_task(coro, name=f"TaskWorker-{task_id}"))
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        self._logger.info("Runner finished.")
        self._tasks_to_run = []
        successes = [r for r in self._results.values() if isinstance(r, TaskSuccess)]
        failures = [r for r in self._results.values() if isinstance(r, TaskFailure)]
        return successes, failures

# Example usage removed for library packaging