"""
Реалізувати комплексний декоратор для профілювання пам'яті в Python.

Завдання:
    Створити декоратор @memory_profile, який вимірює ключові метрики використання памʼяті.
    Формат вільний. Зробити так, як буде зручно саме тобі, щоб використовувати його для аналізу коду.
    Ідеї, що може виконувати декоратор:
        - Знімати snapshots памʼяті ДО та ПІСЛЯ виконання функції.
        - Фіксувати:
            - сумарні алокації між snapshots;
            - поточне та пікове використання памʼяті;
            - час виконання функції;
            - RSS процесу до/після.
        - Показувати топ-рядків коду, що створили найбільше алокацій.
        - Визначати "hotspots" - ймовірні місця створення копій (за кількістю та розміром алокацій).

Актуальність:
    Глибоке профілювання пам'яті - критична навичка для оптимізації Python коду,
    де великі структури даних, копії та зайві алокації можуть створювати
    приховані ботлнеки. Це дозволяє зрозуміти, де саме виникають копії,
    яка пікова памʼять потрібна коду, і як поводиться програма під навантаженням.
    Це фундаментальна техніка для систем високої пропускної здатності,
    асинхронних сервісів та задач інжинірингу даних.
"""

from __future__ import annotations

import functools
import os
import time
import tracemalloc

from dataclasses import dataclass, field
from typing import Any, Callable

import psutil


@dataclass(slots=True)
class AllocationLine:
    """Контейнер для інформації про алокації, згруповані за рядком коду."""

    file: str
    lineno: int
    size_bytes: int
    count: int


@dataclass(slots=True)
class MemoryReport:
    """Звіт про використання памʼяті для однієї функції."""

    func_name: str
    # Timing
    elapsed_seconds: float
    # tracemalloc deltas
    current_memory_bytes: int
    peak_memory_bytes: int
    total_allocated_bytes: int  # Sum of all positive Deltas
    # RSS (Resident Set Size) via psutil
    rss_before_bytes: int
    rss_after_bytes: int
    # Top-N allocation rows (sorted by size in descending order)
    top_allocations: list[AllocationLine] = field(default_factory=list)
    # Hotspots: Rows with an above-average number of allocations
    hotspots: list[AllocationLine] = field(default_factory=list)

    @property
    def rss_delta_bytes(self) -> int:
        return self.rss_after_bytes - self.rss_before_bytes

    def print_report(self) -> None:
        mb = 1024 * 1024
        print(f'\n{"=" * 72}')
        print(f'  Memory Profile: {self.func_name}')
        print(f'{"=" * 72}')
        print(f'  Elapsed          : {self.elapsed_seconds:.4f} s')
        print(f'  tracemalloc cur  : {self.current_memory_bytes / mb:.2f} MiB')
        print(f'  tracemalloc peak : {self.peak_memory_bytes / mb:.2f} MiB')
        print(f'  Σ allocated      : {self.total_allocated_bytes / mb:.2f} MiB')
        print(f'  RSS before       : {self.rss_before_bytes / mb:.2f} MiB')
        print(f'  RSS after        : {self.rss_after_bytes / mb:.2f} MiB')
        print(f'  RSS delta        : {self.rss_delta_bytes / mb:+.2f} MiB')

        if self.top_allocations:
            print('\n  Top allocations:')
            for a in self.top_allocations:
                print(f'    {a.file}:{a.lineno}  ' f'{a.size_bytes / 1024:.1f} KiB  ({a.count} blocks)')

        if self.hotspots:
            print('\n  Hotspots (above-average block count):')
            for h in self.hotspots:
                print(f'    {h.file}:{h.lineno}  ' f'{h.count} blocks  ({h.size_bytes / 1024:.1f} KiB)')
        print(f'{"=" * 72}\n')


def _rss_bytes() -> int:
    """Поточна RSS-карта вашого власного процесу."""
    return psutil.Process(os.getpid()).memory_info().rss


def _build_allocation_lines(
    snapshot_before: tracemalloc.Snapshot,
    snapshot_after: tracemalloc.Snapshot,
    top_n: int,
) -> tuple[list[AllocationLine], int]:
    """Порівнює два знімки; надає інформацію про перші N рядків та загальний розподіл."""
    stats = snapshot_after.compare_to(snapshot_before, 'lineno')

    lines: list[AllocationLine] = []
    total_allocated = 0
    for stat in stats:
        if stat.size_diff > 0:
            total_allocated += stat.size_diff
            lines.append(
                AllocationLine(
                    file=str(stat.traceback),
                    lineno=stat.traceback[0].lineno if stat.traceback else 0,
                    size_bytes=stat.size_diff,
                    count=stat.count_diff,
                )
            )

    lines.sort(key=lambda a: a.size_bytes, reverse=True)
    return lines[:top_n], total_allocated


def _find_hotspots(allocations: list[AllocationLine]) -> list[AllocationLine]:
    """Ряди з кількістю блоків вище середньої."""
    if not allocations:
        return []
    avg_count = sum(a.count for a in allocations) / len(allocations)
    return sorted(
        [a for a in allocations if a.count > avg_count],
        key=lambda a: a.count,
        reverse=True,
    )


def memory_profile(
    _func: Callable | None = None,
    *,
    top_n: int = 10,
    print_on_call: bool = True,
) -> Callable:
    """
    Декоратор для профілювання пам'яті.

    Використання:
        @memory_profile
        def work(): ...

        @memory_profile(top_n=5, print_on_call=False)
        def work(): ...

    Після виклику декорованої функції доступний атрибут
    ``func.last_report`` типу ``MemoryReport``.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # --- before ---
            tracemalloc.start()
            snap_before = tracemalloc.take_snapshot()
            rss_before = _rss_bytes()
            t0 = time.perf_counter()

            # --- call ---
            result = func(*args, **kwargs)

            # --- after ---
            t1 = time.perf_counter()
            snap_after = tracemalloc.take_snapshot()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rss_after = _rss_bytes()

            # --- analyse ---
            top_allocs, total_alloc = _build_allocation_lines(snap_before, snap_after, top_n)
            hotspots = _find_hotspots(top_allocs)

            report = MemoryReport(
                func_name=func.__qualname__,
                elapsed_seconds=t1 - t0,
                current_memory_bytes=current,
                peak_memory_bytes=peak,
                total_allocated_bytes=total_alloc,
                rss_before_bytes=rss_before,
                rss_after_bytes=rss_after,
                top_allocations=top_allocs,
                hotspots=hotspots,
            )
            wrapper.last_report = report  # type: ignore[attr-defined]

            if print_on_call:
                report.print_report()

            return result

        wrapper.last_report = None  # type: ignore[attr-defined]
        return wrapper

    # allowed @memory_profile und @memory_profile(top_n=5)
    if _func is not None:
        return decorator(_func)
    return decorator


if __name__ == '__main__':
    # --- Example 1: basic usage (auto-prints report) ---
    @memory_profile
    def create_big_list() -> list[int]:
        return [i**2 for i in range(1_000_000)]

    result = create_big_list()
    print(f'List length: {len(result)}')

    # --- Example 2: custom top_n, silent mode ---
    @memory_profile(top_n=5, print_on_call=False)
    def build_dict() -> dict[int, str]:
        return {i: str(i) for i in range(500_000)}

    build_dict()
    # access the report programmatically
    report = build_dict.last_report
    print(
        f'\n[silent mode] peak = {report.peak_memory_bytes / 1024:.1f} KiB, '
        f'elapsed = {report.elapsed_seconds:.4f} s'
    )
    # …or print it manually whenever you want
    report.print_report()
