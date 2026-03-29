import unittest
import os
import json
from unittest.mock import patch, mock_open
from src.aeroplane import Airplane
from src.file_saver import JSONFileConnector


class TestJSONFileConnector(unittest.TestCase):
    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.test_filename = "test_airplanes.json"
        self.connector = JSONFileConnector(self.test_filename)

        # Создаём тестовые самолёты
        self.plane1 = Airplane(
            icao24="ABC123",
            callsign="TEST123",
            origin_country="Russia",
            velocity=200.0,
            altitude=10000.0,
            latitude=55.7558,
            longitude=37.6173
        )
        self.plane2 = Airplane(
            icao24="DEF456",
            callsign="FLY456",
            origin_country="USA",
            velocity=150.0,
            altitude=8000.0,
            latitude=40.7128,
            longitude=-74.0060
        )

    def tearDown(self):
        """Очистка после каждого теста."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)


    def test_add_airplane_success(self):
        """Тест успешного добавления самолёта."""
        result = self.connector.add_airplane(self.plane1)
        self.assertTrue(result)
        self.assertIn(self.plane1, self.connector._airplanes)


    def test_get_airplanes_no_criteria(self):
        """Тест получения всех самолётов без критериев."""
        self.connector.add_airplane(self.plane1)
        self.connector.add_airplane(self.plane2)

        result = self.connector.get_airplanes()
        self.assertEqual(len(result), 2)
        self.assertIn(self.plane1, result)
        self.assertIn(self.plane2, result)


    def test_get_airplanes_by_country(self):
        """Тест фильтрации по стране."""
        self.connector.add_airplane(self.plane1)  # Russia
        self.connector.add_airplane(self.plane2)  # USA

        result = self.connector.get_airplanes(country="Russia")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].origin_country, "Russia")


    def test_get_airplanes_by_speed(self):
        """Тест фильтрации по скорости."""
        self.connector.add_airplane(self.plane1)  # 720 км/ч
        self.connector.add_airplane(self.plane2)  # 540 км/ч

        # Самолёты со скоростью > 600 км/ч
        result = self.connector.get_airplanes(min_speed=600)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].icao24, "ABC123")

        # Самолёты со скоростью < 600 км/ч
        result = self.connector.get_airplanes(max_speed=600)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].icao24, "DEF456")
