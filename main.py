from src.Abstract_File_Saver import APIAdapter
from src.file_saver import JSONSaver
from src.aeroplane import Aeroplane

def user_interaction():
    """Функция для взаимодействия с пользователем"""
    api = APIAdapter()
    json_saver = JSONSaver()

    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолётов для вывода в топ N: "))
    filter_countries = input("Введите названия стран для фильтрации по стране регистрации (через пробел): ").split()
    altitude_range_input = input("Введите диапазон высот полёта (например, 10000-15000): ")

    try:
        min_alt, max_alt = map(float, altitude_range_input.split('-'))
    except ValueError:
        print("Некорректный формат диапазона высот. Используется диапазон 0-∞.")
        min_alt, max_alt = 0, float('inf')

    try:
        # Получаем координаты страны
        coordinates = api.get_country_coordinates(country)
        print(f"Координаты страны '{country}': {coordinates}")

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

        # Топ N самолётов по высоте
        sorted_by_altitude = sorted(aeroplanes, key=lambda x: x.altitude, reverse=True)
        print(f"\nТоп {top_n} самолётов по высоте:")
        for i, plane in enumerate(sorted_by_altitude[:top_n], 1):
            print(f"{i}. Позывной: {plane.callsign}, Страна: {plane.country}, "
                  f"Высота: {plane.altitude:.0f} м, Скорость: {plane.velocity:.1f} м/с")

        # Фильтрация по странам регистрации
        if filter_countries:
            filtered_by_country = [plane for plane in aeroplanes if plane.country in filter_countries]
            print(f"\nСамолёты, зарегистрированные в указанных странах ({', '.join(filter_countries)}):")
            if filtered_by_country:
                for plane in filtered_by_country:
                    print(f"- Позывной: {plane.callsign}, Высота: {plane.altitude:.0f} м, "
                  f"Скорость: {plane.velocity:.1f} м/с")
            else:
                print("Самолётов из указанных стран не найдено.")

        # Фильтрация по диапазону высот
        filtered_by_altitude = [
            plane for plane in aeroplanes
            if min_alt <= plane.altitude <= max_alt
        ]
        print(f"\nСамолёты в диапазоне высот {min_alt}–{max_alt} м:")
        if filtered_by_altitude:
            for plane in filtered_by_altitude:
                print(f"- Позывной: {plane.callsign}, Страна: {plane.country}, "
                      f"Высота: {plane.altitude:.0f} м")
        else:
            print("Самолётов в указанном диапазоне высот не найдено.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    user_interaction()