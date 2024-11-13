from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class WeatherViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("weather_view")  # URLを名前付きURLパターンで設定

    def test_default_weather_data(self):
        """デフォルトの緯度・経度でのリクエストが成功することを確認"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("weather_data", response.context)
        self.assertIn("latitude", response.context)
        self.assertIn("longitude", response.context)

    def test_invalid_latitude_error(self):
        """緯度が範囲外の場合にエラーメッセージが表示されることを確認"""
        response = self.client.get(self.url, {"latitude": 100, "longitude": 139.6917})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "エラー: 緯度は-90から90の範囲で指定してください。")

    def test_invalid_longitude_error(self):
        """経度が範囲外の場合にエラーメッセージが表示されることを確認"""
        response = self.client.get(self.url, {"latitude": 35.6895, "longitude": 200})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "エラー: 経度は-180から180の範囲で指定してください。")

    def test_non_numeric_coordinates(self):
        """緯度・経度が数値でない場合にエラーメッセージが表示されることを確認"""
        response = self.client.get(self.url, {"latitude": "abc", "longitude": "xyz"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "エラー: 緯度と経度は数値で指定してください。")

    @patch("weather.views.requests.get")
    def test_api_data_fetch(self, mock_get):
        """Mockを使ってAPIからのデータが正しく処理されることを確認"""
        # Mockの戻り値を設定
        mock_data = {
            "daily": {
                "time": ["2024-11-13", "2024-11-14"],
                "temperature_2m_min": [10.0, 12.0],
                "temperature_2m_max": [20.0, 22.0],
                "precipitation_probability_mean": [30, 40],
                "weathercode": [1, 2],
            }
        }
        mock_get.return_value.json.return_value = mock_data

        response = self.client.get(self.url, {"latitude": 35.6895, "longitude": 139.6917})
        self.assertEqual(response.status_code, 200)
        self.assertIn("weather_data", response.context)
        self.assertEqual(len(response.context["weather_data"]), 2)

        # 各日のデータが正しく設定されているか確認
        self.assertEqual(response.context["weather_data"][0]["date"], "2024/11/13")
        self.assertEqual(response.context["weather_data"][0]["min_temp"], 10.0)
        self.assertEqual(response.context["weather_data"][0]["max_temp"], 20.0)
        self.assertEqual(response.context["weather_data"][0]["precipitation"], 30)
        self.assertEqual(response.context["weather_data"][0]["weather_code"], 1)
