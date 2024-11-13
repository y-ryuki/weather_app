import requests
from django.shortcuts import render
from django.views import View
# from .models import Weather
from datetime import datetime




class WeatherView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.default_latitude = 35.6895  # デフォルトの緯度（東京）
        self.default_longitude = 139.6917  # デフォルトの経度（東京）
        self.params = {
            "daily": ["temperature_2m_min", "temperature_2m_max", "precipitation_probability_mean", "weathercode"],
            "timezone": "Asia/Tokyo"
        }

    def get(self,request):

        latitude = request.GET.get("latitude", self.default_latitude)
        longitude = request.GET.get("longitude", self.default_longitude)
        
        # 緯度と経度の範囲チェック
        error = self.check_place(latitude, longitude)
        if error:
            return render(request, 'weather/index.html', {"error": error})
        
        self.params.update({
            "latitude": latitude,
            "longitude": longitude
        })

        response = requests.get(self.url,params=self.params)
        data = response.json()

        if "daily" not in data:
            error = "エラー: 天気データを取得できませんでした。もう一度お試しください。"
            return render(request, 'weather/index.html', {"error": error})

        weather_data = []
        dates = data["daily"]["time"]#１週間の日付
        min_temps = data["daily"]["temperature_2m_min"]#７日分の最低気温
        max_temps = data["daily"]["temperature_2m_max"]
        precipitation_probs = data["daily"]["precipitation_probability_mean"]
        weather_codes = data["daily"]["weathercode"]

        #1日ごとに日付、最低気温、最高気温、降水確率、天気コードを取得
        for i in range(len(dates)):
            day_data = {
                "date": datetime.strptime(dates[i], "%Y-%m-%d").strftime("%Y/%m/%d"),
                "min_temp": min_temps[i],
                "max_temp": max_temps[i],
                "precipitation": precipitation_probs[i],
                "weather_code": weather_codes[i],
            }
            weather_data.append(day_data)

        context = {
            "weather_data": weather_data,
            "latitude": latitude,
            "longitude": longitude,
        }
        return render(request,'weather/index.html',context)
    

    def check_place(self, latitude, longitude):
        """緯度と経度の範囲をチェックし、範囲外の場合はエラーメッセージを返す"""
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            if not (-90 <= latitude <= 90):
                return "エラー: 緯度は-90から90の範囲で指定してください。"
            if not (-180 <= longitude <= 180):
                return "エラー: 経度は-180から180の範囲で指定してください。"
        except ValueError:
            return "エラー: 緯度と経度は数値で指定してください。"
        return None  # エラーがない場合は None を返す



weather = WeatherView.as_view()



