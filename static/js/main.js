// Utility function để load biểu đồ
function loadChart(url, divId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = url + (queryString ? `?${queryString}` : '');
    
    fetch(fullUrl)
        .then(response => response.json())
        .then(data => {
            Plotly.newPlot(divId, data.data, data.layout, {responsive: true});
        })
        .catch(error => {
            console.error('Error loading chart:', error);
            document.getElementById(divId).innerHTML = 
                '<div class="alert alert-danger">Không thể tải biểu đồ</div>';
        });
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Distribution Chart
    function updateDistribution() {
        const metric = document.getElementById('distMetric').value;
        const type = document.getElementById('distType').value;
        loadChart('/api/weather/distribution', 'distributionChart', {metric, type});
    }
    
    document.getElementById('distMetric')?.addEventListener('change', updateDistribution);
    document.getElementById('distType')?.addEventListener('change', updateDistribution);
    updateDistribution();
    
    // 2. Time Series Chart
    function updateTimeseries() {
        const metric = document.getElementById('timeMetric').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        loadChart('/api/weather/timeseries', 'timeseriesChart', {
            metric, 
            start_date: startDate, 
            end_date: endDate
        });
    }
    
    document.getElementById('timeMetric')?.addEventListener('change', updateTimeseries);
    document.getElementById('startDate')?.addEventListener('change', updateTimeseries);
    document.getElementById('endDate')?.addEventListener('change', updateTimeseries);
    updateTimeseries();
    
    // 3. Scatter Chart
  function updateScatter() {
      const xSelect = document.getElementById('scatterX');
      const ySelect = document.getElementById('scatterY');
      const x = xSelect.value;
      const y = ySelect.value;
      
      // Nếu x và y giống nhau, tự động chọn y khác
      if (x === y) {
          const options = ['temperature', 'humidity', 'precipitation', 'wind_speed'];
          const otherOption = options.find(opt => opt !== x);
          ySelect.value = otherOption;
          return; // Hàm sẽ được gọi lại khi ySelect thay đổi
      }
      
      loadChart('/api/weather/scatter', 'scatterChart', {x, y});
  }

  document.getElementById('scatterX')?.addEventListener('change', updateScatter);
  document.getElementById('scatterY')?.addEventListener('change', updateScatter);
  updateScatter();

    
    // 4. Heatmap (không cần filter)
    loadChart('/api/weather/heatmap', 'heatmapChart');
    
    // 5. Hourly Chart
    function updateHourly() {
        const metric = document.getElementById('hourlyMetric').value;
        loadChart('/api/weather/hourly', 'hourlyChart', {metric});
    }
    
    document.getElementById('hourlyMetric')?.addEventListener('change', updateHourly);
    updateHourly();
    
    // 6. COVID Chart
    function updateCovid() {
        const metric = document.getElementById('covidMetric').value;
        const showMA = document.getElementById('showMA').checked;
        loadChart('/api/covid/timeseries', 'covidChart', {
            metric, 
            show_ma: showMA
        });
    }
    
    document.getElementById('covidMetric')?.addEventListener('change', updateCovid);
    document.getElementById('showMA')?.addEventListener('change', updateCovid);
    updateCovid();
    
    // 7. Treemap
    loadChart('/api/covid/treemap', 'treemapChart');
    
    // 8. Sunburst
    loadChart('/api/weather/sunburst', 'sunburstChart');
});