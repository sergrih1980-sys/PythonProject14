class Aeroplane:
    """Класс для работы с информацией о самолётах"""

    def __init__(self, callsign: str, country: str, velocity: float, altitude: float):
        self._callsign = self._validate_callsign(callsign)
        self._country = self._validate_country(country)
        self._velocity = self._validate_velocity(velocity)
        self._altitude = self._validate_altitude(altitude)

    @staticmethod
    def _validate_callsign(callsign: str) -> str:
        if not callsign or not callsign.strip():
            raise ValueError("Позывной не может быть пустым")
        return callsign.strip()

    @staticmethod
    def _validate_country(country: str) -> str:
        if not country or not country.strip():
            raise ValueError("Страна регистрации не может быть пустой")
        return country.strip()

    @staticmethod
    def _validate_velocity(velocity: float) -> float:
        if velocity < 0:
            raise ValueError("Скорость не может быть отрицательной")
        return velocity

    @staticmethod
    def _validate_altitude(altitude: float) -> float:
        if altitude < 0:
            raise ValueError("Высота не может быть отрицательной")
        return altitude

    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def country(self) -> str:
        return self._country

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def altitude(self) -> float:
        return self._altitude

    def __lt__(self, other) -> bool:
        return self.altitude < other.altitude

    def __le__(self, other) -> bool:
        return self.altitude <= other.altitude

    def __eq__(self, other) -> bool:
        return self.altitude == other.altitude

    def __gt__(self, other) -> bool:
        return self.velocity > other.velocity

    def __ge__(self, other) -> bool:
        return self.velocity >= other.velocity


    @classmethod
    def cast_to_object_list(cls, data: dict) -> list:
        aeroplanes = []
        for plane_data in data.get('states', []):
            try:
                callsign = plane_data[1] or "N/A"
                country = plane_data[2] or "Unknown"
                velocity = float(plane_data[9]) if plane_data[9] else 0.0
                altitude = float(plane_data[7]) if plane_data[7] else 0.0
                aeroplanes.append(cls(callsign, country, velocity, altitude))
            except (ValueError, IndexError, TypeError):
                continue
        return aeroplanes