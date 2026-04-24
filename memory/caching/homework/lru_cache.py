"""
Завдання:
    Реалізувати структуру даних LRU Cache (Least Recently Used), яка
    підтримує операції get() і put() за O(1) часу.

    LRU Cache має фіксовану місткість. Коли кеш переповнюється,
    необхідно видалити ключ, який використовувався
    найдавніше (least recently used - LRU).

Вимоги:
    - Реалізувати клас LRUCache з методами:
        - get(key) -> повертає значення або -1, якщо ключа немає.
        - put(key, value) -> додає або оновлює значення.
    - Часова складність обох операцій має бути O(1).
    - При додаванні нового елемента:
        - якщо є вільне місце - просто додати;
        - якщо кеш повний - видалити найменш використаний ключ.
    - Будь-яке звернення до ключа (get або put для ключа, що існує)
      робить цей ключ останнім використаним.

Технічні обмеження:
    - Заборонено використовувати готові OrderedDict або LRU-реалізації.
    - Дозволено використовувати:
        - словник для O(1) доступу до вузлів;
        - власну реалізацію двозв’язного списку для порядку LRU.
    - Заборонено створювати зайві копії даних.

Актуальність:
    LRU Cache є однією з найважливіших структур у сучасних високонавантажених
    системах. Вона використовується в:
        - кешах веб-серверів та API-гейтвеїв;
        - внутрішніх кешах Python-інтерпретатора (наприклад, bytecode cache);
        - СУБД та файлових системах;
        - Redis, Memcached, CDN-сервісах;
        - оптимізації ML-моделей, коли необхідно кешувати попередні результати.

    Розуміння механіки LRU - це базова навичка для backend/infra/ML-інженера,
    оскільки він поєднує роботу зі структурами даних, керування пам’яттю,
    оптимізацію доступу та алгоритмічне мислення.
"""

from __future__ import annotations


class _Node:
    """Вузол двозв'язного списку для зберігання пари ключ-значення."""

    __slots__ = ('key', 'val', 'prev', 'next')

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: _Node | None = None
        self.next: _Node | None = None


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError(f'capacity must be a positive integer, got {capacity}')
        self._capacity = capacity
        # Словник: ключ → вузол, забезпечує O(1) доступ
        self._cache: dict[int, _Node] = {}
        # Сторожові вузли: head.next — LRU, tail.prev — MRU
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    # --- Допоміжні методи роботи зі списком ---

    @staticmethod
    def _remove(node: _Node) -> None:
        """Відв'язує вузол зі списку."""
        node.prev.next = node.next  # type: ignore[union-attr]
        node.next.prev = node.prev  # type: ignore[union-attr]

    def _insert_tail(self, node: _Node) -> None:
        """Вставляє вузол перед хвостовим сторожем (позиція MRU)."""
        prev = self._tail.prev
        prev.next = node  # type: ignore[union-attr]
        node.prev = prev
        node.next = self._tail
        self._tail.prev = node

    # --- Публічний інтерфейс ---

    def get(self, key: int) -> int:
        """Повертає значення за ключем або -1, якщо ключ відсутній. O(1)."""
        if key not in self._cache:
            return -1
        node = self._cache[key]
        # Переміщуємо до хвоста як нещодавно використаний
        self._remove(node)
        self._insert_tail(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        """Додає або оновлює значення. При переповненні видаляє LRU-елемент. O(1)."""
        if key in self._cache:
            # Оновлюємо існуючий вузол і переміщуємо до хвоста
            node = self._cache[key]
            node.val = value
            self._remove(node)
            self._insert_tail(node)
        else:
            if len(self._cache) == self._capacity:
                # Видаляємо найменш використаний вузол (перший після head)
                lru = self._head.next
                self._remove(lru)  # type: ignore[arg-type]
                del self._cache[lru.key]  # type: ignore[union-attr]
            node = _Node(key, value)
            self._cache[key] = node
            self._insert_tail(node)
