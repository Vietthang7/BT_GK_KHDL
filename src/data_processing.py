import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_and_clean_data(filepath):
    """Load and clean data"""
    df = pd.read_csv(filepath)
    
    # Data type conversion (SỬA: 'data' → 'date')
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    if 'date' in df.columns:  # ← SỬA LỖI TYPO
        df['date'] = pd.to_datetime(df['date'])
    
    # Handle missing values - CHỈ ĐIỀN NẾU < 5% NULL
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        
        if null_count > 0:
            if null_pct < 5:
                # Nếu < 5% missing, điền bằng interpolation
                df[col] = df[col].interpolate(method='linear', limit_direction='both')
                print(f"  ✓ Điền {null_count} giá trị thiếu cho cột '{col}' ({null_pct:.1f}%)")
            else:
                # Nếu > 5% missing, cảnh báo
                print(f"  ⚠️ Cột '{col}' có {null_pct:.1f}% giá trị thiếu - Giữ nguyên hoặc xóa cột")
    
    # Loại bỏ các dòng vẫn còn null sau interpolate
    before_drop = len(df)
    df = df.dropna()
    after_drop = len(df)
    
    if before_drop > after_drop:
        print(f"  ✓ Đã loại bỏ {before_drop - after_drop} dòng còn null")
    
    print(f"✓ Dữ liệu sau khi làm sạch: {df.shape}")
    return df

def create_features(df):
    """Tạo các đặc trưng mới"""
    # Xử lý cho data weather
    if 'timestamp' in df.columns:
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['date'] = df['timestamp'].dt.date
        
        # Phân loại nhiệt độ
        if 'temperature' in df.columns:
            df['temp_category'] = pd.cut(df['temperature'], 
                                        bins=[-np.inf, 10, 20, 30, np.inf],
                                        labels=['Lạnh', 'Mát', 'Ấm', 'Nóng'])
    
    # Xử lý cho data COVID
    if 'date' in df.columns and 'cases' in df.columns:
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['cases_change'] = df['cases'].pct_change() * 100
        df['deaths_change'] = df['deaths'].pct_change() * 100
        df['cases_ma7'] = df['cases'].rolling(window=7).mean()
        df['deaths_ma7'] = df['deaths'].rolling(window=7).mean()
    
    print(f"✓ Đã tạo {len(df.columns)} đặc trưng")
    return df

def process_all_data():
    """Xử lý tất cả dữ liệu"""
    import os
    os.makedirs('data/processed', exist_ok=True)
    
    # Xử lý dữ liệu thời tiết
    print("\n🌤️ Xử lý dữ liệu thời tiết...")
    weather_df = load_and_clean_data('data/raw/weather_data.csv')
    weather_df = create_features(weather_df)
    weather_df.to_csv('data/processed/weather_data_processed.csv', index=False)
    print(f"✅ Đã lưu weather_data_processed.csv với {len(weather_df)} bản ghi")
    
    # Xử lý dữ liệu COVID-19
    print("\n🦠 Xử lý dữ liệu COVID-19...")
    covid_df = load_and_clean_data('data/raw/covid_data.csv')
    covid_df = create_features(covid_df)
    covid_df.to_csv('data/processed/covid_data_processed.csv', index=False)
    print(f"✅ Đã lưu covid_data_processed.csv với {len(covid_df)} bản ghi")
    
    print("\n✅ Đã xử lý xong tất cả dữ liệu")
    return weather_df, covid_df

if __name__ == "__main__":
    process_all_data()