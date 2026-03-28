import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.aeroplane import Airplane

class BaseStorageConnector(ABC):
    """
    Абстрактный класс, определяющий контракт для всех коннекторов к хранилищам данных.
    Позволяет легко заменять хранилище (файлы, БД, облачные сервисы и т. д.).
    """

    @abstractmethod
    def add_airplane(self, airplane: Airplane) -> bool:
        """
        Добавляет информацию о самолёте в хранилище.

        Args:
            airplane (Airplane): объект самолёта для сохранения

        Returns:
            bool: True при успешном добавлении, False при ошибке
        """
        pass

    @abstractmethod
    def get_airplanes(self, **criteria) -> List[Airplane]:
        """
        Получает список самолётов по заданным критериям фильтрации.

        Args:
            **criteria: критерии фильтрации (например, country='Russia', min_speed=500)
        Returns:
            List[Airplane]: список подходящих самолётов
        """
        pass

    @abstractmethod
    def remove_airplane(self, icao24: str) -> bool:
        """
        Удаляет самолёт из хранилища по его уникальному идентификатору ICAO24.

        Args:
            icao24 (str): уникальный идентификатор самолёта
        Returns:
            bool: True при успешном удалении, False если самолёт не найден или ошибка
        """
        pass

    @abstractmethod
    def save_all(self) -> bool:
        """
        Сохраняет все данные в хранилище.
        Может быть полезно для файловых хранилищ или кэширования.
        Returns:
            bool: статус операции сохранения
        """
        pass

    @abstractmethod
    def load_all(self) -> bool:
        """
        Загружает все данные из хранилища.
        Используется при инициализации или синхронизации.
        Returns:
            bool: статус операции загрузки
        """
        pass

    @abstractmethod
    def update_airplane(self, icao24: str, **updates) -> bool:
        """
        Обновляет информацию о самолёте (заглушка для будущей интеграции с БД).

        Args:
            icao24 (str): идентификатор самолёта для обновления
            **updates: поля и их новые значения
        Returns:
            bool: статус операции обновления
        """
        pass


class JSONFileConnector(BaseStorageConnector):
    """Конкретная реализация коннектора для работы с JSON‑файлами."""

    def __init__(self, filename: str = "airplanes.json"):
        self.filename = filename
        self._data: List[Dict[str, Any]] = []
        self.load_all()

    def _find_airplane_index(self, icao24: str) -> Optional[int]:
        for i, plane_data in enumerate(self._data):
            if plane_data.get('icao24') == icao24:
                return i
        return None

    def add_airplane(self, airplane: Airplane) -> bool:
        try:
            if self._find_airplane_index(airplane.icao24) is not None:
                print(f"Самолёт с ICAO24 {airplane.icao24} уже существует")
                return False
            self._data.append(airplane.to_dict())
            return True
        except Exception as e:
            print(f"Ошибка при добавлении самолёта: {e}")
            return False

    def get_airplanes(self, **criteria) -> List[Airplane]:
        """Получает самолёты по критериям фильтрации."""
        result = []

        for plane_data in self._data:
            match = True

            # Применяем все критерии фильтрации
            for key, value in criteria.items():
                if key == 'min_speed' and plane_data.get('speed_kmh', 0) < value:
                    match = False
                elif key == 'max_speed' and plane_data.get('speed_kmh', float('inf')) > value:
                    match = False
                elif key == 'country' and plane_data.get('origin_country', '') != value:
                    match = False
                elif key == 'in_flight' and plane_data.get('is_in_flight', False) != value:
                    match = False
                elif key == 'min_altitude' and plane_data.get('altitude', 0) < value:
                    match = False
                elif key == 'max_altitude' and plane_data.get('altitude', float('inf')) > value:
                    match = False

            if match:
                # Создаём объект Airplane из данных
                try:
                    airplane = Airplane(
                        icao24=plane_data['icao24'],
                        callsign=plane_data.get('callsign', 'N/A'),
                        origin_country=plane_data.get('origin_country', 'Unknown'),
                        velocity=plane_data.get('velocity', 0.0),
                        altitude=plane_data.get('altitude', 0.0),
                        latitude=plane_data.get('latitude', 0.0),
                        longitude=plane_data.get('longitude', 0.0)
                    )
                    result.append(airplane)
                except Exception as e:
                    print(f"Ошибка создания объекта Airplane из данных {plane_data}: {e}")
                    continue

        return result


    def remove_airplane(self, icao24: str) -> bool:
        index = self._find_airplane_index(icao24)
        if index is not None:
            removed_plane = self._data.pop(index)
            print(f"Удален самолёт: {removed_plane['callsign']} (ICAO24: {icao24})")
            return True
        else:
            print(f"Самолёт с ICAO24 {icao24} не найден")
            return False

    def save_all(self) -> bool:
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            print(f"Данные сохранены в {self.filename}")
            return True
        except Exception as e:
            print(f"Ошибка сохранения в файл: {e}")
            return False

    def load_all(self) -> bool:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
            print(f"Данные загружены из {self.filename}")
            return True
        except FileNotFoundError:
            self._data = []
            print(f"Файл {self.filename} не найден, создан новый")
            return True
        except Exception as e:
            print(f"Ошибка загрузки из файла: {e}")
            self._data = []
            return False

    def update_airplane(self, icao24: str, **updates) -> bool:
        print("Метод update_airplane пока не реализован для JSON‑хранилища")
        index = self._find_airplane_index(icao24)
        if index is not None:
            for field, value in updates.items():
                self._data[index][field] = value
            return self.save_all()
        return False

