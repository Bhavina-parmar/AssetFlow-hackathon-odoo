from __future__ import annotations

import functools
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def _now_stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Ansi.RESET}"


def log_info(message: str) -> None:
    print(f"[{_now_stamp()}] {colorize('INFO', Ansi.CYAN)}  {message}")


def log_success(message: str) -> None:
    print(f"[{_now_stamp()}] {colorize('OK', Ansi.GREEN)}    {message}")


def log_warn(message: str) -> None:
    print(f"[{_now_stamp()}] {colorize('WARN', Ansi.YELLOW)}  {message}")


def log_error(message: str) -> None:
    print(f"[{_now_stamp()}] {colorize('ERROR', Ansi.RED)} {message}")


@dataclass(slots=True)
class RetryConfig:
    attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 5.0
    jitter: float = 0.25


def retryable(config: RetryConfig) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error: Exception | None = None
            for attempt in range(1, config.attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    if attempt >= config.attempts:
                        break

                    raw_delay = config.base_delay * (2 ** (attempt - 1))
                    delay = min(raw_delay, config.max_delay) + random.uniform(0.0, config.jitter)
                    log_warn(
                        f"{func.__name__} failed (attempt {attempt}/{config.attempts}): {exc}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    time.sleep(delay)

            assert last_error is not None
            raise last_error

        return wrapper

    return decorator


class Stopwatch:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    @property
    def elapsed_seconds(self) -> float:
        return time.perf_counter() - self._start

    def elapsed_human(self) -> str:
        total = int(self.elapsed_seconds)
        mins, secs = divmod(total, 60)
        hrs, mins = divmod(mins, 60)
        if hrs:
            return f"{hrs}h {mins}m {secs}s"
        if mins:
            return f"{mins}m {secs}s"
        return f"{secs}s"


def summarize_exception(prefix: str, exc: Exception, context: dict[str, Any] | None = None) -> str:
    ctx = f" | context={context}" if context else ""
    return f"{prefix}: {exc}{ctx}"
