import requests
import pandas as pd
from datetime import datetime, timedelta

def scrape_weather_data():
    """Thu thập dữ liệu thời tiết từ Open-Meteo Archive API"""
    print("🌤️ Đang thu thập dữ liệu thời tiết...")
    
    # Tính ngày bắt đầu và kết thúc (90 ngày trước đến hôm nay)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # Sử dụng Archive API cho dữ liệu lịch sử
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": 21.0285,  # Hà Nội
        "longitude": 105.8542,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
        "timezone": "Asia/Bangkok"
    }
    
    try:
        print(f"📡 Gửi request tới: {url}")
        print(f"📅 Từ {start_date.date()} đến {end_date.date()}")
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'hourly' not in data:
            print("❌ API không trả về dữ liệu hourly")
            print(f"Response: {data}")
            return None
        
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'temperature': data['hourly']['temperature_2m'],
            'humidity': data['hourly']['relative_humidity_2m'],
            'precipitation': data['hourly']['precipitation'],
            'wind_speed': data['hourly']['wind_speed_10m']
        })
        
        # Loại bỏ các dòng có tất cả giá trị null
        df = df.dropna(how='all', subset=['temperature', 'humidity', 'precipitation', 'wind_speed'])
        
        # Kiểm tra dữ liệu có hợp lệ không
        if len(df) == 0:
            print("❌ Không có dữ liệu sau khi loại bỏ null")
            return None
        
        # Kiểm tra xem có giá trị trùng lặp không
        unique_temps = df['temperature'].nunique()
        if unique_temps < 10:
            print(f"⚠️ Cảnh báo: Chỉ có {unique_temps} giá trị nhiệt độ khác nhau - Dữ liệu có thể bị lỗi")
        
        # In thống kê
        print(f"\n📊 Tổng số bản ghi: {len(df)}")
        print(f"📊 Khoảng thời gian: {df['timestamp'].min()} đến {df['timestamp'].max()}")
        print(f"\n📋 Thống kê nhiệt độ:")
        print(df['temperature'].describe())
        print(f"\n📋 Số giá trị unique:")
        print(f"  - Temperature: {df['temperature'].nunique()}")
        print(f"  - Humidity: {df['humidity'].nunique()}")
        print(f"  - Precipitation: {df['precipitation'].nunique()}")
        print(f"  - Wind Speed: {df['wind_speed'].nunique()}")
        print(f"\n📋 5 dòng đầu tiên:")
        print(df.head(10))
        print(f"\n📋 5 dòng cuối cùng:")
        print(df.tail(10))
        
        df.to_csv('data/raw/weather_data.csv', index=False)
        print(f"\n✅ Đã lưu vào data/raw/weather_data.csv")
        
        return df
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_covid_data():
    """Thu thập dữ liệu COVID-19 từ disease.sh API"""
    print("\n🦠 Đang thu thập dữ liệu COVID-19...")
    url = "https://disease.sh/v3/covid-19/historical/all?lastdays=180"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(list(data['cases'].keys()), format='%m/%d/%y'),
            'cases': list(data['cases'].values()),
            'deaths': list(data['deaths'].values()),
            'recovered': list(data['recovered'].values())
        })
        
        df.to_csv('data/raw/covid_data.csv', index=False)
        print(f"✅ Thu thập thành công {len(df)} bản ghi COVID-19")
        print(f"\n📋 5 dòng đầu tiên:")
        print(df.head())
        
        return df
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import os
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    weather_df = scrape_weather_data()
    covid_df = scrape_covid_data()
    
    if weather_df is not None and covid_df is not None:
        print("\n✅ Hoàn tất thu thập dữ liệu!")
    else:
        print("\n⚠️ Có lỗi xảy ra trong quá trình thu thập")