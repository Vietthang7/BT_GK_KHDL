
// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Loading animation
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Add animation when elements come into view
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .metric-card, .stat-card').forEach(el => {
    observer.observe(el);
});

// Console greeting
console.log('%c🎓 Dự án Phân tích Dữ liệu - COVID-19 & Kinh tế', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cPhát triển bởi nhóm Khoa học Dữ liệu', 'color: #6b7280; font-size: 14px;');



// Check if we're on dashboard page
if (document.querySelector('.dashboard-page')) {
    initDashboard();
}

function initDashboard() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
            
            // Load charts for active tab
            loadChartsForTab(btn.dataset.tab);
        });
    });

    // Load initial charts
    loadChartsForTab('economy');
}

function loadChartsForTab(tab) {
    if (tab === 'economy') {
        loadEconomyTimeseries();
        loadEconomyDistribution();
        loadEconomyHeatmap();
        loadEconomySunburst();
        loadEconomyComparison();
    } else if (tab === 'covid') {
        loadCovidTimeseries();
        loadCovidTreemap();
    } else if (tab === 'impact') {
        loadEconomyScatter();
        loadImpactAnalysis();
    }
}



// Economy Time Series
function loadEconomyTimeseries() {
    const metricSelect = document.getElementById('economy-metric');
    if (!metricSelect) return;
    
    const metric = metricSelect.value;
    
    fetch(`/api/economy/timeseries?metric=${metric}`)
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('economy-timeseries', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading economy timeseries:', err));
}

// Add event listener for economy metric selector
if (document.getElementById('economy-metric')) {
    document.getElementById('economy-metric').addEventListener('change', loadEconomyTimeseries);
}

// Economy Distribution
function loadEconomyDistribution() {
    const metricSelect = document.getElementById('distribution-metric');
    const typeSelect = document.getElementById('distribution-type');
    if (!metricSelect || !typeSelect) return;
    
    const metric = metricSelect.value;
    const type = typeSelect.value;
    
    fetch(`/api/economy/distribution?metric=${metric}&type=${type}`)
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('economy-distribution', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading economy distribution:', err));
}

// Add event listeners
if (document.getElementById('distribution-metric')) {
    document.getElementById('distribution-metric').addEventListener('change', loadEconomyDistribution);
}
if (document.getElementById('distribution-type')) {
    document.getElementById('distribution-type').addEventListener('change', loadEconomyDistribution);
}

// Economy Heatmap
function loadEconomyHeatmap() {
    fetch('/api/economy/heatmap')
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('economy-heatmap', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading economy heatmap:', err));
}

// Economy Sunburst
function loadEconomySunburst() {
    fetch('/api/economy/sunburst')
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('economy-sunburst', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading economy sunburst:', err));
}

// Economy Comparison
function loadEconomyComparison() {
    fetch('/api/economy/comparison')
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('economy-comparison', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading economy comparison:', err));
}


function loadCovidTimeseries() {
    const metricSelect = document.getElementById('covid-metric');
    const showMACheckbox = document.getElementById('covid-show-ma');
    if (!metricSelect || !showMACheckbox) return;
    
    const metric = metricSelect.value;
    const showMA = showMACheckbox.checked;
    
    fetch(`/api/covid/timeseries?metric=${metric}&show_ma=${showMA}`)
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('covid-timeseries', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading covid timeseries:', err));
}

// Add event listeners
if (document.getElementById('covid-metric')) {
    document.getElementById('covid-metric').addEventListener('change', loadCovidTimeseries);
}
if (document.getElementById('covid-show-ma')) {
    document.getElementById('covid-show-ma').addEventListener('change', loadCovidTimeseries);
}

// COVID Treemap
function loadCovidTreemap() {
    fetch('/api/covid/treemap')
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('covid-treemap', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading covid treemap:', err));
}

function loadEconomyScatter() {
    const xSelect = document.getElementById('scatter-x');
    const ySelect = document.getElementById('scatter-y');
    if (!xSelect || !ySelect) return;
    
    const x = xSelect.value;
    const y = ySelect.value;
    
    fetch(`/api/economy/scatter?x=${x}&y=${y}`)
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('economy-scatter', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading economy scatter:', err));
}

// Add event listeners
if (document.getElementById('scatter-x')) {
    document.getElementById('scatter-x').addEventListener('change', loadEconomyScatter);
}
if (document.getElementById('scatter-y')) {
    document.getElementById('scatter-y').addEventListener('change', loadEconomyScatter);
}

// Impact Analysis
function loadImpactAnalysis() {
    fetch('/api/impact/analysis')
        .then(res => res.json())
        .then(data => {
            Plotly.newPlot('impact-analysis', data.data, data.layout, {responsive: true});
        })
        .catch(err => console.error('Error loading impact analysis:', err));
}


window.addEventListener('resize', debounce(() => {
    const chartIds = [
        'economy-timeseries',
        'economy-distribution',
        'economy-heatmap',
        'economy-sunburst',
        'economy-comparison',
        'covid-timeseries',
        'covid-treemap',
        'economy-scatter',
        'impact-analysis'
    ];
    
    chartIds.forEach(id => {
        const element = document.getElementById(id);
        if (element && element.data) {
            Plotly.Plots.resize(element);
        }
    });
}, 250));

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const printBtn = document.getElementById('print-report');
if (printBtn) {
    printBtn.addEventListener('click', () => {
        window.print();
    });
}

function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(col => csvRow.push(col.innerText));
        csv.push(csvRow.join(','));
    });
    
    // Download CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}



const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.toggle('dark-theme', savedTheme === 'dark');
    
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
    });
}


function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});


if (window.performance) {
    window.addEventListener('load', () => {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`⚡ Page loaded in ${pageLoadTime}ms`);
    });
}
