import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os

def collect_economy_data():
    """Thu thập dữ liệu kinh tế giả lập"""
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    np.random.seed(42)
    
    # Giả lập dữ liệu kinh tế với xu hướng thực tế
    base_unemployment = 2.5
    unemployment_rates = []
    gdp_growths = []
    stock_indices = []
    retail_sales = []
    
    for i, date in enumerate(dates):
        # Tỷ lệ thất nghiệp tăng trong đại dịch
        if date.year == 2020:
            # Tăng mạnh trong 2020
            unemployment = base_unemployment + (i/100) * 2.5 + np.random.normal(0, 0.3)
        elif date.year == 2021:
            # Giảm dần trong 2021
            unemployment = base_unemployment + 2.5 - (i/300) + np.random.normal(0, 0.3)
        else:
            # Ổn định 2022-2023
            unemployment = base_unemployment + 0.5 + np.random.normal(0, 0.2)
        
        unemployment_rates.append(max(1.5, min(8, unemployment)))
        
        # GDP giảm mạnh 2020, hồi phục 2021-2023
        if date.year == 2020:
            if date.month <= 6:
                gdp = -3 + np.random.normal(0, 1)
            else:
                gdp = -1 + np.random.normal(0, 1)
        elif date.year == 2021:
            gdp = 3 + np.random.normal(0, 1.5)
        else:
            gdp = 6.5 + np.random.normal(0, 1)
        
        gdp_growths.append(gdp)
        
        # Stock index (VN-Index giả lập: 800-1500)
        stock_base = 1000
        if date.year == 2020:
            # Giảm mạnh Q1-Q2/2020
            if date.month <= 6:
                stock = stock_base - 200 + np.random.normal(0, 30)
            else:
                stock = stock_base - 100 + np.random.normal(0, 30)
        elif date.year == 2021:
            # Tăng trưởng mạnh 2021
            stock = stock_base + (i/5) + np.random.normal(0, 40)
        else:
            # Ổn định cao 2022-2023
            stock = 1300 + np.random.normal(0, 50)
        
        stock_indices.append(max(700, min(1600, stock)))
        
        # Retail sales (tỷ VND/tháng)
        retail_base = 50000
        if date.year == 2020:
            # Giảm 30-40% trong 2020
            retail = retail_base * 0.65 + np.random.normal(0, 3000)
        elif date.year == 2021:
            # Hồi phục 80% trong 2021
            retail = retail_base * 0.85 + np.random.normal(0, 4000)
        else:
            # Vượt mức trước dịch 2022-2023
            retail = retail_base * 1.1 + np.random.normal(0, 5000)
        
        retail_sales.append(max(25000, retail))
    
    # Tạo DataFrame
    economy_df = pd.DataFrame({
        'date': dates,
        'unemployment_rate': unemployment_rates,
        'gdp_growth': gdp_growths,
        'stock_index': stock_indices,
        'retail_sales': retail_sales
    })
    
    return economy_df

def collect_covid_data():
    """Thu thập dữ liệu COVID-19 giả lập"""
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    np.random.seed(42)
    
    cases_list = []
    deaths_list = []
    recovered_list = []
    
    cumulative_cases = 0
    cumulative_deaths = 0
    cumulative_recovered = 0
    
    for i, date in enumerate(dates):
        # Mô phỏng các đợt dịch
        if date.year == 2020:
            # Đợt đầu: ít ca
            daily_cases = np.random.poisson(50)
        elif date.year == 2021:
            # Đợt 2-3-4: tăng mạnh
            if date.month <= 4:
                daily_cases = np.random.poisson(200)
            elif date.month <= 9:
                daily_cases = np.random.poisson(8000)  # Đợt Delta
            else:
                daily_cases = np.random.poisson(4000)
        elif date.year == 2022:
            # Omicron: nhiều ca nhưng giảm dần
            if date.month <= 3:
                daily_cases = np.random.poisson(15000)
            else:
                daily_cases = np.random.poisson(2000)
        else:
            # 2023: ổn định
            daily_cases = np.random.poisson(500)
        
        cumulative_cases += daily_cases
        
        # Tử vong: 1-2% số ca
        daily_deaths = int(daily_cases * np.random.uniform(0.01, 0.02))
        cumulative_deaths += daily_deaths
        
        # Hồi phục: 90-95% số ca (sau 14 ngày)
        if i > 14:
            daily_recovered = int(cases_list[i-14] * np.random.uniform(0.90, 0.95))
            cumulative_recovered += daily_recovered
        
        cases_list.append(cumulative_cases)
        deaths_list.append(cumulative_deaths)
        recovered_list.append(cumulative_recovered)
    
    covid_df = pd.DataFrame({
        'date': dates,
        'cases': cases_list,
        'deaths': deaths_list,
        'recovered': recovered_list
    })
    
    return covid_df

if __name__ == "__main__":
    print("🔄 Đang thu thập dữ liệu...")
    
    # Tạo thư mục nếu chưa có
    os.makedirs('data/raw', exist_ok=True)
    
    # Thu thập dữ liệu kinh tế
    print("\n📊 Thu thập dữ liệu kinh tế...")
    economy_df = collect_economy_data()
    economy_df.to_csv('data/raw/economy_data.csv', index=False)
    print(f"✅ Đã lưu {len(economy_df)} bản ghi kinh tế vào data/raw/economy_data.csv")
    
    # Thu thập dữ liệu COVID
    print("\n🦠 Thu thập dữ liệu COVID-19...")
    covid_df = collect_covid_data()
    covid_df.to_csv('data/raw/covid_data.csv', index=False)
    print(f"✅ Đã lưu {len(covid_df)} bản ghi COVID vào data/raw/covid_data.csv")
    
    print("\n✨ Hoàn thành thu thập dữ liệu!")