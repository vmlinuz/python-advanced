"""
Завдання:
    Реалізувати аналіз великого лог-файлу та знайти максимальну суму значень duration у ковзному вікні з K рядків.

    Формат рядка:
        timestamp;service;duration

    Приклад:
        1719921001;auth;34

    Необхідно:
        - прочитати лог-файл;
        - витягнути значення duration;
        - знайти максимальну суму у ковзному вікні розміру K.

Вимоги:
    - файл може містити десятки мільйонів рядків;
    - рішення має працювати потоково (streaming);
    - заборонено завантажувати весь файл у памʼять;
    - необхідно мінімізувати кількість алокацій;
    - не створювати зайві списки або копії рядків;

Технічні обмеження:
    - дозволено використовувати стандартну бібліотеку Python;
    - заборонено pandas / numpy;
    - заборонено читати файл повністю в памʼять;
    - бажано уникати зайвих split() та list().

Актуальність:
    Аналіз великих логів є типовою задачею у системах observability, monitoring та distributed systems.

    У production-системах такі задачі часто обробляють терабайти даних, тому оптимальне використання памʼяті
    та мінімізація алокацій є критично важливими.

    Це завдання тренує:
        - streaming обробку даних;
        - оптимізацію алокацій;
        - ефективні структури даних;
        - роботу з ковзними вікнами;
        - memory-efficient Python код.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from memory.memory_anatomy.homework.log_window_analyzer.generator import LogFileGenerator


@dataclass(slots=True, frozen=True)
class WindowResult:
    """
    Результат аналізу лог-файлу.
    """

    max_window_sum: int
    window_size: int
    processed_rows: int


class LogWindowAnalyzer:
    """
    Аналізатор великого лог-файлу.
    Необхідно знайти максимальну суму значень duration у ковзному вікні розміру K.
    """

    def __init__(self, window_size: int):
        if window_size <= 0:
            raise ValueError('window_size must be greater than 0')

        self._window_size = window_size

    def process_file(self, path: Path) -> WindowResult:
        """
        Відкрити файл та передати файловий потік у метод _process_stream.
        """
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return self._process_stream(f)

    def _process_stream(self, stream: TextIO) -> WindowResult:
        """
        Потоково обробити лог-файл.

        Потрібно:
            - читати файл рядок за рядком;
            - витягувати duration через _parse_duration();
            - підтримувати ковзне вікно розміру self._window_size;
            - знайти максимальну суму duration у цьому вікні.

        Важливо:
            - не можна читати файл повністю в памʼять;
            - не створювати зайві списки;
            - мінімізувати кількість алокацій.
        """
        self._processed_sliding_window_rows = 0
        self._current_window_sum = 0
        self._max_window_sum = 0
        processed_rows = 0

        for line in stream:
            line = line.strip()
            if not line:
                continue

            duration = self._parse_duration(line)
            self._process_duration(duration)
            processed_rows += 1

        return WindowResult(self._max_window_sum, self._window_size, processed_rows)

    @staticmethod
    def _parse_last_int(s: str, delim: str = ";") -> int:
        if delim not in s:
            raise ValueError("delimiter not found")

        i = s.rfind(delim)
        if i + 1 >= len(s):
            raise ValueError("no integer after delimiter")

        n = 0
        for j in range(i + 1, len(s)):
            d = ord(s[j]) - ord("0")
            if d < 0 or d > 9:
                raise ValueError(f"non-digit character: {s[j]!r}")
            n = n * 10 + d

        return n

    @staticmethod
    def _parse_duration(line: str) -> int:
        """
        Витягнути значення duration з рядка формату:
            timestamp;service;duration

        Заборонено:
            - використовувати split(), щоб уникнути зайвих алокацій.
        """
        return LogWindowAnalyzer._parse_last_int(line)

    def _process_duration(self, duration: int) -> None:
        """
        Оновити стан ковзного вікна для нового значення duration.
        Метод має підтримувати ковзне вікно розміру self._window_size та знайти максимальну суму duration у цьому вікні.
        """
        if self._processed_sliding_window_rows == 0:
            self._window_values = [0] * self._window_size
            self._window_index = 0

        if self._processed_sliding_window_rows < self._window_size:
            self._window_values[self._window_index] = duration
            self._current_window_sum += duration
            self._processed_sliding_window_rows += 1
        else:
            old_duration = self._window_values[self._window_index]
            self._window_values[self._window_index] = duration
            self._current_window_sum += duration - old_duration

        self._window_index += 1
        if self._window_index == self._window_size:
            self._window_index = 0

        if (
                self._processed_sliding_window_rows == self._window_size
                and self._current_window_sum > self._max_window_sum
        ):
            self._max_window_sum = self._current_window_sum


def main() -> None:
    generator = LogFileGenerator(
        services=('auth', 'payments', 'search', 'profile'),
        duration_min=5,
        duration_max=300,
    )

    generator.generate(
        path=Path('data/test_logs.txt'),
        rows=5_000_000,
    )

    analyzer = LogWindowAnalyzer(window_size=3)

    result = analyzer.process_file(Path('data/test_logs.txt'))

    print(f'Processed rows: {result.processed_rows}')
    print(f'Window size: {result.window_size}')
    print(f'Max window sum: {result.max_window_sum}')


if __name__ == '__main__':
    main()
