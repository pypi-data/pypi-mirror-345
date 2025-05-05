#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تست‌های واحد برای کلاس Hero.

این ماژول شامل تست‌های واحد برای کلاس Hero است که در پکیج ghahreman تعریف شده است.
"""

import unittest
from ghahreman import Hero


class TestHero(unittest.TestCase):
    """
    کلاس تست برای کلاس Hero.

    این کلاس شامل تست‌های واحد برای کلاس Hero است.
    """

    def test_init_default_parameters(self):
        """
        تست مقادیر پیش‌فرض پارامترهای کلاس Hero.
        """
        hero = Hero()
        self.assertEqual(hero.height1, 1.0)
        self.assertEqual(hero.radius1, 0.5)
        self.assertEqual(hero.height2, 1.0 / 3.0)
        self.assertEqual(hero.radius2, 0.5 * 0.8)
        self.assertEqual(hero.resolution, 30)

    def test_init_custom_parameters(self):
        """
        تست مقادیر سفارشی پارامترهای کلاس Hero.
        """
        hero = Hero(height1=2.0, radius1=1.0, height2=1.0, radius2=0.5, resolution=60)
        self.assertEqual(hero.height1, 2.0)
        self.assertEqual(hero.radius1, 1.0)
        self.assertEqual(hero.height2, 1.0)
        self.assertEqual(hero.radius2, 0.5)
        self.assertEqual(hero.resolution, 60)

    def test_create_cones(self):
        """
        تست ایجاد مخروط‌ها و سایر اجزای تروفی.
        """
        hero = Hero()
        self.assertIsNotNone(hero.cone1)
        self.assertIsNotNone(hero.cone2)
        self.assertIsNotNone(hero.disk)
        self.assertIsNotNone(hero.bottom_disk)
        self.assertIsNotNone(hero.cube)
        self.assertIsNotNone(hero.sphere)
        self.assertIsNotNone(hero.upper_sphere)
        self.assertIsNotNone(hero.handle1)
        self.assertIsNotNone(hero.handle2)


if __name__ == "__main__":
    unittest.main()
