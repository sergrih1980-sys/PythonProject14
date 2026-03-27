from abc import ABC, abstractmethod
from requests import get

class AbstractAPIAdapter(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def get_country_coordinates(self, country: str) -> list:
        pass

    @abstractmethod
    def get_aeroplanes_by_coordinates(self, coordinates: list) -> dict:
        pass

class APIAdapter(AbstractAPIAdapter):
    def __init__(self) -> None:
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all?'

    def get_country_coordinates(self, country: str) -> list:
        headers = {'User-Agent': 'test-app/1.0'}
        params = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }
        response = get(url=self.openstreetmap_url, params=params, headers=headers)
        data = response.json()
        return data[0].get('boundingbox')

    def get_aeroplanes_by_coordinates(self, coordinates: list) -> dict:
        params = {
            'lamin': coordinates[0],
            'lamax': coordinates[1],
            'lomin': coordinates[2],
            'lomax': coordinates[3],
        }
        response = get(url=self.opensky_url, params=params)
        return response.json()