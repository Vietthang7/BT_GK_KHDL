import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

class CovidEconomyVisualizer:
    """Class để tạo các biểu đồ phân tích COVID-19 và kinh tế"""
    
    def __init__(self):
        self.covid_data = None
        self.economy_data = None
        self.merged_data = None
    
    def load_data(self):
        """Load dữ liệu đã xử lý"""
        try:
            self.covid_data = pd.read_csv('data/processed/covid_data_processed.csv')
            self.economy_data = pd.read_csv('data/processed/economy_data_processed.csv')
            
            if 'date' in self.covid_data.columns:
                self.covid_data['date'] = pd.to_datetime(self.covid_data['date'])
            if 'date' in self.economy_data.columns:
                self.economy_data['date'] = pd.to_datetime(self.economy_data['date'])
            
            if 'date' in self.covid_data.columns and 'date' in self.economy_data.columns:
                self.merged_data = pd.merge(
                    self.covid_data, 
                    self.economy_data, 
                    on='date', 
                    how='inner'
                )
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_covid_cases_timeline(self):
        """Tạo biểu đồ timeline số ca COVID"""
        if self.covid_data is None:
            return None
        
        fig = go.Figure()
        
        if 'date' in self.covid_data.columns and 'cases' in self.covid_data.columns:
            fig.add_trace(go.Scatter(
                x=self.covid_data['date'],
                y=self.covid_data['cases'],
                mode='lines+markers',
                name='Số ca COVID-19',
                line=dict(color='red', width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title='Diễn biến số ca COVID-19 theo thời gian',
            xaxis_title='Thời gian',
            yaxis_title='Số ca',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_unemployment_timeline(self):
        """Tạo biểu đồ timeline tỷ lệ thất nghiệp"""
        if self.economy_data is None:
            return None
        
        fig = go.Figure()
        
        if 'date' in self.economy_data.columns and 'unemployment_rate' in self.economy_data.columns:
            fig.add_trace(go.Scatter(
                x=self.economy_data['date'],
                y=self.economy_data['unemployment_rate'],
                mode='lines+markers',
                name='Tỷ lệ thất nghiệp',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title='Diễn biến tỷ lệ thất nghiệp theo thời gian',
            xaxis_title='Thời gian',
            yaxis_title='Tỷ lệ thất nghiệp (%)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_gdp_timeline(self):
        """Tạo biểu đồ timeline tăng trưởng GDP"""
        if self.economy_data is None:
            return None
        
        fig = go.Figure()
        
        if 'date' in self.economy_data.columns and 'gdp_growth' in self.economy_data.columns:
            fig.add_trace(go.Scatter(
                x=self.economy_data['date'],
                y=self.economy_data['gdp_growth'],
                mode='lines+markers',
                name='Tăng trưởng GDP',
                line=dict(color='green', width=2),
                marker=dict(size=6),
                fill='tozeroy'
            ))
        
        fig.update_layout(
            title='Diễn biến tăng trưởng GDP theo thời gian',
            xaxis_title='Thời gian',
            yaxis_title='Tăng trưởng GDP (%)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_covid_vs_unemployment_scatter(self):
        """Tạo scatter plot COVID cases vs Unemployment Rate"""
        if self.merged_data is None:
            return None
        
        fig = go.Figure()
        
        if 'cases' in self.merged_data.columns and 'unemployment_rate' in self.merged_data.columns:
            correlation = self.merged_data['cases'].corr(self.merged_data['unemployment_rate'])
            
            fig.add_trace(go.Scatter(
                x=self.merged_data['cases'],
                y=self.merged_data['unemployment_rate'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=self.merged_data.index,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Thời gian")
                ),
                text=self.merged_data['date'].astype(str) if 'date' in self.merged_data.columns else None,
                hovertemplate='<b>Số ca COVID:</b> %{x}<br><b>Tỷ lệ thất nghiệp:</b> %{y}%<br><b>Ngày:</b> %{text}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f'COVID Cases vs Unemployment Rate<br><sub>Correlation: {correlation:.3f}</sub>',
                xaxis_title='COVID Cases',
                yaxis_title='Unemployment Rate (%)',
                template='plotly_white'
            )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_covid_vs_gdp_scatter(self):
        """Tạo scatter plot COVID cases vs GDP Growth"""
        if self.merged_data is None:
            return None
        
        fig = go.Figure()
        
        if 'cases' in self.merged_data.columns and 'gdp_growth' in self.merged_data.columns:
            correlation = self.merged_data['cases'].corr(self.merged_data['gdp_growth'])
            
            fig.add_trace(go.Scatter(
                x=self.merged_data['cases'],
                y=self.merged_data['gdp_growth'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=self.merged_data.index,
                    colorscale='Plasma',
                    showscale=True,
                    colorbar=dict(title="Thời gian")
                ),
                text=self.merged_data['date'].astype(str) if 'date' in self.merged_data.columns else None,
                hovertemplate='<b>Số ca COVID:</b> %{x}<br><b>Tăng trưởng GDP:</b> %{y}%<br><b>Ngày:</b> %{text}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f'COVID Cases vs GDP Growth<br><sub>Correlation: {correlation:.3f}</sub>',
                xaxis_title='COVID Cases',
                yaxis_title='GDP Growth (%)',
                template='plotly_white'
            )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_correlation_matrix(self):
      """Tạo ma trận tương quan"""
      if self.merged_data is None:
          return None
      
      selected_cols = []
      
      priority_cols = ['cases', 'deaths', 'unemployment_rate', 'gdp_growth', 'stock_index', 'retail_sales']
      
      for col in priority_cols:
          if col in self.merged_data.columns:
              selected_cols.append(col)
      
      if not selected_cols:
          selected_cols = self.merged_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
      
      corr_matrix = self.merged_data[selected_cols].corr()
      
      label_mapping = {
          'cases': 'Số ca COVID',
          'deaths': 'Tử vong',
          'recovered': 'Hồi phục',
          'unemployment_rate': 'Tỷ lệ thất nghiệp',
          'gdp_growth': 'Tăng trưởng GDP',
          'stock_index': 'Chỉ số chứng khoán',
          'retail_sales': 'Doanh thu bán lẻ'
      }
      
      readable_labels = [label_mapping.get(col, col) for col in corr_matrix.columns]
      
      fig = go.Figure(data=go.Heatmap(
          z=corr_matrix.values,
          x=readable_labels,
          y=readable_labels,
          colorscale='RdBu',
          zmid=0,
          zmin=-1,
          zmax=1,
          text=corr_matrix.values.round(2),
          texttemplate='%{text}',
          textfont={"size": 14, "color": "black"},
          colorbar=dict(
              title=dict(
                  text="Hệ số<br>tương quan",
                  side="right"
              ),
              tickmode="linear",
              tick0=-1,
              dtick=0.5
          ),
          hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
      ))
      
      fig.update_layout(
          title={
              'text': 'Ma trận Tương quan - Chỉ số Kinh tế & COVID-19',
              'x': 0.5,
              'xanchor': 'center',
              'font': {'size': 18}
          },
          template='plotly_white',
          width=800,
          height=700,
          xaxis={
              'tickangle': -45,
              'tickfont': {'size': 12}
          },
          yaxis={
              'tickfont': {'size': 12}
          },
          margin=dict(l=150, r=150, t=100, b=150)
      )
      
      return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    def create_combined_timeline(self):
        """Tạo biểu đồ kết hợp COVID và kinh tế"""
        if self.merged_data is None:
            return None
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('COVID Cases vs Unemployment Rate', 'COVID Cases vs GDP Growth'),
            specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
            vertical_spacing=0.15
        )
        
        if 'date' in self.merged_data.columns:
            if 'cases' in self.merged_data.columns:
                fig.add_trace(
                    go.Scatter(x=self.merged_data['date'], y=self.merged_data['cases'],
                              name="COVID Cases", line=dict(color='red')),
                    row=1, col=1, secondary_y=False
                )
            
            if 'unemployment_rate' in self.merged_data.columns:
                fig.add_trace(
                    go.Scatter(x=self.merged_data['date'], y=self.merged_data['unemployment_rate'],
                              name="Unemployment Rate", line=dict(color='blue')),
                    row=1, col=1, secondary_y=True
                )
            
            if 'cases' in self.merged_data.columns:
                fig.add_trace(
                    go.Scatter(x=self.merged_data['date'], y=self.merged_data['cases'],
                              name="COVID Cases", line=dict(color='red'), showlegend=False),
                    row=2, col=1, secondary_y=False
                )
            
            if 'gdp_growth' in self.merged_data.columns:
                fig.add_trace(
                    go.Scatter(x=self.merged_data['date'], y=self.merged_data['gdp_growth'],
                              name="GDP Growth", line=dict(color='green')),
                    row=2, col=1, secondary_y=True
                )
        
        fig.update_xaxes(title_text="Thời gian", row=1, col=1)
        fig.update_xaxes(title_text="Thời gian", row=2, col=1)
        
        fig.update_yaxes(title_text="COVID Cases", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Unemployment Rate (%)", row=1, col=1, secondary_y=True)
        
        fig.update_yaxes(title_text="COVID Cases", row=2, col=1, secondary_y=False)
        fig.update_yaxes(title_text="GDP Growth (%)", row=2, col=1, secondary_y=True)
        
        fig.update_layout(
            title_text="Phân tích Tác động COVID-19 lên Kinh tế",
            height=800,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_statistics(self):
        """Lấy thống kê tổng quan"""
        if self.merged_data is None:
            return {}
        
        stats = {}
        
        if 'cases' in self.merged_data.columns:
            stats['total_cases'] = int(self.merged_data['cases'].sum())
            stats['avg_cases'] = float(self.merged_data['cases'].mean())
            stats['max_cases'] = int(self.merged_data['cases'].max())
        
        if 'unemployment_rate' in self.merged_data.columns:
            stats['avg_unemployment'] = float(self.merged_data['unemployment_rate'].mean())
            stats['max_unemployment'] = float(self.merged_data['unemployment_rate'].max())
            stats['min_unemployment'] = float(self.merged_data['unemployment_rate'].min())
        
        if 'gdp_growth' in self.merged_data.columns:
            stats['avg_gdp_growth'] = float(self.merged_data['gdp_growth'].mean())
            stats['max_gdp_growth'] = float(self.merged_data['gdp_growth'].max())
            stats['min_gdp_growth'] = float(self.merged_data['gdp_growth'].min())
        
        if 'cases' in self.merged_data.columns and 'unemployment_rate' in self.merged_data.columns:
            stats['corr_cases_unemployment'] = float(
                self.merged_data['cases'].corr(self.merged_data['unemployment_rate'])
            )
        
        if 'cases' in self.merged_data.columns and 'gdp_growth' in self.merged_data.columns:
            stats['corr_cases_gdp'] = float(
                self.merged_data['cases'].corr(self.merged_data['gdp_growth'])
            )
        
        return stats

def create_all_visualizations():
    """Tạo tất cả các biểu đồ"""
    visualizer = CovidEconomyVisualizer()
    
    if not visualizer.load_data():
        return None
    
    return {
        'covid_timeline': visualizer.create_covid_cases_timeline(),
        'unemployment_timeline': visualizer.create_unemployment_timeline(),
        'gdp_timeline': visualizer.create_gdp_timeline(),
        'covid_vs_unemployment': visualizer.create_covid_vs_unemployment_scatter(),
        'covid_vs_gdp': visualizer.create_covid_vs_gdp_scatter(),
        'correlation_matrix': visualizer.create_correlation_matrix(),
        'combined_timeline': visualizer.create_combined_timeline(),
        'statistics': visualizer.get_statistics()
    }

if __name__ == "__main__":
    visualizer = CovidEconomyVisualizer()
    if visualizer.load_data():
        print("Data loaded successfully!")
        print("\nStatistics:")
        stats = visualizer.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print("Failed to load data")