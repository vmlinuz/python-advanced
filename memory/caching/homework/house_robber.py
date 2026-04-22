"""
Реалізувати задачу "House Robber" трьома методами динамічного програмування:
    1) Рекурсія з memoization (Top-Down) - O(n) пам’яті;
    2) Табуляція (Bottom-Up) з масивом - O(n) пам’яті;
    3) Оптимізована версія (Bottom-Up) з O(1) пам’яттю - опціонально.

Завдання:
    Є список будинків, де кожен елемент - сума грошей у будинку.
    Злодій не може грабувати два сусідні будинки.
    Потрібно повернути максимальну суму, яку можна викрасти.

    Опціонально - намалювати діаграму роботи алгоритму для мемоізації та табуляції

Актуальність:
    Три підходи демонструють еволюцію алгоритмів динамічного програмування:
        - Memoization: простий для розуміння, але рекурсивний;
        - Табуляція: ітеративний, контрольований, без рекурсії;
        - Оптимізований варіант: максимально ефективний по пам’яті.
    Такі техніки широко використовуються у кешуванні, оптимізації
    підзадач, аналізі часової/просторової складності та реальних
    системах з обмеженнями по пам’яті.
"""

from functools import lru_cache
from typing import Iterable


class HouseRobberMemoized:
    """House Robber - рекурсія + мемоізація (Top-Down Dynamic Programming)."""

    @staticmethod
    def rob(nums: Iterable[int]) -> int:
        houses = tuple(nums)  # потрібен hashable тип для lru_cache

        @lru_cache(maxsize=None)
        def dp(i: int) -> int:
            """Максимальний прибуток починаючи з індексу i."""
            if i >= len(houses):
                return 0
            # або грабуємо поточний і пропускаємо наступний,
            # або пропускаємо поточний
            return max(houses[i] + dp(i + 2), dp(i + 1))

        return dp(0)


class HouseRobberTabulated:
    """House Robber - табуляція (Bottom-Up Dynamic Programming)."""

    @staticmethod
    def rob(nums: Iterable[int]) -> int:
        houses = list(nums)
        n = len(houses)
        if not n:
            return 0
        if n == 1:
            return houses[0]

        # dp[i] — максимальний прибуток для перших i+1 будинків
        dp = [0] * n
        dp[0] = houses[0]
        dp[1] = max(houses[0], houses[1])

        for i in range(2, n):
            dp[i] = max(dp[i - 1], houses[i] + dp[i - 2])

        return dp[-1]


class HouseRobberOptimized:
    """House Robber - оптимізована табуляція з O(1) памʼяттю. Опціонально"""

    @staticmethod
    def rob(nums: Iterable[int]) -> int:
        # prev2 — dp[i-2], prev1 — dp[i-1]
        prev2 = prev1 = 0
        for house in nums:
            prev2, prev1 = prev1, max(prev1, house + prev2)
        return prev1
