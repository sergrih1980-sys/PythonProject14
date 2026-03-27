from src.api_adapter import APIAdapter
from src.file_saver import JSONSaver
from src.aeroplane import Aeroplane

def filter_aeroplanes(aeroplanes: list, countries: list) -> list:
    """Фильтрация самолётов по странам регистрации."""
    if not countries:
        return aeroplanes
    return [plane for plane in aeroplanes if plane.country in countries]

def get_aeroplanes_by_altitude(aeroplanes: list, altitude_range: str) -> list:
    """Фильтрация самолётов по диапазону высот."""
    try:
        min_alt, max_alt = map(float, altitude_range.split('-'))
        return [plane for plane in aeroplanes if min_alt <= plane.altitude <= max_alt]
    except ValueError:
        print("Некорректный формат диапазона высот. Используется диапазон 0–∞.")
        return aeroplanes

def sort_aeroplanes(aeroplanes: list) -> list:
    """Сортировка самолётов по высоте (по убыванию)."""
    return sorted(aeroplanes, key=lambda x: x.altitude, reverse=True)

def get_top_aeroplanes(aeroplanes: list, top_n: int) -> list:
    """Получение топ‑N самолётов."""
    return aeroplanes[:top_n]

def print_aeroplanes(aeroplanes: list) -> None:
    """Вывод информации о самолётах."""
    for i, plane in enumerate(aeroplanes, 1):
        print(f"{i}. Позывной: {plane.callsign}, Страна: {plane.country}, "
              f"Высота: {plane.altitude:.0f} м, Скорость: {plane.velocity:.1f} м/с")

def user_interaction():
    """Функция для взаимодействия с пользователем."""
    api = APIAdapter()
    json_saver = JSONSaver()

    country = input("Введите название страны: ")
    try:
        top_n = int(input("Введите количество самолётов для вывода в топ N: "))
    except ValueError:
        print("Некорректное число. Используется значение 5.")
        top_n = 5

    filter_countries = input("Введите названия стран для фильтрации по стране регистрации (через пробел): ").split()
    altitude_range = input("Введите диапазон высот полёта (например, 10000-15000): ")

    # Получаем координаты страны
    coordinates = api.get_country_coordinates(country)
    if not coordinates:
        print("Не удалось получить координаты для указанной страны.")
        return

    # Получаем сырые данные о самолётах
    raw_aeroplanes_data = api.get_aeroplanes_by_coordinates(coordinates)

    # Преобразуем в объекты Aeroplane
    aeroplanes = Aeroplane.cast_to_object_list(raw_aeroplanes_data)
    if not aeroplanes:
        print("Самолёты в воздушном пространстве не найдены.")
        return

    # Сохраняем все полученные самолёты в JSON
    for plane in aeroplanes:
        json_saver.add_aeroplane(plane)

    print(f"\nНайдено самолётов: {len(aeroplanes)}")

    # Фильтрация и сортировка
    filtered_aeroplanes = filter_aeroplanes(aeroplanes, filter_countries)
    ranged_aeroplanes = get_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)
    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)
    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)

    # Вывод результата
    print("\nТоп самолётов по высоте:")
    print_aeroplanes(top_aeroplanes)

if __name__ == "__main__":
    user_interaction()