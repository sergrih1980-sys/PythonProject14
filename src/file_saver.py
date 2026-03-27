import json
from abc import ABC, abstractmethod
from aeroplane import Aeroplane

class AbstractFileSaver(ABC):
    """Абстрактный класс для работы с файлами"""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        pass

    @abstractmethod
    def get_aeroplanes(self, **filters) -> list:
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        pass

class JSONSaver(AbstractFileSaver):
    def __init__(self, filename: str = 'aeroplanes.json'):
        self.filename = filename
        self._create_file_if_not_exists()

    def _create_file_if_not_exists(self) -> None:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        plane_data = {
            'callsign': aeroplane.callsign,
            'country': aeroplane.country,
            'velocity': aeroplane.velocity,
            'altitude': aeroplane.altitude
        }
        data.append(plane_data)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_aeroplanes(self, **filters) -> list:
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        filtered = data
        if 'country' in filters:
            filtered = [p for p in filtered if p['country'] == filters['country']]
        if 'min_altitude' in filters:
            filtered = [p for p in filtered if p['altitude'] >= filters['min_altitude']]
        return filtered

    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        original_len = len(data)
        data = [p for p in data if not (
            p['callsign'] == aeroplane.callsign and
            p['country'] == aeroplane.country
        )]
        if len(data) < original_len:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        return False