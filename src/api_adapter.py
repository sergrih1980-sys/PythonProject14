from abc import ABC, abstractmethod
import requests


class BaseAPI(ABC):
    """Абстрактный класс для работы с различными API."""

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
