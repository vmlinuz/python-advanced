"""
Billion Row Challenge - реалізація на Dask

Завдання:
    Файл містить температурні вимірювання у форматі:
        <station>;<temperature>

    Приклад:
        Hamburg;12.3
        Kyiv;-5.0
        Amsterdam;7.1
        Kyiv;2.3

    Для кожної станції потрібно обчислити:
        min / mean / max

    Формат фінального результату:
        station -> "min/mean/max"

    Наприклад:
        {
            "Amsterdam": "7.1/7.1/7.1",
            "Hamburg": "12.3/12.3/12.3",
            "Kyiv": "-5.0/-1.4/2.3",
        }

Що потрібно реалізувати:
    Потрібно реалізувати dask-based підхід, у якому:
        - файл читається partition-ами;
        - для читання CSV використовується PyArrow engine;
        - обчислення виконуються паралельно;
        - агрегація виконується через DataFrame API;
        - результат обчислюється тільки при виклику compute().

Обмеження та фокус:
    - основний акцент реалізації на Dask;
    - не потрібно зчитувати файл у пам'ять повністю;
    - важливо зрозуміти принцип lazy execution.

Актуальність:
    У реальних системах обробки великих даних файли можуть містити десятки або сотні мільярдів рядків.
    Обробка таких даних у чистому Python або навіть у pandas може бути занадто повільною або вимагати
    занадто багато пам'яті.

    Dask дозволяє масштабувати знайомий pandas API на великі дані, використовуючи:
        - partition-based execution;
        - lazy computation graph;
        - parallel execution.

    Тому цей підхід часто використовують у data engineering,
    batch processing та data science pipelines.
"""

from __future__ import annotations

import time

from dataclasses import dataclass
from pathlib import Path

import dask.dataframe as dd


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    def mean(self) -> float:
        """
        Повертає середнє значення температури.
        """
        if self.count == 0:
            raise ZeroDivisionError('Cannot compute mean when count is 0.')
        return self.sum_value / self.count


class DaskMeasurementsAggregator:
    def __init__(self, chunk_size: str = '128MB'):
        """
        Ініціалізує агрегатор.
        chunk_size: розмір partition для читання CSV.
        """
        self._chunk_size = chunk_size
        # Словник станція -> агреговані статистики
        self._stats: dict[str, StationStats] = {}

    def process_file(self, path: Path) -> None:
        """
        Основний метод обробки файлу.
        Потрібно реалізувати:
        1. Прочитати файл через dd.read_csv(...) - краще використати engine="pyarrow";
        2. Виконати агрегацію df.groupby;
        3. Викликати compute(), щоб отримати pandas DataFrame.
        """
        # Лінивe читання CSV з розбиттям на партиції
        df = dd.read_csv(
            path,
            sep=';',
            header=None,
            names=['station', 'temperature'],
            blocksize=self._chunk_size,
            engine='pyarrow',
        )

        # Групування та агрегація — обчислення відбувається лише при compute()
        agg = df.groupby('station')['temperature'].agg(['min', 'max', 'sum', 'count']).compute()

        # Перетворюємо pandas DataFrame у словник StationStats
        for station, row in agg.iterrows():
            self._stats[station] = StationStats(
                min_value=float(row['min']),
                max_value=float(row['max']),
                sum_value=float(row['sum']),
                count=int(row['count']),
            )

    def render_sorted(self) -> dict[str, str]:
        """
        Формує фінальний результат.
        Потрібно:
            - відсортувати станції за назвою;
            - обчислити mean через StationStats.mean();
            - сформувати рядок "min_value/mean/max_value".
        """
        return {
            station: f'{s.min_value:.1f}/{s.mean():.1f}/{s.max_value:.1f}'
            for station, s in sorted(self._stats.items())
            if s.count > 0
        }


def main():
    BASE_DIR = Path(__file__).parent

    agg = DaskMeasurementsAggregator()
    print('Running aggregation...')
    t2 = time.perf_counter()
    agg.process_file(BASE_DIR / 'data/measurements.txt')
    result = agg.render_sorted()
    t3 = time.perf_counter()

    print(f'Aggregation completed in {t3 - t2:.2f}s')
    print(f'Stations processed: {len(result)}')


if __name__ == '__main__':
    main()
