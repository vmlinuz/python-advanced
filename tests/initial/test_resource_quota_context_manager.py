import unittest

from initial.homework.resource_quota_context_manager import ResourceQuota


class TestResourceQuota(unittest.TestCase):
    def test_simple_allocation(self):
        quota = ResourceQuota(10)

        with quota.request(4):
            self.assertEqual(quota.used, 4)

        self.assertEqual(quota.used, 0)

    def test_nested_allocation(self):
        quota = ResourceQuota(10)

        with quota.request(3):
            self.assertEqual(quota.used, 3)

            with quota.request(5):
                self.assertEqual(quota.used, 8)

            self.assertEqual(quota.used, 3)

        self.assertEqual(quota.used, 0)

    def test_exceed_limit(self):
        quota = ResourceQuota(5)

        with quota.request(3):
            with self.assertRaises(ValueError):
                with quota.request(4):
                    pass

        self.assertEqual(quota.used, 0)

    def test_release_on_exception(self):
        quota = ResourceQuota(5)

        try:
            with quota.request(4):
                raise RuntimeError('boom')
        except RuntimeError:
            pass

        self.assertEqual(quota.used, 0)
