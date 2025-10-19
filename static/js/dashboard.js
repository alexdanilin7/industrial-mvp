function initCharts() {
    const dataEl = document.getElementById('dashboard-data');
    if (!dataEl) return;

    const revenueData = JSON.parse(dataEl.dataset.revenueByIndustry || '{}');
    const staffData = JSON.parse(dataEl.dataset.staffByDistrict || '{}');

    // Удаляем старые графики (если есть)
    Chart.helpers.each(Chart.instances, function (instance) {
        instance.destroy();
    });

    // График 1: Выручка по отраслям
    const revenueCtx = document.getElementById('revenueByIndustryChart');
    if (revenueCtx) {
        new Chart(revenueCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: revenueData.labels || [],
                datasets: [{
                    label: 'Выручка, млн ₽',
                    data: revenueData.data || [],
                    backgroundColor: 'rgba(54, 162, 235, 0.6)'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }

    // График 2: Занятость по районам
    const staffCtx = document.getElementById('staffByDistrictChart');
    if (staffCtx) {
        new Chart(staffCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: staffData.labels || [],
                datasets: [{
                    label: 'Средняя численность',
                    data: staffData.data || [],
                    backgroundColor: 'rgba(255, 206, 86, 0.6)'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', initCharts);

// Пересоздание графиков после HTMX-запроса
document.addEventListener('htmx:afterSettle', initCharts);