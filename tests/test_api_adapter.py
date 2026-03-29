import unittest
from unittest.mock import patch, Mock
from src.api_adapter import NominatimAPI, OpenSkyAPI


class TestNominatimAPI(unittest.TestCase):
    def setUp(self):
        self.nominatim = NominatimAPI()

    @patch('requests.get')
    def test_get_data_success(self, mock_get):
        """Тест успешного получения данных из Nominatim API."""
        # Настраиваем mock для успешного ответа
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'lat': '56.326944',
            'lon': '44.005278',
            'display_name': 'Russia'
        }]
        mock_get.return_value = mock_response

        # Вызываем метод
        result = self.nominatim.get_data('Russia')

        # Проверяем результат
        self.assertEqual(result['lat'], '56.326944')
        self.assertEqual(result['lon'], '44.005278')
        self.assertEqual(result['display_name'], 'Russia')

        # Проверяем, что запрос был сделан с правильными параметрами
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        self.assertIn('params', call_args)
        self.assertEqual(call_args['params']['q'], 'Russia')
        self.assertEqual(call_args['params']['format'], 'json')
        self.assertEqual(call_args['params']['limit'], 1)

    @patch('requests.get')
    def test_get_data_country_not_found(self, mock_get):
        """Тест когда страна не найдена в Nominatim."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.nominatim.get_data('NonExistentCountry')
        self.assertIn("Страна 'NonExistentCountry' "
                      "не найдена", str(context.exception))


class TestOpenSkyAPI(unittest.TestCase):
    def setUp(self):
        self.opensky = OpenSkyAPI()

    @patch('requests.get')
    def test_get_data_success(self, mock_get):
        """Тест успешного получения данных из OpenSky API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'states': [
                ['icao1', 'callsign1', 'country1', 100.0, 5000.0, 55.0, 37.0],
                ['icao2', 'callsign2', 'country2', 150.0, 8000.0, 56.0, 38.0]
            ]
        }
        mock_get.return_value = mock_response

        bounding_box = [50.0, 60.0, 30.0, 40.0]
        result = self.opensky.get_data(bounding_box)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 'icao1')
        self.assertEqual(result[1][1], 'callsign2')

        # Проверяем параметры запроса
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        params = call_args['params']
        self.assertEqual(params['lamin'], 50.0)
        self.assertEqual(params['lamax'], 60.0)
        self.assertEqual(params['lomin'], 30.0)
        self.assertEqual(params['lomax'], 40.0)

    @patch('requests.get')
    def test_get_data_empty_states(self, mock_get):
        """Тест когда в ответе OpenSky нет данных о самолётах."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'states': []}
        mock_get.return_value = mock_response

        result = self.opensky.get_data([0, 1, 0, 1])
        self.assertEqual(result, [])
