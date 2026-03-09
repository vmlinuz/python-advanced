import unittest

from initial.homework.call_counter_decorator import call_counter


class TestCallCounterDecorator(unittest.TestCase):
    def test_single_call(self):
        @call_counter
        def foo():
            return 'ok'

        foo()
        self.assertEqual(foo.calls, 1)

    def test_multiple_calls(self):
        @call_counter
        def add(a, b):
            return a + b

        add(1, 2)
        add(3, 4)
        add(5, 6)

        self.assertEqual(add.calls, 3)

    def test_return_value_preserved(self):
        @call_counter
        def multiply(a, b):
            return a * b

        result = multiply(2, 4)
        self.assertEqual(result, 8)
        self.assertEqual(multiply.calls, 1)

    def test_args_and_kwargs(self):
        @call_counter
        def combine(a, b=10):
            return a + b

        combine(5)
        combine(5, b=7)

        self.assertEqual(combine.calls, 2)

    def test_independent_counters(self):
        @call_counter
        def f1():
            return 1

        @call_counter
        def f2():
            return 2

        f1()
        f1()
        f2()

        self.assertEqual(f1.calls, 2)
        self.assertEqual(f2.calls, 1)
