from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
from scipy import stats
from src.visualization import CovidEconomyVisualizer, create_all_visualizations

app = Flask(__name__)

# Initialize visualizer
visualizer = CovidEconomyVisualizer()
visualizer.load_data()

# Load data (giữ lại để backward compatibility)
economy_df = pd.read_csv('data/processed/economy_data_processed.csv')
economy_df['date'] = pd.to_datetime(economy_df['date'])

covid_df = pd.read_csv('data/processed/covid_data_processed.csv')
covid_df['date'] = pd.to_datetime(covid_df['date'])

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard chính"""
    # Lấy thống kê từ visualizer
    stats_from_viz = visualizer.get_statistics()
    
    # Tính toán thống kê bổ sung
    stats = {
        'total_records': len(economy_df),
        'avg_unemployment': stats_from_viz.get('avg_unemployment', round(economy_df['unemployment_rate'].mean(), 2)),
        'avg_gdp_growth': stats_from_viz.get('avg_gdp_growth', round(economy_df['gdp_growth'].mean(), 2)),
        'total_covid_cases': stats_from_viz.get('total_cases', int(covid_df['cases'].iloc[-1])),
        'date_range': f"{economy_df['date'].min().strftime('%d/%m/%Y')} - {economy_df['date'].max().strftime('%d/%m/%Y')}",
        'max_unemployment': stats_from_viz.get('max_unemployment', 0),
        'min_unemployment': stats_from_viz.get('min_unemployment', 0),
        'corr_cases_unemployment': stats_from_viz.get('corr_cases_unemployment', 0),
        'corr_cases_gdp': stats_from_viz.get('corr_cases_gdp', 0)
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/api/economy/timeseries')
def economy_timeseries():
    """API: Biểu đồ thời gian chỉ số kinh tế"""
    metric = request.args.get('metric', 'unemployment_rate')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Filter dữ liệu
    df = economy_df.copy()
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    # Tạo biểu đồ
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[metric],
        mode='lines+markers',
        fill='tozeroy',
        name=metric.replace('_', ' ').title(),
        line=dict(color='#667eea', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=f'{metric.replace("_", " ").title()} theo thời gian',
        xaxis_title='Thời gian',
        yaxis_title=metric.replace('_', ' ').title(),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/economy/distribution')
def economy_distribution():
    """API: Phân phối dữ liệu kinh tế"""
    metric = request.args.get('metric', 'unemployment_rate')
    chart_type = request.args.get('type', 'histogram')
    
    df = economy_df.copy()
    
    if chart_type == 'histogram':
        fig = px.histogram(df, x=metric, nbins=20, 
                          title=f'Histogram - {metric.replace("_", " ").title()}',
                          color_discrete_sequence=['#667eea'])
    elif chart_type == 'box':
        fig = px.box(df, y=metric, 
                     title=f'Boxplot - {metric.replace("_", " ").title()}',
                     color_discrete_sequence=['#764ba2'])
    elif chart_type == 'violin':
        fig = px.violin(df, y=metric, box=True,
                       title=f'Violin Plot - {metric.replace("_", " ").title()}',
                       color_discrete_sequence=['#f093fb'])
    
    fig.update_layout(template='plotly_white', height=400)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/economy/scatter')
def economy_scatter():
    """API: Scatter plot - Kinh tế vs COVID"""
    x_metric = request.args.get('x', 'unemployment_rate')
    y_metric = request.args.get('y', 'cases')
    
    # Sử dụng visualizer nếu là COVID vs Unemployment
    if x_metric == 'unemployment_rate' and y_metric == 'cases':
        chart_data = visualizer.create_covid_vs_unemployment_scatter()
        if chart_data:
            return jsonify(json.loads(chart_data))
    elif x_metric == 'gdp_growth' and y_metric == 'cases':
        chart_data = visualizer.create_covid_vs_gdp_scatter()
        if chart_data:
            return jsonify(json.loads(chart_data))
    
    # Fallback: tạo scatter plot thông thường
    merged = pd.merge(economy_df, covid_df, on='date', how='inner')
    
    # Tính correlation
    correlation = merged[[x_metric, y_metric]].corr().iloc[0, 1]
    
    fig = px.scatter(merged, x=x_metric, y=y_metric,
                    trendline="ols",
                    title=f'{x_metric.replace("_", " ").title()} vs {y_metric.title()}<br>Correlation: {correlation:.3f}',
                    color_discrete_sequence=['#667eea'],
                    hover_data=['date'])
    
    fig.update_layout(template='plotly_white', height=500)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/economy/heatmap')
def economy_heatmap():
    """API: Heatmap tương quan kinh tế"""
    # Sử dụng visualizer
    chart_data = visualizer.create_correlation_matrix()
    if chart_data:
        return jsonify(json.loads(chart_data))
    
    # Fallback
    numeric_cols = ['unemployment_rate', 'gdp_growth', 'stock_index', 'retail_sales']
    corr_matrix = economy_df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[col.replace('_', ' ').title() for col in corr_matrix.columns],
        y=[col.replace('_', ' ').title() for col in corr_matrix.columns],
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title='Ma trận tương quan - Chỉ số Kinh tế',
        template='plotly_white',
        height=500
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/economy/comparison')
def economy_comparison():
    """API: So sánh đa chỉ số"""
    # Chuẩn hóa dữ liệu về scale 0-100
    df = economy_df.copy()
    metrics = ['unemployment_rate', 'gdp_growth', 'stock_index', 'retail_sales']
    
    fig = go.Figure()
    
    for metric in metrics:
        # Normalize to 0-100 scale
        normalized = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min()) * 100
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=normalized,
            mode='lines',
            name=metric.replace('_', ' ').title()
        ))
    
    fig.update_layout(
        title='So sánh các Chỉ số Kinh tế (Normalized)',
        xaxis_title='Thời gian',
        yaxis_title='Giá trị (0-100)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/covid/timeseries')
def covid_timeseries():
    """API: COVID-19 time series"""
    # Sử dụng visualizer
    chart_data = visualizer.create_covid_cases_timeline()
    if chart_data:
        return jsonify(json.loads(chart_data))
    
    # Fallback
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
    covid_df['month_str'] = pd.to_datetime(covid_df['date']).dt.strftime('%Y-%m')
    monthly = covid_df.groupby('month_str').agg({
        'cases': 'last',
        'deaths': 'last',
        'recovered': 'last'
    }).reset_index()
    
    monthly['new_cases'] = monthly['cases'].diff().fillna(monthly['cases'])
    
    fig = px.treemap(monthly, 
                    path=['month_str'], 
                    values='new_cases',
                    title='Treemap: Số ca COVID-19 mới theo tháng',
                    color='new_cases',
                    color_continuous_scale='Reds')
    
    fig.update_layout(height=500)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/economy/sunburst')
def economy_sunburst():
    """API: Sunburst chart - Phân loại kinh tế"""
    df = economy_df.copy()
    df['month_str'] = df['date'].dt.strftime('%Y-%m')
    df['quarter'] = df['date'].dt.to_period('Q').astype(str)
    
    # Phân loại tình trạng kinh tế
    df['economic_status'] = pd.cut(df['unemployment_rate'], 
                                    bins=[0, 3, 5, 100],
                                    labels=['Tốt', 'Trung bình', 'Xấu'])
    
    grouped = df.groupby(['quarter', 'economic_status']).size().reset_index(name='count')
    
    fig = px.sunburst(grouped,
                     path=['quarter', 'economic_status'],
                     values='count',
                     title='Sunburst: Tình trạng Kinh tế theo Quý',
                     color='count',
                     color_continuous_scale='RdYlGn_r')
    
    fig.update_layout(height=500)
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/impact/analysis')
def impact_analysis():
    """API: Phân tích tác động COVID lên Kinh tế"""
    # Sử dụng visualizer
    chart_data = visualizer.create_combined_timeline()
    if chart_data:
        return jsonify(json.loads(chart_data))
    
    # Fallback
    merged = pd.merge(economy_df, covid_df[['date', 'cases', 'deaths']], on='date', how='inner')
    
    # Tạo subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('COVID Cases vs Unemployment Rate', 'COVID Cases vs GDP Growth'),
        vertical_spacing=0.15
    )
    
    # Plot 1: Cases vs Unemployment
    fig.add_trace(
        go.Scatter(x=merged['cases'], y=merged['unemployment_rate'], 
                  mode='markers', name='Unemployment',
                  marker=dict(color='#ff6b6b', size=6)),
        row=1, col=1
    )
    
    # Plot 2: Cases vs GDP
    fig.add_trace(
        go.Scatter(x=merged['cases'], y=merged['gdp_growth'], 
                  mode='markers', name='GDP Growth',
                  marker=dict(color='#4ecdc4', size=6)),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="COVID Cases", row=2, col=1)
    fig.update_yaxes(title_text="Unemployment Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="GDP Growth (%)", row=2, col=1)
    
    fig.update_layout(
        title_text="Phân tích Tác động COVID-19 lên Kinh tế",
        height=700,
        template='plotly_white',
        showlegend=False
    )
    
    return jsonify(json.loads(fig.to_json()))

@app.route('/api/visualizations/all')
def get_all_visualizations():
    """API: Lấy tất cả visualizations từ visualizer"""
    try:
        viz_data = create_all_visualizations()
        if viz_data:
            # Convert statistics to JSON serializable format
            response = {
                'covid_timeline': json.loads(viz_data['covid_timeline']) if viz_data.get('covid_timeline') else None,
                'unemployment_timeline': json.loads(viz_data['unemployment_timeline']) if viz_data.get('unemployment_timeline') else None,
                'gdp_timeline': json.loads(viz_data['gdp_timeline']) if viz_data.get('gdp_timeline') else None,
                'covid_vs_unemployment': json.loads(viz_data['covid_vs_unemployment']) if viz_data.get('covid_vs_unemployment') else None,
                'covid_vs_gdp': json.loads(viz_data['covid_vs_gdp']) if viz_data.get('covid_vs_gdp') else None,
                'correlation_matrix': json.loads(viz_data['correlation_matrix']) if viz_data.get('correlation_matrix') else None,
                'combined_timeline': json.loads(viz_data['combined_timeline']) if viz_data.get('combined_timeline') else None,
                'statistics': viz_data.get('statistics', {})
            }
            return jsonify(response)
        else:
            return jsonify({'error': 'Could not generate visualizations'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report')
def report():
    """Trang báo cáo storytelling"""
    # Lấy insights từ visualizer
    stats_from_viz = visualizer.get_statistics()
    
    # Merge data để tính correlation (fallback)
    merged = pd.merge(economy_df, covid_df[['date', 'cases', 'deaths']], on='date', how='inner')
    
    insights = {
        'avg_unemployment': stats_from_viz.get('avg_unemployment', round(economy_df['unemployment_rate'].mean(), 2)),
        'max_unemployment': stats_from_viz.get('max_unemployment', round(economy_df['unemployment_rate'].max(), 2)),
        'min_unemployment': stats_from_viz.get('min_unemployment', round(economy_df['unemployment_rate'].min(), 2)),
        'avg_gdp_growth': stats_from_viz.get('avg_gdp_growth', round(economy_df['gdp_growth'].mean(), 2)),
        'correlation_covid_unemployment': stats_from_viz.get('corr_cases_unemployment', round(merged[['cases', 'unemployment_rate']].corr().iloc[0, 1], 3)),
        'correlation_covid_gdp': stats_from_viz.get('corr_cases_gdp', round(merged[['cases', 'gdp_growth']].corr().iloc[0, 1], 3)),
        'total_covid_cases': stats_from_viz.get('total_cases', int(covid_df['cases'].iloc[-1])),
        'total_covid_deaths': int(covid_df['deaths'].iloc[-1]),
        'total_covid_recovered': int(covid_df['recovered'].iloc[-1]) if 'recovered' in covid_df.columns else 0,
    }
    
    return render_template('report.html', insights=insights)

@app.route('/api/stats')
def get_stats():
    """API: Lấy thống kê tổng quan"""
    # Sử dụng visualizer
    viz_stats = visualizer.get_statistics()
    
    stats = {
        'economy': {
            'total_records': len(economy_df),
            'avg_unemployment': viz_stats.get('avg_unemployment', round(economy_df['unemployment_rate'].mean(), 2)),
            'max_unemployment': viz_stats.get('max_unemployment', round(economy_df['unemployment_rate'].max(), 2)),
            'avg_gdp_growth': viz_stats.get('avg_gdp_growth', round(economy_df['gdp_growth'].mean(), 2)),
            'avg_stock_index': round(economy_df['stock_index'].mean(), 2) if 'stock_index' in economy_df.columns else 0
        },
        'covid': {
            'total_cases': viz_stats.get('total_cases', int(covid_df['cases'].iloc[-1])),
            'total_deaths': int(covid_df['deaths'].iloc[-1]),
            'total_recovered': int(covid_df['recovered'].iloc[-1]) if 'recovered' in covid_df.columns else 0,
            'mortality_rate': round((covid_df['deaths'].iloc[-1] / covid_df['cases'].iloc[-1]) * 100, 2) if covid_df['cases'].iloc[-1] > 0 else 0
        },
        'correlations': {
            'covid_unemployment': viz_stats.get('corr_cases_unemployment', 0),
            'covid_gdp': viz_stats.get('corr_cases_gdp', 0)
        }
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)