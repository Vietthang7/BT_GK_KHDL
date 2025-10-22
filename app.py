from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
from scipy import stats
import folium

app = Flask(__name__)

# Load data
weather_df = pd.read_csv('data/processed/weather_data_processed.csv')
weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
weather_df['date'] = pd.to_datetime(weather_df['date'])

covid_df = pd.read_csv('data/processed/covid_data_processed.csv')
covid_df['date'] = pd.to_datetime(covid_df['date'])

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard chính"""
    # Tính toán thống kê
    stats = {
        'total_records': len(weather_df),
        'avg_temp': round(weather_df['temperature'].mean(), 2),
        'avg_humidity': round(weather_df['humidity'].mean(), 2),
        'total_covid_cases': int(covid_df['cases'].iloc[-1]),
        'date_range': f"{weather_df['timestamp'].min().strftime('%d/%m/%Y')} - {weather_df['timestamp'].max().strftime('%d/%m/%Y')}"
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/api/weather/timeseries')
def weather_timeseries():
    """API: Biểu đồ thời gian nhiệt độ"""
    # Lấy tham số filter
    metric = request.args.get('metric', 'temperature')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Filter dữ liệu
    df = weather_df.copy()
    if start_date:
        df = df[df['timestamp'] >= start_date]
    if end_date:
        df = df[df['timestamp'] <= end_date]
    
    # Tạo biểu đồ
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df[metric],
        mode='lines',
        fill='tozeroy',
        name=metric.capitalize(),
        line=dict(color='#667eea', width=2)
    ))
    
    fig.update_layout(
        title=f'{metric.capitalize()} theo thời gian',
        xaxis_title='Thời gian',
        yaxis_title=metric.capitalize(),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/weather/distribution')
def weather_distribution():
    """API: Phân phối dữ liệu"""
    metric = request.args.get('metric', 'temperature')
    chart_type = request.args.get('type', 'histogram')
    
    df = weather_df.copy()
    
    if chart_type == 'histogram':
        fig = px.histogram(df, x=metric, nbins=30, 
                          title=f'Histogram - {metric.capitalize()}',
                          color_discrete_sequence=['#667eea'])
    elif chart_type == 'box':
        fig = px.box(df, y=metric, 
                     title=f'Boxplot - {metric.capitalize()}',
                     color_discrete_sequence=['#764ba2'])
    elif chart_type == 'violin':
        fig = px.violin(df, y=metric, box=True,
                       title=f'Violin Plot - {metric.capitalize()}',
                       color_discrete_sequence=['#f093fb'])
    
    fig.update_layout(template='plotly_white', height=400)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/weather/scatter')
def weather_scatter():
    """API: Scatter plot với hồi quy"""
    x_metric = request.args.get('x', 'temperature')
    y_metric = request.args.get('y', 'humidity')
    
    df = weather_df.copy()
    
    # Tính correlation
    correlation = df[[x_metric, y_metric]].corr().iloc[0, 1]
    
    fig = px.scatter(df, x=x_metric, y=y_metric,
                    trendline="ols",
                    title=f'{x_metric.capitalize()} vs {y_metric.capitalize()}<br>Correlation: {correlation:.3f}',
                    color_discrete_sequence=['#667eea'])
    
    fig.update_layout(template='plotly_white', height=500)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/weather/heatmap')
def weather_heatmap():
    """API: Heatmap tương quan"""
    numeric_cols = ['temperature', 'humidity', 'precipitation', 'wind_speed']
    corr_matrix = weather_df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title='Ma trận tương quan',
        template='plotly_white',
        height=500
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/weather/hourly')
def weather_hourly():
    """API: Biểu đồ theo giờ"""
    metric = request.args.get('metric', 'temperature')
    
    hourly_avg = weather_df.groupby('hour')[metric].mean().reset_index()
    
    fig = px.bar(hourly_avg, x='hour', y=metric,
                title=f'Trung bình {metric.capitalize()} theo giờ trong ngày',
                color=metric,
                color_continuous_scale='Viridis')
    
    fig.update_layout(template='plotly_white', height=400)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/covid/timeseries')
def covid_timeseries():
    """API: COVID-19 time series"""
    metric = request.args.get('metric', 'cases')
    show_ma = request.args.get('show_ma', 'true') == 'true'
    
    fig = go.Figure()
    
    # Đường chính
    fig.add_trace(go.Scatter(
        x=covid_df['date'],
        y=covid_df[metric],
        mode='lines',
        name=metric.capitalize(),
        line=dict(color='#ff6b6b', width=2)
    ))
    
    # Moving average
    if show_ma and f'{metric}_ma7' in covid_df.columns:
        fig.add_trace(go.Scatter(
            x=covid_df['date'],
            y=covid_df[f'{metric}_ma7'],
            mode='lines',
            name='7-day MA',
            line=dict(color='#4ecdc4', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=f'COVID-19 {metric.capitalize()} theo thời gian',
        xaxis_title='Ngày',
        yaxis_title=metric.capitalize(),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/covid/treemap')
def covid_treemap():
    """API: Treemap"""
    # Tạo dữ liệu treemap theo tháng
    covid_df['month_str'] = pd.to_datetime(covid_df['date']).dt.strftime('%Y-%m')
    monthly = covid_df.groupby('month_str').agg({
        'cases': 'last',
        'deaths': 'last',
        'recovered': 'last'
    }).reset_index()
    
    # Tính số ca mới mỗi tháng
    monthly['new_cases'] = monthly['cases'].diff().fillna(monthly['cases'])
    
    fig = px.treemap(monthly, 
                    path=['month_str'], 
                    values='new_cases',
                    title='Treemap: Số ca COVID-19 mới theo tháng',
                    color='new_cases',
                    color_continuous_scale='Reds')
    
    fig.update_layout(height=500)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/weather/sunburst')
def weather_sunburst():
    """API: Sunburst chart"""
    # Nhóm theo tháng và danh mục nhiệt độ
    df = weather_df.copy()
    df['month_str'] = df['timestamp'].dt.strftime('%Y-%m')
    
    grouped = df.groupby(['month_str', 'temp_category']).size().reset_index(name='count')
    
    fig = px.sunburst(grouped,
                     path=['month_str', 'temp_category'],
                     values='count',
                     title='Sunburst: Phân bố nhiệt độ theo tháng',
                     color='count',
                     color_continuous_scale='RdYlBu_r')
    
    fig.update_layout(height=500)
    return jsonify(json.loads(fig.to_json()))

@app.route('/report')
def report():
    """Trang báo cáo storytelling"""
    # Tính toán insights
    insights = {
        'avg_temp': round(weather_df['temperature'].mean(), 2),
        'max_temp': round(weather_df['temperature'].max(), 2),
        'min_temp': round(weather_df['temperature'].min(), 2),
        'correlation_temp_humidity': round(weather_df[['temperature', 'humidity']].corr().iloc[0, 1], 3),
        'total_covid_cases': int(covid_df['cases'].iloc[-1]),
        'total_covid_deaths': int(covid_df['deaths'].iloc[-1]),
        'total_covid_recovered': int(covid_df['recovered'].iloc[-1]),
        'avg_daily_cases': round(covid_df['cases_change'].mean(), 2)
    }
    
    return render_template('report.html', insights=insights)

@app.route('/api/stats')
def get_stats():
    """API: Lấy thống kê tổng quan"""
    stats = {
        'weather': {
            'total_records': len(weather_df),
            'avg_temp': round(weather_df['temperature'].mean(), 2),
            'max_temp': round(weather_df['temperature'].max(), 2),
            'min_temp': round(weather_df['temperature'].min(), 2),
            'avg_humidity': round(weather_df['humidity'].mean(), 2),
            'total_precipitation': round(weather_df['precipitation'].sum(), 2)
        },
        'covid': {
            'total_cases': int(covid_df['cases'].iloc[-1]),
            'total_deaths': int(covid_df['deaths'].iloc[-1]),
            'total_recovered': int(covid_df['recovered'].iloc[-1]),
            'mortality_rate': round((covid_df['deaths'].iloc[-1] / covid_df['cases'].iloc[-1]) * 100, 2)
        }
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)