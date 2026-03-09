"""
Завдання: Контекстний менеджер з обмеженням ресурсу

Мета:
    Освіжити знання про:
    - протокол контекстного менеджера (__enter__ / __exit__);
    - контроль та облік ресурсу;
    - збереження стану обʼєкта;
    - гарантоване звільнення ресурсу.

Контекст:
    У реальних системах ресурси обмежені памʼяттю, зʼєднанням, файловими дескрипторами, API quota.
    Контекстний менеджер дозволяє коректно резервувати ресурс і гарантовано повертати його назад.

Умова:
    Реалізуйте контекстний менеджер ResourceQuota, який:

    - має загальний ліміт ресурсу (total_limit);
    - при вході в контекст резервує requested одиниць ресурсу;
    - якщо ресурсу недостатньо - кидає ValueError;
    - при виході з контексту завжди повертає ресурс.

    Ресурс - абстрактний (просто число).

Вимоги:
    - реалізуйте __enter__ та __exit__;
    - не використовуйте глобальні змінні;
    - стан ресурсу має зберігатись у класі;
    - __exit__ повинен звільняти ресурс навіть при винятках.

Приклад:
    quota = ResourceQuota(total_limit=10)
    with quota.request(4):
        pass
"""

from types import TracebackType
from typing import Type


class ResourceQuota:
    def __init__(self, total_limit: int):
        # TODO: initialize total limit and current usage (call the variable 'used')
        ...

    def request(self, amount: int) -> '_QuotaContext':
        # TODO: return a context manager instance
        ...


class _QuotaContext:
    def __init__(self, quota: ResourceQuota, amount: int):
        # TODO: store quota reference and requested amount
        ...

    def __enter__(self) -> int:
        # TODO: reserve resource or raise ValueError
        ...

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        # TODO: release resource
        ...
