"""
Завдання:
    Реалізувати FileParseCache - кеш для результатів дорогого парсингу файлів.

    У системі є функція parser(path), яка читає файл і повертає розпарсений результат. Виконання parser може бути
    дорогим, тому потрібно уникати повторного парсингу файлу, якщо файл не змінювався.

    Кеш повинен зберігати результат парсингу для кожного path та перевіряти, чи файл змінився з моменту останнього
    парсингу.

Вимоги:
    - Реалізувати клас FileParseCache;
    - Клас повинен мати метод:
        - get(path) -> повертає розпарсений результат.
    - Якщо файл уже є в кеші і не змінювався:
        - повернути значення з кешу.
    - Якщо файл змінився:
        - повторно викликати parser(path);
        - оновити кеш.

Технічні обмеження:
    - Для перевірки змін файлу можна використовувати:
        - modified time (mtime), або
        - розмір файлу, або
        - комбінацію обох.
    - Заборонено використовувати готові бібліотеки кешування.

Актуальність:
    Подібний тип кешування дуже часто використовується у:
        - конфігураційних системах;
        - data pipelines;
        - ETL/ELT процесах;
        - сервісах, що читають схеми, метадані та правила;
        - системах, які працюють із YAML / JSON / CSV файлами;
        - devtools та build systems.

    Це завдання демонструє одну з найважливіших проблем кешування: недостатньо просто зберегти значення - потрібно ще
    правильно визначити, коли воно застаріло.

    Розуміння інвалідації кешу є критично важливим для backend, data та platform engineers.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from memory.caching.homework.smart_file_parse_cache.generator import JsonConfigGenerator


@dataclass(slots=True, frozen=True)
class FileFingerprint:
    """
    Описує поточний стан файлу.
    Потрібен для перевірки, чи змінився файл з моменту останнього парсингу.
    """

    modified_ns: int
    size: int


@dataclass(slots=True)
class CacheStats:
    """
    Зберігає статистику роботи кешу.
    """

    hits: int = 0
    misses: int = 0
    refreshes: int = 0

    @property
    def total_requests(self) -> int:
        """
        Повертає загальну кількість звернень до кешу.
        Формула:
            hits + misses
        """
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """
        Повертає відсоток cache hit.

        Потрібно:
            - якщо звернень ще не було, повернути 0.0;
            - інакше обчислити hits / total_requests.
        """
        return self.hits / self.total_requests if self.total_requests else 0.0


@dataclass(slots=True)
class _CacheEntry:
    """
    Один запис у кеші.

    Містить:
        - fingerprint файлу;
        - розпарсене значення.
    """

    fingerprint: FileFingerprint
    value: Any


class FileParseCache:
    """
    Кеш результатів дорогого парсингу файлів.

    Ідея:
        - якщо файл не змінювався, повернути значення з кешу;
        - якщо файл змінився, виконати повторний парсинг.
    """

    __slots__ = ('_parser', '_entries', '_stats')

    def __init__(self, parser: Callable[[Path], Any]) -> None:
        self._parser = parser
        self._entries: dict[Path, _CacheEntry] = {}
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        """
        Повертає статистику кешу.
        """
        return self._stats

    @property
    def size(self) -> int:
        """
        Повертає кількість записів у кеші.
        """
        return len(self._entries)

    def get(self, path: Path) -> Any:
        """
        Повертає розпарсений результат для файлу.

        Потрібно:
            - нормалізувати шлях;
            - побудувати fingerprint файлу;
            - перевірити, чи є запис у кеші;
            - якщо fingerprint не змінився -> cache hit;
            - якщо запису немає -> cache miss;
            - якщо fingerprint змінився -> refresh;
            - у випадку miss або refresh викликати parser(path) і оновити кеш.
        """
        path = path.resolve()
        # підніме FileNotFoundError, якщо файл відсутній
        fingerprint = self._build_fingerprint(path)

        entry = self._entries.get(path)

        if entry is not None:
            if entry.fingerprint == fingerprint:
                # файл не змінився — повертаємо кешоване значення
                self._stats.hits += 1
                return entry.value
            # файл змінився — треба оновити кеш
            self._stats.refreshes += 1
        else:
            # перший запит для цього файлу
            self._stats.misses += 1

        value = self._parser(path)
        self._entries[path] = _CacheEntry(fingerprint=fingerprint, value=value)
        return value

    def contains(self, path: Path) -> bool:
        """
        Перевіряє, чи є файл у кеші.
        """
        return path.resolve() in self._entries

    def invalidate(self, path: Path) -> None:
        """
        Видаляє один запис із кешу вручну.
        """
        self._entries.pop(path.resolve(), None)

    def clear(self) -> None:
        """
        Повністю очищає кеш.
        """
        self._entries.clear()

    @staticmethod
    def _build_fingerprint(path: Path) -> FileFingerprint:
        """
        Будує fingerprint файлу.

        Потрібно:
            - отримати stat() для файлу;
            - взяти modified time у наносекундах;
            - взяти розмір файлу;
            - повернути FileFingerprint.
        """
        stat = path.stat()  # підніме FileNotFoundError, якщо файл не існує
        return FileFingerprint(modified_ns=stat.st_mtime_ns, size=stat.st_size)


def parse_json_file(path: Path) -> dict:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def main() -> None:
    generator = JsonConfigGenerator(
        services=5,
        features_per_service=10,
        seed=42,
    )

    path = Path('data/test_config.json')

    generator.generate(path)
    print('Generated initial test file')

    cache = FileParseCache(parser=parse_json_file)

    print('\n--- First access: expected cache miss ---')
    config1 = cache.get(path)
    print('Loaded services:', len(config1['services']))
    print('hits:', cache.stats.hits)
    print('misses:', cache.stats.misses)
    print('refreshes:', cache.stats.refreshes)

    print('\n--- Second access: expected cache hit ---')
    config2 = cache.get(path)
    print('Loaded services:', len(config2['services']))
    print('hits:', cache.stats.hits)
    print('misses:', cache.stats.misses)
    print('refreshes:', cache.stats.refreshes)

    print('\n--- Modify file: expected cache refresh ---')
    generator = JsonConfigGenerator(
        services=6,
        features_per_service=10,
        seed=99,
    )
    generator.generate(path)

    config3 = cache.get(path)
    print('Loaded services after refresh:', len(config3['services']))
    print('hits:', cache.stats.hits)
    print('misses:', cache.stats.misses)
    print('refreshes:', cache.stats.refreshes)

    print('\n--- Manual invalidate: expected miss again ---')
    cache.invalidate(path)
    config4 = cache.get(path)
    print('Loaded services after invalidate:', len(config4['services']))
    print('hits:', cache.stats.hits)
    print('misses:', cache.stats.misses)
    print('refreshes:', cache.stats.refreshes)
    print('hit rate:', f'{cache.stats.hit_rate:.2%}')


if __name__ == '__main__':
    main()
