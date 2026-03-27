from abc import ABC, abstractmethod
import requests

class AbstractAPIAdapter(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def get_country_coordinates(self, country: str) -> list:
        """Получить координаты (bounding box) для указанной страны.

        Args:
            country (str): Название страны.

        Returns:
            list: Список из 4 чисел [lat_min, lat_max, lon_min, lon_max] или пустой список при ошибке.
        """
        pass

    @abstractmethod
    def get_aeroplanes_by_coordinates(self, coordinates: list) -> dict:
        """Получить данные о самолётах в указанном географическом прямоугольнике.

        Args:
            coordinates (list): Список из 4 координат [lat_min, lat_max, lon_min, lon_max].

        Returns:
            dict: Сырые данные от API (обычно JSON).
        """
        pass

class APIAdapter(AbstractAPIAdapter):
    def __init__(self) -> None:
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all'

    def get_country_coordinates(self, country: str) -> list:
        headers = {'User-Agent': 'test-app/1.0'}
        params = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }
        try:
            response = requests.get(url=self.openstreetmap_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data and 'boundingbox' in data[0]:
                bbox = data[0]['boundingbox']
                return [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])]
            else:
                print(f"Координаты для страны '{country}' не найдены.")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к OpenStreetMap: {e}")
            return []
        except (IndexError, KeyError, ValueError) as e:
            print(f"Ошибка обработки данных OpenStreetMap: {e}")
            return []

    def get_aeroplanes_by_coordinates(self, coordinates: list) -> dict:
        if not coordinates:
            print("Координаты не предоставлены.")
            return {}
        params = {
            'lamin': coordinates[0],
            'lamax': coordinates[1],
            'lomin': coordinates[2],
            'lomax': coordinates[3],
        }
        try:
            response = requests.get(url=self.opensky_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к OpenSky Network: {e}")
            return {}
        except ValueError as e:
            print(f"Ошибка парсинга JSON от OpenSky: {e}")
            return {}