import json
from abc import ABC, abstractmethod
from typing import List,  Optional
from src.aeroplane import Airplane

class BaseStorageConnector(ABC):
    """Абстрактный класс, определяющий контракт для всех коннекторов к хранилищам данных."""

    @abstractmethod
    def add_airplane(self, airplane: Airplane) -> bool:
        pass

    @abstractmethod
    def get_airplanes(self, **criteria) -> List[Airplane]:
        pass

    @abstractmethod
    def remove_airplane(self, icao24: str) -> bool:
        pass

    @abstractmethod
    def save_all(self) -> bool:
        pass

    @abstractmethod
    def load_all(self) -> bool:
        pass

    @abstractmethod
    def update_airplane(self, icao24: str, **updates) -> bool:
        pass

class JSONFileConnector(BaseStorageConnector):
    """Конкретная реализация коннектора для работы с JSON‑файлами."""

    def __init__(self, filename: str = "airplanes.json"):
        self.filename = filename
        self._airplanes: List[Airplane] = []
        self.load_all()

    def _find_airplane_index(self, icao24: str) -> Optional[int]:
        """Вспомогательный метод: находит индекс самолёта по ICAO24."""
        for i, plane in enumerate(self._airplanes):
            if plane.icao24 == icao24:
                return i
        return None

    def add_airplane(self, airplane: Airplane) -> bool:
        """Добавляет самолёт в хранилище, если его ещё нет."""
        if self._find_airplane_index(airplane.icao24) is not None:
            print(f"Самолёт с ICAO24 {airplane.icao24} уже существует")
            return False
        try:
            self._airplanes.append(airplane)
            return True
        except Exception as e:
            print(f"Ошибка при добавлении самолёта: {e}")
            return False

    def get_airplanes(self, **criteria) -> List[Airplane]:
        """Получает самолёты по критериям фильтрации."""
        result = []
        for plane in self._airplanes:
            match = True

            # Применяем критерии фильтрации
            for key, value in criteria.items():
                if key == 'country' and plane.origin_country != value:
                    match = False
                elif key == 'min_speed' and plane.get_speed_kmh() < value:
                    match = False
                elif key == 'max_speed' and plane.get_speed_kmh() > value:
                    match = False
                elif key == 'in_flight' and plane.is_in_flight() != value:
                    match = False
                elif key == 'min_altitude' and plane.altitude < value:
                    match = False
                elif key == 'max_altitude' and plane.altitude > value:
                    match = False

            if match:
                result.append(plane)
        return result

    def remove_airplane(self, icao24: str) -> bool:
        """Удаляет самолёт по ICAO24."""
        index = self._find_airplane_index(icao24)
        if index is not None:
            removed_plane = self._airplanes.pop(index)
            print(f"Удален самолёт: {removed_plane.callsign} (ICAO24: {icao24})")
            return True
        else:
            print(f"Самолёт с ICAO24 {icao24} не найден")
            return False

    def update_airplane(self, icao24: str, **updates) -> bool:
        """Обновляет поля самолёта по ICAO24."""
        index = self._find_airplane_index(icao24)
        if index is None:
            print(f"Самолёт с ICAO24 {icao24} не найден для обновления")
            return False

        plane = self._airplanes[index]
        try:
            for field, value in updates.items():
                if hasattr(plane, field):
                    setattr(plane, field, value)
                else:
                    print(f"Поле {field} не существует в классе Airplane")
                    return False
            return self.save_all()
        except Exception as e:
            print(f"Ошибка обновления самолёта: {e}")
            return False

    def save_all(self) -> bool:
        """Сохраняет все данные в JSON‑файл."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([ap.to_dict() for ap in self._airplanes], f, ensure_ascii=False, indent=2)
            print(f"Данные сохранены в {self.filename}")
            return True
        except Exception as e:
            print(f"Ошибка сохранения в файл: {e}")
            return False

    def load_all(self) -> bool:
        """Загружает данные из JSON‑файла."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._airplanes = [Airplane(**item) for item in data]
            print(f"Данные загружены из {self.filename}")
            return True
        except FileNotFoundError:
            self._airplanes = []
            print(f"Файл {self.filename} не найден, создан новый")
            return True
        except Exception as e:
            print(f"Ошибка загрузки из файла: {e}")
            self._airplanes = []
            return False