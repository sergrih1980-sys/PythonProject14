import unittest
from src.aeroplane import Airplane


class TestAirplane(unittest.TestCase):
    def test_valid_airplane_creation(self):
        """Тест создания самолёта с корректными данными."""
        airplane = Airplane(
            icao24="ABC123",
            callsign="TEST123",
            origin_country="Russia",
            velocity=200.0,
            altitude=10000.0,
            latitude=55.7558,
            longitude=37.6173
        )
        self.assertEqual(airplane.icao24, "ABC123")
        self.assertEqual(airplane.callsign, "TEST123")
        self.assertEqual(airplane.origin_country, "Russia")
        self.assertEqual(airplane.velocity, 200.0)
        self.assertEqual(airplane.altitude, 10000.0)
        self.assertEqual(airplane.latitude, 55.7558)
        self.assertEqual(airplane.longitude, 37.6173)

    def test_origin_country_validation(self):
        """Тест валидации страны регистрации."""
        # Нормальная страна
        airplane = Airplane("ABC123", "TEST", "Germany", 100, 5000, 0, 0)
        self.assertEqual(airplane.origin_country, "Germany")

        # Пустая страна
        airplane = Airplane("ABC123", "TEST", "", 100, 5000, 0, 0)
        self.assertEqual(airplane.origin_country, "Unknown")

    def test_callsign_validation(self):
        """Тесты валидации позывного."""
        # Корректный позывной
        plane = Airplane("ABC123", "TEST123", "Russia", 0, 0, 0, 0)
        self.assertEqual(plane.callsign, "TEST123")

        # Слишком длинный
        with self.assertRaises(ValueError):
            Airplane("ABC123", "TOO_LONG_CALLSIGN", "Russia", 0, 0, 0, 0)

        # Пустой позывной — должен стать "N/A"
        plane = Airplane("ABC123", "", "Russia", 0, 0, 0, 0)
        self.assertEqual(plane.callsign, "N/A")

        # Пробелы — должны быть убраны
        plane = Airplane("ABC123", "  TEST  ", "Russia", 0, 0, 0, 0)
        self.assertEqual(plane.callsign, "TEST")

    def test_origin_country_validation(self):
        """Тесты валидации страны регистрации."""
        # Корректная страна
        plane = Airplane("ABC123", "TEST", "Russia", 0, 0, 0, 0)
        self.assertEqual(plane.origin_country, "Russia")

        # Пустая страна — должна стать "Unknown"
        plane = Airplane("ABC123", "TEST", "", 0, 0, 0, 0)
        self.assertEqual(plane.origin_country, "Unknown")

        # Пробелы — должны быть убраны
        plane = Airplane("ABC123", "TEST", "  USA  ", 0, 0, 0, 0)
        self.assertEqual(plane.origin_country, "USA")

    def test_velocity_validation(self):
        """Тесты валидации скорости."""
        # Корректная скорость
        plane = Airplane("ABC123", "TEST", "Russia", 150.0, 0, 0, 0)
        self.assertEqual(plane.velocity, 150.0)

        # None — должна стать 0.0
        plane = Airplane("ABC123", "TEST", "Russia", None, 0, 0, 0)
        self.assertEqual(plane.velocity, 0.0)

        # Отрицательная скорость
        with self.assertRaises(ValueError):
            Airplane("ABC123", "TEST", "Russia", -10.0, 0, 0, 0)

        # Слишком высокая скорость
        with self.assertRaises(ValueError):
            Airplane("ABC123", "TEST", "Russia", 300.0, 0, 0, 0)

    def test_altitude_validation(self):
        """Тесты валидации высоты."""
        # Корректная высота
        plane = Airplane("ABC123", "TEST", "Russia", 0, 5000.0, 0, 0)
        self.assertEqual(plane.altitude, 5000.0)

        # None — должна стать 0.0
        plane = Airplane("ABC123", "TEST", "Russia", 0, None, 0, 0)
        self.assertEqual(plane.altitude, 0.0)

        # Слишком низкая высота
        with self.assertRaises(ValueError):
            Airplane("ABC123", "TEST", "Russia", 0, -2000.0, 0, 0)

        # Слишком высокая высота
        with self.assertRaises(ValueError):
            Airplane("ABC123", "TEST", "Russia", 0, 20000.0, 0, 0)

