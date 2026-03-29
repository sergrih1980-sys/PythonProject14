import unittest
import os
import json
from unittest.mock import patch, mock_open
from src.aeroplane import Airplane
from src.file_saver import JSONFileConnector  # замените на актуальный путь

class TestJSONFileConnector(unittest.TestCase):
    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.connector = JSONFileConnector("test_airplanes.json")
        # Создаём тестовый самолёт — теперь гарантированно доступен во всех тестах
        self.test_plane = Airplane(
            icao24="ABC123",
            callsign="TEST123",
            origin_country="Russia",
            velocity=200.0,
            altitude=10000.0,
            latitude=55.7558,
            longitude=37.6173
        )

    def tearDown(self):
        """Очистка после каждого теста."""
        if os.path.exists("test_airplanes.json"):
            os.remove("test_airplanes.json")

    def test_add_airplane_success(self):
        """Тест успешного добавления самолёта."""
        result = self.connector.add_airplane(self.test_plane)
        self.assertTrue(result)
        self.assertEqual(len(self.connector._airplanes), 1)
        self.assertEqual(self.connector._airplanes[0].icao24, "ABC123")

    def test_add_airplane_duplicate(self):
        """Тест добавления дубликата самолёта."""
        self.connector.add_airplane(self.test_plane)
        result = self.connector.add_airplane(self.test_plane)
        self.assertFalse(result)

    def test_get_airplanes_no_criteria(self):
        """Тест получения всех самолётов без критериев."""
        self.connector.add_airplane(self.test_plane)
        result = self.connector.get_airplanes()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].icao24, "ABC123")

    def test_get_airplanes_by_country(self):
        """Тест фильтрации по стране."""
        plane1 = Airplane("ABC123", "TEST1", "Russia", 200, 10000, 55, 37)
        plane2 = Airplane("DEF456", "TEST2", "USA", 150, 8000, 40, -74)
        self.connector.add_airplane(plane1)
        self.connector.add_airplane(plane2)

        result = self.connector.get_airplanes(country="Russia")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].origin_country, "Russia")

    def test_get_airplanes_by_speed_range(self):
        """Тест фильтрации по диапазону скорости."""
        plane1 = Airplane("ABC123", "FAST", "Russia", 250, 10000, 55, 37)  # 900 км/ч
        plane2 = Airplane("DEF456", "SLOW", "Russia", 50, 8000, 40, -74)  # 180 км/ч
        self.connector.add_airplane(plane1)
        self.connector.add_airplane(plane2)

        # Самолёты со скоростью от 100 до 200 км/ч (попадает только SLOW)
        result = self.connector.get_airplanes(min_speed=100, max_speed=200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].callsign, "SLOW")

    def test_get_airplanes_by_flight_status(self):
        """Тест фильтрации по статусу полёта."""
        plane1 = Airplane("ABC123", "INFLIGHT", "Russia", 200, 200, 55, 37)   # в полёте
        plane2 = Airplane("DEF456", "ONGROUND", "Russia", 0, 50, 40, -74)     # на земле
        self.connector.add_airplane(plane1)
        self.connector.add_airplane(plane2)

        in_flight = self.connector.get_airplanes(in_flight=True)
        on_ground = self.connector.get_airplanes(in_flight=False)

        self.assertEqual(len(in_flight), 1)
        self.assertEqual(in_flight[0].callsign, "INFLIGHT")
        self.assertEqual(len(on_ground), 1)
        self.assertEqual(on_ground[0].callsign, "ONGROUND")

    def test_remove_airplane_success(self):
        """Тест успешного удаления самолёта."""
        # Добавляем самолёт перед удалением
        self.connector.add_airplane(self.test_plane)
        result = self.connector.remove_airplane("ABC123")
        self.assertTrue(result)
        self.assertEqual(len(self.connector._airplanes), 0)

    def test_remove_airplane_not_found(self):
        """Тест удаления несуществующего самолёта."""
        result = self.connector.remove_airplane("NONEXIST")
        self.assertFalse(result)

    def test_update_airplane_success(self):
        """Тест успешного обновления самолёта."""
        self.connector.add_airplane(self.test_plane)
        result = self.connector.update_airplane("ABC123", velocity=250.0)
        self.assertTrue(result)
        updated_plane = self.connector._airplanes[0]
        self.assertEqual(updated_plane.velocity, 250.0)

    def test_update_airplane_invalid_field(self):
        """Тест обновления несуществующего поля."""
        self.connector.add_airplane(self.test_plane)
        result = self.connector.update_airplane("ABC123", nonexistent_field="value")
        self.assertFalse(result)

    def test_save_all_success(self):
        """Тест успешного сохранения в файл."""
        self.connector.add_airplane(self.test_plane)
        result = self.connector.save_all()
        self.assertTrue(result)
        # Проверяем, что файл создан и содержит данные
        self.assertTrue(os.path.exists("test_airplanes.json"))
        with open("test_airplanes.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['icao24'], "ABC123")

    def test_load_all_new_file(self):
        """Тест загрузки из несуществующего файла (должен создать пустой список)."""
        # Удаляем файл, если он существует
        if os.path.exists("test_airplanes.json"):
            os.remove("test_airplanes.json")
        result = self.connector.load_all()
        self.assertTrue(result)
        self.assertEqual(len(self.connector._airplanes), 0)

