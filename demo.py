import pandas as pd
from src.visualization import CovidEconomyVisualizer

def generate_markdown_report():
    """Generate markdown report với data thực"""
    
    # Load visualizer
    visualizer = CovidEconomyVisualizer()
    visualizer.load_data()
    stats = visualizer.get_statistics()
    
    # Load data
    economy_df = pd.read_csv('data/processed/economy_data_processed.csv')
    covid_df = pd.read_csv('data/processed/covid_data_processed.csv')
    economy_df['date'] = pd.to_datetime(economy_df['date'])
    covid_df['date'] = pd.to_datetime(covid_df['date'])
    
    merged = pd.merge(economy_df, covid_df[['date', 'cases', 'deaths']], on='date', how='inner')
    
    # Calculate insights
    gdp_data = economy_df['gdp_growth']
    unemployment_data = economy_df['unemployment_rate']
    
    min_gdp_idx = gdp_data.idxmin()
    max_gdp_idx = gdp_data.idxmax()
    
    insights = {
        'total_covid_cases': f"{int(covid_df['cases'].iloc[-1]):,}",
        'avg_unemployment': round(unemployment_data.mean(), 2),
        'max_unemployment': round(unemployment_data.max(), 2),
        'min_unemployment': round(unemployment_data.min(), 2),
        'avg_gdp_growth': round(gdp_data.mean(), 2),
        'min_gdp_growth': round(gdp_data.min(), 2),
        'max_gdp_growth': round(gdp_data.max(), 2),
        'min_gdp_date': economy_df.loc[min_gdp_idx, 'date'].strftime('%m/%Y'),
        'max_gdp_date': economy_df.loc[max_gdp_idx, 'date'].strftime('%m/%Y'),
        'correlation_covid_unemployment': round(merged[['cases', 'unemployment_rate']].corr().iloc[0, 1], 3),
        'correlation_covid_gdp': round(merged[['cases', 'gdp_growth']].corr().iloc[0, 1], 3),
        'total_covid_deaths': f"{int(covid_df['deaths'].iloc[-1]):,}",
        'total_covid_recovered': f"{int(covid_df['recovered'].iloc[-1]):,}" if 'recovered' in covid_df.columns else "0",
    }
    
    # Read template
    with open('READ_PROFILE.md', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace placeholders
    for key, value in insights.items():
        template = template.replace(f'{{insights.{key}}}', str(value))
    
    # Replace -X%, +Y% placeholders
    template = template.replace('-X%', f"{insights['min_gdp_growth']}%")
    template = template.replace('+Y%', f"+{insights['max_gdp_growth']}%")
    template = template.replace('(Q2/2020)', f"({insights['min_gdp_date']})")
    template = template.replace('(Q3/2021)', f"({insights['max_gdp_date']})")
    
    # Write output
    with open('REPORT_FINAL.md', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Report generated successfully: REPORT_FINAL.md")
    print("\nInsights:")
    for key, value in insights.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    generate_markdown_report()