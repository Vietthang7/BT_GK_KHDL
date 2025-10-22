import pandas as pd
import numpy as np
import os

def process_economy_data():
    """Xử lý dữ liệu kinh tế"""
    
    print("\n🔧 Đang xử lý dữ liệu kinh tế...")
    
    df = pd.read_csv('data/raw/economy_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_name'] = df['date'].dt.day_name()
    df['month_name'] = df['date'].dt.month_name()
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    df['unemployment_ma7'] = df['unemployment_rate'].rolling(window=7, min_periods=1).mean()
    df['unemployment_ma30'] = df['unemployment_rate'].rolling(window=30, min_periods=1).mean()
    
    df['gdp_ma7'] = df['gdp_growth'].rolling(window=7, min_periods=1).mean()
    df['gdp_ma30'] = df['gdp_growth'].rolling(window=30, min_periods=1).mean()
    
    df['stock_ma7'] = df['stock_index'].rolling(window=7, min_periods=1).mean()
    df['stock_ma30'] = df['stock_index'].rolling(window=30, min_periods=1).mean()
    
    df['retail_ma7'] = df['retail_sales'].rolling(window=7, min_periods=1).mean()
    df['retail_ma30'] = df['retail_sales'].rolling(window=30, min_periods=1).mean()
    
    df['unemployment_change'] = df['unemployment_rate'].diff()
    df['gdp_change'] = df['gdp_growth'].diff()
    df['stock_change'] = df['stock_index'].pct_change() * 100  # % change
    df['retail_change'] = df['retail_sales'].pct_change() * 100
    
    df['economic_status'] = pd.cut(df['unemployment_rate'], 
                                    bins=[0, 3, 5, 100],
                                    labels=['Tốt', 'Trung bình', 'Xấu'])
    
    df['gdp_status'] = pd.cut(df['gdp_growth'], 
                              bins=[-100, 0, 3, 100],
                              labels=['Suy thoái', 'Chậm', 'Tăng trưởng'])
    
    df['stock_status'] = pd.cut(df['stock_index'],
                                bins=[0, 900, 1200, 2000],
                                labels=['Thấp', 'Trung bình', 'Cao'])
    
    df = df.ffill().bfill()
    
    os.makedirs('data/processed', exist_ok=True)
    
    df.to_csv('data/processed/economy_data_processed.csv', index=False)
    print(f"Đã xử lý {len(df)} bản ghi kinh tế → data/processed/economy_data_processed.csv")
    
    print("\n Thống kê dữ liệu kinh tế:")
    print(df[['unemployment_rate', 'gdp_growth', 'stock_index', 'retail_sales']].describe().round(2))
    
    return df

def process_covid_data():
    """Xử lý dữ liệu COVID-19"""
    
    print("\n🔧 Đang xử lý dữ liệu COVID-19...")
    
    df = pd.read_csv('data/raw/covid_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.dayofweek
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    df['daily_cases'] = df['cases'].diff().fillna(df['cases'])
    df['daily_deaths'] = df['deaths'].diff().fillna(df['deaths'])
    df['daily_recovered'] = df['recovered'].diff().fillna(df['recovered'])
    
    df['cases_ma7'] = df['daily_cases'].rolling(window=7, min_periods=1).mean()
    df['cases_ma14'] = df['daily_cases'].rolling(window=14, min_periods=1).mean()
    
    df['deaths_ma7'] = df['daily_deaths'].rolling(window=7, min_periods=1).mean()
    df['recovered_ma7'] = df['daily_recovered'].rolling(window=7, min_periods=1).mean()
    
    df['mortality_rate'] = (df['deaths'] / df['cases'] * 100).replace([np.inf, -np.inf], 0)
    
    df['recovery_rate'] = (df['recovered'] / df['cases'] * 100).replace([np.inf, -np.inf], 0)
    
    df['active_cases'] = df['cases'] - df['deaths'] - df['recovered']
    
    df['growth_rate'] = df['daily_cases'].pct_change() * 100
    df['growth_rate'] = df['growth_rate'].replace([np.inf, -np.inf], 0).fillna(0)
    
    df['severity'] = pd.cut(df['daily_cases'],
                           bins=[0, 1000, 5000, 100000],
                           labels=['Thấp', 'Trung bình', 'Cao'])
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].ffill().bfill().fillna(0)
    
    categorical_cols = df.select_dtypes(include=['category', 'object']).columns
    for col in categorical_cols:
        if col != 'date':  
            df[col] = df[col].ffill().bfill()
    
    df.to_csv('data/processed/covid_data_processed.csv', index=False)
    print(f" Đã xử lý {len(df)} bản ghi COVID → data/processed/covid_data_processed.csv")
    
    print("\n Thống kê dữ liệu COVID-19:")
    print(df[['cases', 'deaths', 'recovered', 'daily_cases']].describe().round(2))
    
    return df

if __name__ == "__main__":
    print(" Bắt đầu xử lý dữ liệu...\n")
    
    economy_df = process_economy_data()
    
    covid_df = process_covid_data()
    
    print("\n Hoàn thành xử lý dữ liệu!")
    print(f"\n Các file đã tạo:")
    print("   - data/processed/economy_data_processed.csv")
    print("   - data/processed/covid_data_processed.csv")