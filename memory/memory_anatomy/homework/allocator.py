"""
Завдання:
    Є памʼять розміром n, представлена масивом із n комірок (0-індексація).
    Усі комірки спочатку вільні.

    Потрібно реалізувати простий алокатор з двома операціями:
        1.	allocate(size, alloc_id) - знайти лівіший блок із size послідовних вільних комірок,
        позначити їх alloc_id і повернути індекс початку. Якщо такого блоку немає - повернути -1.
        2.	free_memory(alloc_id) - звільнити всі комірки з цим alloc_id та повернути кількість звільнених елементів.

    При цьому:
        - одному alloc_id може належати кілька блоків;
        - free_memory має видаляти всі комірки цього alloc_id, навіть якщо вони були виділені окремими викликами;
        - заборонено створювати копії всього масиву - працюємо напряму з памʼяттю.

Вимоги:
    - Пошук блоку має відбуватися зліва направо;
    - Вільна комірка позначається 0, зайнята - її alloc_id;
    - Операції мають бути ефективними для великих значень n;
    - Заборонено використовувати зайві копії або дублювати структури памʼяті.

Приклад для n = 10:
    allocate(1, 1) -> 0    [1,_,_,_,_,_,_,_,_,_]
    allocate(1, 2) -> 1    [1,2,_,_,_,_,_,_,_,_]
    allocate(1, 3) -> 2    [1,2,3,_,_,_,_,_,_,_]
    free_memory(2) -> 1    [1,_,3,_,_,_,_,_,_,_]
    allocate(3, 4) -> 3    [1,_,3,4,4,4,_,_,_,_]
    allocate(1, 1) -> 1    [1,1,3,4,4,4,_,_,_,_]
    allocate(1, 1) -> 6    [1,1,3,4,4,4,1,_,_,_]
    free_memory(1) -> 3    [_,_,3,4,4,4,_,_,_,_]
    allocate(10, 2) -> -1  неможливо
    free_memory(7) -> 0    нічого не змінюється

Актуальність:
    Це дуже спрощена модель роботи heap-алокатора: пошук першого доступного
    блоку, фрагментація, масове звільнення памʼяті за ідентифікатором.
    Вона допомагає зрозуміти:
        - як алокатори виділяють послідовні ділянки памʼяті;
        - як виникає та впливає фрагментація;
        - чому великі запити можуть не проходити навіть при наявності достатнього загального обсягу памʼяті;
        - логіку "first-fit" та проблеми лінійного пошуку;
        - базові принципи роботи heap у Python (arenas/pools/blocks) у максимально спрощеній формі.
"""


class Allocator:
    def __init__(self, n: int):
        self._container = [0] * n

    def allocate(self, size: int, alloc_id: int) -> int:
        if size <= 0 or size > len(self._container) or alloc_id <= 0:
            return -1

        consecutive_free_blocks = 0
        for current_index in range(len(self._container)):
            if self._container[current_index] == 0:
                consecutive_free_blocks += 1
            else:
                consecutive_free_blocks = 0

            if consecutive_free_blocks == size:
                start_index = current_index - size + 1
                for block_index in range(start_index, current_index + 1):
                    self._container[block_index] = alloc_id
                return start_index
        return -1

    def free_memory(self, alloc_id: int) -> int:
        freed_count = 0
        for current_index in range(len(self._container)):
            if self._container[current_index] == alloc_id:
                self._container[current_index] = 0
                freed_count += 1
        return freed_count
