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

    def test_origin_country_validation(self):
        """Тест валидации страны регистрации."""
        # Нормальная страна
        airplane = Airplane("ABC123", "TEST", "Germany", 100, 5000, 0, 0)
        self.assertEqual(airplane.origin_country, "Germany")

        # Пустая страна
        airplane = Airplane("ABC123", "TEST", "", 100, 5000, 0, 0)
        self.assertEqual(airplane.origin_country, "Unknown")

