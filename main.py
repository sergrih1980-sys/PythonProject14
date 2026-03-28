from src.aeroplane import Airplane
from src.api_adapter import NominatimAPI, OpenSkyAPI
from typing import List,  Optional
from src.file_saver import  BaseStorageConnector
import json

def user_interaction():
    """Функция для взаимодействия с пользователем.
    Реализует понятный интерфейс без вывода сырых коллекций — только человекочитаемые строки.
    Использует ранее созданные классы и их методы без дублирования функциональности.
    """
    print("=== Система отслеживания самолётов ===")

    # Создаём экземпляры API и хранилища
    nominatim_api = NominatimAPI()
    opensky_api = OpenSkyAPI()
    storage = JSONFileConnector()

    try:
        # Запрос данных у пользователя
        country = input("\nВведите название страны для поиска самолётов: ").strip()
        if not country:
            print("Ошибка: название страны не может быть пустым.")
            return

        top_n = input("Введите количество самолётов для вывода в топ (по высоте): ")
        try:
            top_n = int(top_n)
            if top_n <= 0:
                print("Количество должно быть положительным числом.")
                return
        except ValueError:
            print("Ошибка: введите корректное число для количества самолётов.")
            return

        # Получаем координаты страны через Nominatim API
        print(f"Поиск координат для страны '{country}'...")
        country_data = nominatim_api.get_data(country)
        lat = float(country_data['lat'])
        lng = float(country_data['lon'])

        # Формируем bounding box (упрощённо: ±2 градуса от центра)
        boundingbox = [lat - 2, lat + 2, lng - 2, lng + 2]
        print(f"Координаты найдены: широта {lat:.2f}, долгота {lng:.2f}")

        # Получаем данные о самолётах из OpenSky API
        print("Получение данных о самолётах...")
        airplanes_data = opensky_api.get_data(boundingbox)

        if not airplanes_data:
            print("В указанном регионе самолёты не найдены.")
            return

        aeroplanes = []
        for plane_data in airplanes_data:
            # Проверяем, что данных достаточно (минимум 10 элементов)
            if len(plane_data) < 10:
                continue

            try:
                airplane = Airplane(
                    icao24=plane_data[0] or "N/A",
            callsign=plane_data[1] or "N/A",
            origin_country=country,
            velocity=plane_data[9],  # скорость в м/с
            altitude=plane_data[7] or 0.0,  # высота в метрах
            latitude=plane_data[6] or 0.0,
            longitude=plane_data[5] or 0.0
        )
                aeroplanes.append(airplane)
                storage.add_airplane(airplane)
            except (ValueError, TypeError) as e:
                # Пропускаем некорректные записи, выводим предупреждение
                print(f"Предупреждение: пропущена запись из‑за ошибки валидации: {e}")
                continue

        # Сохраняем все данные в JSON
        storage.save_all()
        print(f"\nПолучено и сохранено {len(aeroplanes)} самолётов.")

        # Сортируем самолёты по высоте (основное сравнение) и скорости
        sorted_aeroplanes = sorted(aeroplanes, reverse=True)

        # Берём топ‑N самолётов
        top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)

        # Выводим результат в человекочитаемом формате
        print(f"\n=== Топ-{top_n} самолётов по высоте полёта ===")
        print_aeroplanes(top_aeroplanes)

    except ConnectionError as e:
        print(f"Ошибка подключения: {e}")
    except ValueError as e:
        print(f"Ошибка данных: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")



def get_top_aeroplanes(sorted_aeroplanes: List[Airplane], top_n: int) -> List[Airplane]:
    """Возвращает топ‑N самолётов из отсортированного списка."""
    return sorted_aeroplanes[:top_n]


def print_aeroplanes(aeroplanes: List[Airplane]):
    """Выводит информацию о самолётах в человекочитаемом формате."""
    if not aeroplanes:
        print("Самолётов для отображения нет.")
        return

    for i, ap in enumerate(aeroplanes, 1):
        status = "в полёте" if ap.is_in_flight() else "на земле"
        print(f"{i}. {ap.callsign} (ICAO24: {ap.icao24})")
        print(f"   Страна: {ap.origin_country}")
        print(f"   Высота: {ap.altitude:.0f} м")
        print(f"   Скорость: {ap.get_speed_kmh():.1f} км/ч")
        print(f"   Координаты: {ap.latitude:.4f}° с. ш., {ap.longitude:.4f}° в. д.")
        print(f"   Статус: {status}")
        print("-" * 40)

# Класс для JSON‑хранилища (дополняет ваш код)
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

if __name__ == "__main__":
    user_interaction()