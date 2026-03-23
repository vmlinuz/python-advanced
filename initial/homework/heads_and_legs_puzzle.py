"""
Завдання: Класична давньокитайська задача про голови та ноги

Мета:
    Освіжити знання про:
    - роботу з циклами for та особливостями ітеративних рішень;
    - перебір простору можливих рішень.

Контекст:
    Це класична давньокитайська задача. На фермі є кури (2 ноги) та кролики (4 ноги).
    Відомо загальну кількість голів і ніг. Потрібно визначити, скільки яких тварин є на фермі.

Умова:
    Реалізуйте функцію, яка:
    - приймає кількість голів (num_heads);
    - приймає кількість ніг (num_legs);
    - повертає кількість курей і кроликів.

    Якщо розвʼязку не існує - поверніть (-1, -1).

Вимоги:
    - використовуйте цикл for для перебору можливих варіантів;
    - не використовуйте глобальні змінні;
    - функція не повинна нічого друкувати;
    - повернення результату має бути у вигляді кортежу (chickens, rabbits).

Приклад:
    >>> solve_heads_and_legs(35, 94)
    (23, 12)

Аналітична частина:
    У докстрінгу функції додай відповіді на питання (коротко):
    1. Яка часова складність алгоритму за Big-O нотацією? І чому?
    2. Яка просторова складність за Big-O нотацією? І чому?
"""


def solve_heads_and_legs(num_heads: int, num_legs: int) -> tuple[int, int]:
    """
    1. Time complexity: `O(n)`, where `n` is the number of heads, because one `for` loop is executed to iterate over the possible options.
    2. Space complexity: `O(1)`, because a constant number of additional variables are used.
    """
    if num_heads < 0 or num_legs < 0:
        return -1, -1

    for rabbits in range(num_heads + 1):
        chickens = num_heads - rabbits
        if chickens * 2 + rabbits * 4 == num_legs:
            return chickens, rabbits

    return -1, -1
