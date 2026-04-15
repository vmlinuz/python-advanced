"""
Завдання:
    Реалізувати zero-copy аналог slicing для bytes.

Пояснення:
    ByteSlice повинен працювати як view на частину великого буфера.
    Він НЕ має створювати копії bytes при slicing або індексації - тільки
    перераховувати індекси й тримати посилання на один спільний буфер (memoryview).

Вимоги:
    - ByteSlice(data, start, end) -> не копіює дані;
    - bs[i]       -> повертає один байт як int;
    - bs[i:j]     -> повертає новий ByteSlice без копій;
    - len(bs)     -> довжина піддіапазону;
    - bytes(bs)   -> явне створення копії (дозволено);
    - Працює з bytes, bytearray, memoryview.

Що слід реалізувати:
    - усі методи нижче;
    - логіку обробки меж індексів;
    - zero-copy slicing;
    - докладний repr.

Примітка:
    Заборонено використовувати data[start:end] всередині (крім bytes() / to_bytes()).

Актуальність:
    Ця задача показує, як працювати з великими двійковими буферами без зайвих копій -
    важлива техніка у виробничих системах. Zero-copy slicing використовується під час
    парсингу мережевих протоколів (HTTP, gRPC, TCP-фрейми), роботи з великими файлами
    (логи, відео, сенсорні дані), обробки binary-форматів (Protobuf, Avro), у стрімінгу
    та mmap-файлах. У цих випадках один великий буфер часто нарізається на тисячі
    підфрагментів, і класичний bytes-slice створює стільки ж копій у памʼяті.
    Zero-copy дозволяє уникати цих алокацій, працювати напряму з даними і значно
    зменшувати навантаження на RAM та GC.
"""

from __future__ import annotations

from typing import Iterator


class ByteSlice:
    """
    Zero-copy представлення частини bytes/bytearray.

    Слід реалізувати:
        - ініціалізацію з посиланням на memoryview;
        - індексацію;
        - slicing;
        - перетворення в bytes;
        - коректну роботу з негативними індексами;
        - читабельний __repr__.
    """

    __slots__ = ('_buffer', '_start', '_end')

    def __init__(
        self,
        data: bytes | bytearray | memoryview,
        start: int = 0,
        end: int | None = None,
    ):
        """
        Ініціалізація ByteSlice.

        Параметри:
            data  - вихідні bytes або bytearray.
            start - початок піддіапазону.
            end   - кінець піддіапазону (не обовʼязковий).

        Має створювати memoryview(data) та зберігати тільки вказівники.
        Не повинно бути жодних копій даних.
        """
        if isinstance(data, memoryview):
            # Повторно використовуємо існуючий memoryview (zero-copy)
            self._buffer: memoryview = data
        else:
            # Створюємо memoryview поверх bytes/bytearray — без копій
            self._buffer = memoryview(data)

        # Обмежуємо межі довжиною буфера
        buf_len = len(self._buffer)

        normalized_start = max(
            0,
            min(start + buf_len if start < 0 else start, buf_len),
        )

        if end is None:
            raw_end = buf_len
        else:
            raw_end = end + buf_len if end < 0 else end

        normalized_end = max(0, min(raw_end, buf_len))
        self._start: int = normalized_start
        self._end: int = max(self._start, normalized_end)

    def __len__(self) -> int:
        """
        Повернути довжину зрізу.

        Має бути O(1).
        """
        return self._end - self._start

    def __getitem__(self, item: int | slice) -> int | ByteSlice:
        """
        Підтримка індексації та slicing.

        Якщо item - int:
            повернути один байт (int 0–255).

        Якщо item - slice:
            повернути новий ByteSlice, який посилається на той же буфер.

        Заборонено робити копії bytes.
        """
        if isinstance(item, int):
            # Підтримка негативних індексів
            length = len(self)
            original_item = item
            if item < 0:
                item += length
            if item < 0 or item >= length:
                raise IndexError(f'ByteSlice index {original_item} out of range for length {length}')
            # Читаємо один байт за абсолютним зміщенням у буфері
            return self._buffer[self._start + item]

        if isinstance(item, slice):
            # indices() коректно обробляє None, негативні значення та крок
            start, stop, step = item.indices(len(self))
            if step != 1:
                raise ValueError(f'ByteSlice does not support step != 1 (got step={step})')
            return ByteSlice(self._buffer, self._start + start, self._start + stop)

        raise TypeError(f'ByteSlice indices must be integers or slices, not {type(item).__name__}')

    def __iter__(self) -> Iterator[int]:
        """
        Ітерація по байтах, як у звичайних bytes.

        Повертати int для кожного байта.
        """
        buf = self._buffer
        for i in range(self._start, self._end):
            yield buf[i]

    def __bytes__(self) -> bytes:
        """
        Створити копію даних.

        Єдиний дозволений спосіб створення bytes-обʼєкта всередині класу.
        """
        return bytes(self._buffer[self._start : self._end])

    def to_bytes(self) -> bytes:
        """
        Alias для bytes(self).

        Можна викликати руками - повинен повертати копію вмісту ByteSlice.
        """
        return bytes(self)

    def __repr__(self) -> str:
        """
        Повернути зручне текстове представлення.
        Має бути корисно для дебагу.
        """
        # Обмежуємо превʼю, щоб repr не був завеликим
        preview_end = min(self._start + 20, self._end)
        preview = bytes(self._buffer[self._start : preview_end])
        return f'ByteSlice(len={len(self)}, start={self._start}, preview={preview!r})'
