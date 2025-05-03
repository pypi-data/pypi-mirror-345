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
    TypeVar,
    Generic,
)
from dataclasses import dataclass

# Define a generic type variable for the result of the async function
T = TypeVar("T")

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(task_id)s] %(message)s"
)
log = logging.getLogger(__name__)


class SimpleTaskIdFilter(logging.Filter):
    """Ensures that log records have a 'task_id' attribute."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Adds a default task_id if it's missing."""
        if not hasattr(record, "task_id"):
            record.task_id = "[Unknown]"
        return True


# Remove any pre-existing filters that might conflict (optional, defensive)
for f in log.filters[:]:
    if type(f).__name__ == "TaskIdFilter": # Check for a specific older filter name if needed
        log.removeFilter(f)

# Add the filter to the logger instance
log.addFilter(SimpleTaskIdFilter())


# --- Type Hinting ---
AsyncTaskFunc: TypeAlias = Callable[..., Coroutine[Any, Any, T]]


# --- Result Data Structures ---
@dataclass
class TaskResultBase:
    """Base class for task results."""
    task_id: int
    duration: float
    total_attempts_made: int


@dataclass
class TaskSuccess(TaskResultBase, Generic[T]):
    """Represents a successfully completed task."""
    status: str = "success"
    result: Optional[T] = None # Use the generic type T for the result


@dataclass
class TaskFailure(TaskResultBase):
    """Represents a failed task."""
    error: Optional[BaseException | str] = None
    status: str = "failed"


# --- Runner Class ---
class ResilientTaskRunner(Generic[T]):
    """
    Runs asynchronous tasks with concurrency control, retries, and dynamic timeouts.

    Manages a queue of tasks, executes them respecting concurrency limits,
    handles failures with configurable retries and backoff, and adjusts
    attempt timeouts based on historical performance.
    """

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
        """
        Initializes the ResilientTaskRunner.

        Args:
            max_concurrency: Maximum number of tasks to run concurrently.
            max_attempts: Total maximum attempts per task (1 initial + N retries).
            retry_delay_seconds: Base delay before the first retry (exponential backoff used).
            default_attempt_timeout_seconds: Timeout for each task attempt if dynamic timeouts
                                             are disabled or lack data. None means no timeout.
            enable_dynamic_timeouts: Whether to adjust attempt timeouts based on history.
            min_completed_for_stats: Min successful tasks needed for dynamic timeouts.
            completed_duration_history_size: Max history size for dynamic timeout calculation.
            straggler_percentile: Percentile of successful durations for dynamic timeout base.
            straggler_factor: Multiplier for the percentile duration to get dynamic timeout.

        Raises:
            ValueError: If configuration parameters are invalid (e.g., non-positive).
        """
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
        if not (0 < straggler_percentile <= 100):
             raise ValueError("straggler_percentile must be between 0 (exclusive) and 100 (inclusive)")
        if straggler_factor <= 0:
             raise ValueError("straggler_factor must be positive")


        self.max_concurrency: int = max_concurrency
        self.max_attempts: int = max_attempts
        self.retry_delay_seconds: float = retry_delay_seconds
        self.default_attempt_timeout_seconds: Optional[float] = default_attempt_timeout_seconds

        self.enable_dynamic_timeouts: bool = enable_dynamic_timeouts
        self.min_completed_for_stats: int = min_completed_for_stats
        self.completed_duration_history_size: int = completed_duration_history_size
        self.straggler_percentile: float = straggler_percentile
        self.straggler_factor: float = straggler_factor

        # Internal state
        self._tasks_to_run: List[Tuple[int, AsyncTaskFunc[T], tuple, dict]] = []
        self._results: Dict[int, TaskSuccess[T] | TaskFailure] = {}
        self._next_task_id: int = 0
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._logger: logging.LoggerAdapter = logging.LoggerAdapter(log, {"task_id": "Runner"})
        self._completed_durations: Deque[float] = deque(
            maxlen=self.completed_duration_history_size
        )
        self._state_lock: asyncio.Lock = asyncio.Lock()

    def add_task(self, func: AsyncTaskFunc[T], *args: Any, **kwargs: Any) -> int:
        """
        Adds an asynchronous task function and its arguments to the runner's queue.

        Args:
            func: The asynchronous function (coroutine function) to execute.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The unique ID assigned to this task.
        """
        task_id = self._next_task_id
        self._next_task_id += 1
        self._tasks_to_run.append((task_id, func, args, kwargs))
        self._logger.debug(f"Added Task-{task_id} ({func.__name__}) to queue.")
        return task_id

    async def _get_dynamic_attempt_timeout(self) -> Optional[float]:
        """
        Calculates the attempt timeout based on recent successful task durations.

        If dynamic timeouts are disabled or not enough data is available,
        falls back to the default attempt timeout.

        Returns:
            The calculated timeout in seconds, or None if no timeout should be applied.
        """
        if not self.enable_dynamic_timeouts:
            return self.default_attempt_timeout_seconds

        async with self._state_lock:
            if len(self._completed_durations) < self.min_completed_for_stats:
                self._logger.debug(
                    f"Not enough completed tasks ({len(self._completed_durations)} < "
                    f"{self.min_completed_for_stats}) for dynamic timeout, using default."
                )
                return self.default_attempt_timeout_seconds
            try:
                # Ensure enough distinct data points for quantiles if n=100
                if len(set(self._completed_durations)) < 2 and self.straggler_percentile != 100:
                     self._logger.warning(
                         "Insufficient distinct data points for percentile calculation, using default."
                     )
                     return self.default_attempt_timeout_seconds

                # Use max if percentile is 100 to avoid issues with quantiles function
                if self.straggler_percentile == 100:
                    percentile_duration = max(self._completed_durations)
                else:
                    # Calculate percentile (e.g., 90th percentile)
                    # Note: statistics.quantiles needs at least 2 data points for n=100
                    percentiles = statistics.quantiles(self._completed_durations, n=100)
                    percentile_index = min(int(self.straggler_percentile), len(percentiles) - 1)
                    percentile_duration = percentiles[percentile_index]

                dynamic_timeout = percentile_duration * self.straggler_factor
                self._logger.debug(
                    f"Calculated dynamic timeout: {dynamic_timeout:.2f}s "
                    f"(based on {self.straggler_percentile}th percentile={percentile_duration:.2f}s * {self.straggler_factor})"
                )
                # Optional: Add a minimum timeout value?
                # dynamic_timeout = max(dynamic_timeout, 1.0) # Example minimum
                return dynamic_timeout
            except statistics.StatisticsError:
                self._logger.warning(
                    "StatisticsError during dynamic timeout calculation (likely insufficient data), using default."
                )
                return self.default_attempt_timeout_seconds
            except Exception as e:
                self._logger.error(
                    f"Error calculating dynamic timeout: {e}", exc_info=True
                )
                return self.default_attempt_timeout_seconds

    async def _worker(
        self, task_id: int, func: AsyncTaskFunc[T], args: tuple, kwargs: dict
    ) -> None:
        """
        Internal worker coroutine that manages a single task's lifecycle.

        Handles semaphore acquisition, execution attempts, timeouts, retries,
        and result recording for one task added via `add_task`.

        Args:
            task_id: The unique ID of the task.
            func: The async function to execute.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.
        """
        task_logger = logging.LoggerAdapter(log, {"task_id": f"Task-{task_id}"})
        start_time: float = time.monotonic()
        exec_start_time: float = 0.0  # Time after acquiring semaphore
        total_attempts_made: int = 0
        final_status: str = "unknown"
        error_detail: Optional[BaseException | str] = None
        result_detail: Optional[T] = None
        last_exception: Optional[BaseException] = None

        try:
            # --- Semaphore Acquisition ---
            if self._semaphore is None:
                 # Should not happen if run() is called first, but defensive check
                 raise RuntimeError("Semaphore not initialized. Call run() first.")
            async with self._semaphore:
                exec_start_time = time.monotonic()
                task_logger.info(
                    f"Starting execution (concurrency: {self.max_concurrency - self._semaphore._value}/{self.max_concurrency})"
                )

                # --- Attempt Loop ---
                current_attempt_timeout: Optional[float] = await self._get_dynamic_attempt_timeout()

                for attempt in range(self.max_attempts):
                    total_attempts_made = attempt + 1
                    attempt_start_time = time.monotonic()
                    task_logger.debug(
                        f"Starting attempt {total_attempts_made}/{self.max_attempts} with timeout {current_attempt_timeout}s"
                    )

                    try:
                        # --- Execute Task with Attempt Timeout ---
                        async with asyncio.timeout(current_attempt_timeout):
                            result_detail = await func(*args, **kwargs)
                            final_status = "success"
                            task_logger.debug(
                                f"Attempt {total_attempts_made} succeeded in {time.monotonic() - attempt_start_time:.2f}s."
                            )
                            break  # Exit attempt loop on success

                    except asyncio.TimeoutError as e:
                        last_exception = e
                        task_logger.warning(
                            f"Attempt {total_attempts_made} timed out after {current_attempt_timeout}s."
                        )
                        # Timeout doubling happens before next retry below

                    except asyncio.CancelledError as e:
                        # Treat as final failure - likely external cancellation
                        last_exception = e
                        task_logger.error(
                            f"Attempt {total_attempts_made} cancelled externally."
                        )
                        final_status = "cancelled"
                        error_detail = e
                        break  # Exit loop immediately

                    except Exception as e:
                        # Catch any other exception during task execution
                        last_exception = e
                        task_logger.warning(
                            f"Attempt {total_attempts_made} failed with {type(e).__name__}: {e}"
                        )
                        # Timeout doubling happens before next retry below

                    # --- Retry Logic ---
                    if final_status == "success" or final_status == "cancelled":
                        break # Already handled

                    if total_attempts_made < self.max_attempts:
                        # Double timeout for the *next* attempt, regardless of failure reason
                        if current_attempt_timeout is not None:
                            current_attempt_timeout *= 2
                            task_logger.info(
                                f"Increasing timeout for next attempt to {current_attempt_timeout}s"
                            )

                        # Calculate delay with exponential backoff and jitter
                        delay = self.retry_delay_seconds * (2**attempt)
                        delay += random.uniform(-delay * 0.1, delay * 0.1) # +/- 10% jitter
                        delay = max(0, delay) # Ensure non-negative delay
                        task_logger.info(f"Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
                    else:
                        # Max attempts reached
                        task_logger.error(
                            f"Failed after maximum {self.max_attempts} attempts. Last error: {type(last_exception).__name__ if last_exception else 'None'}"
                        )
                        if isinstance(last_exception, asyncio.TimeoutError):
                            final_status = "failed_timeout"
                        elif isinstance(last_exception, asyncio.CancelledError):
                            # Should have been caught earlier, but handle defensively
                            final_status = "cancelled"
                        else:
                            final_status = "failed_exception"
                        error_detail = last_exception # Store the last known exception
                        break # Exit loop

        except asyncio.CancelledError:
             # Catch cancellation that happens *outside* the attempt loop (e.g., during semaphore wait)
             final_status = "cancelled"
             error_detail = asyncio.CancelledError("Task cancelled during worker processing (outside attempt loop).")
             task_logger.error(str(error_detail))
        except Exception as e:
            # Catch unexpected errors during semaphore acquisition or other worker logic
            final_status = "error_worker"
            error_detail = e
            task_logger.error(f"Unexpected worker error: {type(e).__name__}: {e}", exc_info=True)

        finally:
            # --- Cleanup and Result Recording ---
            end_time = time.monotonic()
            total_duration = end_time - start_time
            task_logger.info(
                f"Finished with status '{final_status}' in {total_duration:.2f}s after {total_attempts_made} attempts"
            )

            # Record execution duration (excluding wait time) for successful tasks
            async with self._state_lock:
                if final_status == "success" and exec_start_time > 0:
                    exec_duration = end_time - exec_start_time
                    self._completed_durations.append(exec_duration)
                    task_logger.debug(f"Recorded successful execution duration: {exec_duration:.2f}s")

            # Store final result
            if final_status == "success":
                self._results[task_id] = TaskSuccess(
                    task_id=task_id,
                    duration=total_duration,
                    result=result_detail,
                    total_attempts_made=total_attempts_made,
                )
            else:
                # Ensure error_detail is serializable if it's an exception
                error_repr = repr(error_detail) if isinstance(error_detail, BaseException) else str(error_detail)
                self._results[task_id] = TaskFailure(
                    task_id=task_id,
                    duration=total_duration,
                    status=final_status,
                    error=error_repr, # Store representation
                    total_attempts_made=total_attempts_made,
                )
            # Semaphore released automatically by 'async with' context manager

    async def run(self) -> Tuple[List[TaskSuccess[T]], List[TaskFailure]]:
        """
        Runs all tasks added to the queue.

        Initializes the semaphore, creates worker tasks for each queued function,
        and waits for them to complete using asyncio.gather.

        Returns:
            A tuple containing two lists:
            - List of TaskSuccess objects for successfully completed tasks
            - List of TaskFailure objects for failed tasks
        """
        if not self._tasks_to_run:
            self._logger.warning("No tasks added to run.")
            return [], []

        self._semaphore = asyncio.Semaphore(self.max_concurrency)
        self._results = {} # Clear previous results
        async with self._state_lock:
            self._completed_durations.clear() # Clear previous durations

        self._logger.info(f"Starting runner for {len(self._tasks_to_run)} tasks with max_concurrency={self.max_concurrency}...")

        worker_tasks: List[asyncio.Task] = []
        for task_id, func, args, kwargs in self._tasks_to_run:
            # Create a task for each worker coroutine
            coro = self._worker(task_id, func, args, kwargs)
            task = asyncio.create_task(coro, name=f"TaskWorker-{task_id}")
            worker_tasks.append(task)

        # Wait for all worker tasks to complete
        # return_exceptions=True ensures gather doesn't stop on the first error
        # in a worker, allowing us to collect all results.
        await asyncio.gather(*worker_tasks, return_exceptions=True)

        self._logger.info(f"Runner finished processing {len(self._tasks_to_run)} initial tasks.")

        # Clear the queue for the next run, if any
        self._tasks_to_run = []

        # Separate results into successes and failures
        successes: List[TaskSuccess[T]] = []
        failures: List[TaskFailure] = []
        for result in self._results.values():
             if isinstance(result, TaskSuccess):
                 successes.append(result)
             elif isinstance(result, TaskFailure):
                 failures.append(result)

        self._logger.info(f"Run summary: {len(successes)} successes, {len(failures)} failures.")
        return successes, failures

# Example usage removed for library packaging