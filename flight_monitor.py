import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


# === КЛАСС AIRPLANE ===
class Airplane:
    """Класс для представления информации о самолёте."""
    __slots__ = ('icao24', 'callsign', 'origin_country', 'velocity', 'altitude', 'latitude', 'longitude')

    def __init__(self, icao24, callsign, origin_country, velocity, altitude, latitude, longitude):
        self.icao24 = self._validate_icao24(icao24)
        self.callsign = self._validate_callsign(callsign)
        self.origin_country = self._validate_origin_country(origin_country)
        self.velocity = self._validate_velocity(velocity)
        self.altitude = self._validate_altitude(altitude)
        self.latitude = self._validate_latitude(latitude)
        self.longitude = self._validate_longitude(longitude)

    # Приватные методы валидации
    def _validate_icao24(self, icao24):
        if not isinstance(icao24, str):
            raise ValueError("ICAO24 должен быть строкой")
        if len(icao24) != 6:
            raise ValueError("ICAO24 должен содержать ровно 6 символов")
        try:
            int(icao24, 16)
        except ValueError:
            raise ValueError("ICAO24 должен содержать только шестнадцатеричные символы (0–9, A–F)")
        return icao24.upper()

    def _validate_callsign(self, callsign):
        if not isinstance(callsign, str):
            raise ValueError("Позывной должен быть строкой")
        callsign = callsign.strip()
        if len(callsign) > 8:
            raise ValueError("Позывной не должен превышать 8 символов")
        if not callsign:
            return "N/A"
        return callsign

    def _validate_origin_country(self, origin_country):
        if not isinstance(origin_country, str):
            raise ValueError("Страна регистрации должна быть строкой")
        origin_country = origin_country.strip()
        if not origin_country:
            return "Unknown"
        return origin_country

    def _validate_velocity(self, velocity):
        if velocity is None:
            return 0.0
        try:
            velocity = float(velocity)
        except (TypeError, ValueError):
            raise ValueError("Скорость должна быть числом")
        if velocity < 0:
            raise ValueError("Скорость не может быть отрицательной")
        if velocity > 250:
            raise ValueError("Скорость слишком высока (максимум 250 м/с)")
        return velocity

    def _validate_altitude(self, altitude):
        if altitude is None:
            return 0.0
        try:
            altitude = float(altitude)
        except (TypeError, ValueError):
            raise ValueError("Высота должна быть числом")
        if altitude < -1000:
            raise ValueError("Высота слишком низкая (минимум −1000 м)")
        if altitude > 15000:
            raise ValueError("Высота слишком высокая (максимум 15 000 м)")
        return altitude

    def _validate_latitude(self, latitude):
        try:
            latitude = float(latitude)
        except (TypeError, ValueError):
            raise ValueError("Широта должна быть числом")
        if latitude < -90 or latitude > 90:
            raise ValueError("Широта должна быть в диапазоне от −90 до 90 градусов")
        return latitude

    def _validate_longitude(self, longitude):
        try:
            longitude = float(longitude)
        except (TypeError, ValueError):
            raise ValueError("Долгота должна быть числом")
        if longitude < -180 or longitude > 180:
            raise ValueError("Долгота должна быть в диапазоне от −180 до 180 градусов")
        return longitude

    # Методы сравнения (по высоте полёта, при равной высоте — по скорости)
    def __eq__(self, other):
        if not isinstance(other, Airplane):
            return NotImplemented
        return (self.altitude == other.altitude and
                self.velocity == other.velocity)

    def __lt__(self, other):
        if not isinstance(other, Airplane):
            return NotImplemented
        if self.altitude != other.altitude:
            return self.altitude < other.altitude
        return self.velocity < other.velocity

    def __le__(self, other):
        return self < other or self == other


    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    # Вспомогательные методы
    def get_speed_kmh(self):
        """Возвращает скорость в км/ч (м/с × 3.6)."""
        return self.velocity * 3.6

    def is_in_flight(self):
        """Проверяет, находится ли самолёт в полёте (высота > 100 м)."""
        return self.altitude > 100

    def to_dict(self):
        """Преобразует объект в словарь для сериализации."""
        return {
            'icao24': self.icao24,
            'callsign': self.callsign,
            'origin_country': self.origin_country,
            'velocity': self.velocity,
            'altitude': self.altitude,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed_kmh': self.get_speed_kmh(),
            'is_in_flight': self.is_in_flight()
        }

    def __repr__(self):
        """Строковое представление объекта для отладки."""
        return (f"Airplane(icao24='{self.icao24}', callsign='{self.callsign}', "
                f"origin_country='{self.origin_country}', altitude={self.altitude} м, "
                f"velocity={self.get_speed_kmh():.1f} км/ч)")

# === БАЗОВЫЙ КЛАСС API И РЕАЛИЗАЦИИ ===
class BaseAPI(ABC):
    """Абстрактный класс для работы с различными API."""

    @abstractmethod
    def get_data(self, **kwargs):
        pass

    @abstractmethod
    def is_valid_response(self, response):
        pass

    @abstractmethod
    def get_data(self, **kwargs):
        """Абстрактный метод для получения данных из API."""
        pass

    @abstractmethod
    def is_valid_response(self, response):
        """Абстрактный метод для проверки валидности ответа от API."""
        pass

class NominatimAPI(BaseAPI):
    """Класс для работы с Nominatim OpenStreetMap API."""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"

    def get_data(self, country_name):
        params = {
            'q': country_name,
            'format': 'json',
            'limit': 1
        }
        try:
            response = requests.get(self.base_url, params=params)
            if self.is_valid_response(response):
                data = response.json()
                if data:
                    return data[0]
                else:
                    raise ValueError(f"Страна '{country_name}' не найдена")
            else:
                raise ConnectionError(f"Ошибка API: {response.status_code}")
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка сети: {e}")

    def is_valid_response(self, response):
        return response.status_code == 200

class OpenSkyAPI(BaseAPI):
    """Класс для работы с OpenSky Network API."""

    def __init__(self):
        self.base_url = "https://opensky-network.org/api/states/all"

    def get_data(self, boundingbox):
        params = {
            'lamin': boundingbox[0],  # юг
            'lamax': boundingbox[1],  # север
            'lomin': boundingbox[2],  # запад
            'lomax': boundingbox[3]   # восток
        }
        try:
            response = requests.get(self.base_url, params=params)
            if self.is_valid_response(response):
                data = response.json()
                return data.get('states', [])
            else:
                raise ConnectionError(f"Ошибка API: {response.status_code}")
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка сети: {e}")

    def is_valid_response(self, response):
        return response.status_code == 200


# === БАЗОВЫЙ КЛАСС ХРАНИЛИЩА И РЕАЛИЗАЦИЯ ДЛЯ JSON ===
class BaseStorageConnector(ABC):
    """
    Абстрактный класс, определяющий контракт для всех коннекторов к хранилищам данных.
    Позволяет легко заменять хранилище (файлы, БД, облачные сервисы и т. д.).
    """

    @abstractmethod
    def add_airplane(self, airplane: Airplane) -> bool:
        """Добавляет информацию о самолёте в хранилище."""
        pass

    @abstractmethod
    def get_airplanes(self) -> List[Airplane]:
        """Возвращает список всех самолётов из хранилища."""
        pass

    @abstractmethod
    def remove_airplane(self, icao24: str) -> bool:
        """Удаляет самолёт по ICAO24 из хранилища."""
        pass

    @abstractmethod
    def update_airplane(self, airplane: Airplane) -> bool:
        """Обновляет информацию о самолёте в хранилище."""
        pass

    @abstractmethod
    def save_all(self):
        """Сохраняет все данные в хранилище."""
        pass

    @abstractmethod
    def load_all(self):
        """Загружает данные из хранилища."""
        pass
