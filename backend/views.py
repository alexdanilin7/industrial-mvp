from django.shortcuts import render

# Create your views here.
# backend/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from enterprises.models import Enterprise, FinancialKPI
from django.db.models import Sum, Avg, Count, Max

from enterprises.models import Enterprise, FinancialKPI


def home(request):
    # Фильтры
    industry = request.GET.get('industry-filter')
    district = request.GET.get('district')
    year = request.GET.get('year')

    # Базовые QuerySet
    enterprises = Enterprise.objects.all()
    kpis = FinancialKPI.objects.all()

    # Применяем фильтры
    if industry:
        enterprises = enterprises.filter(main_industry=industry)
    if district:
        enterprises = enterprises.filter(geo_location__district=district)
    if year:
        kpis = kpis.filter(year=int(year))

    enterprise_ids = enterprises.values_list('id', flat=True)
    kpis = kpis.filter(enterprise_id__in=enterprise_ids)

    # Агрегаты
    enterprises_count = enterprises.count()
    total_revenue = kpis.aggregate(total=Sum('revenue'))['total'] or 0
    total_staff = kpis.aggregate(total=Avg('staff_total'))['total'] or 0
    export_volume = kpis.aggregate(total=Sum('export_volume'))['total'] or 0

    # Выручка по отраслям
    revenue_by_industry = list(
        Enterprise.objects.filter(id__in=enterprise_ids)
        .values('main_industry')
        .annotate(total_revenue=Sum('financial_kpis__revenue'))
        .filter(total_revenue__isnull=False)
        .order_by('-total_revenue')
    )
    revenue_chart = {
        'labels': [item['main_industry'] for item in revenue_by_industry],
        'data': [float(item['total_revenue'] or 0) / 1e6 for item in revenue_by_industry]
    }

    # Занятость по районам
    staff_by_district = list(
        Enterprise.objects.filter(id__in=enterprise_ids)
        .values('geo_location__district')
        .annotate(avg_staff=Avg('financial_kpis__staff_total'))
        .filter(avg_staff__isnull=False)
        .order_by('-avg_staff')
    )
    staff_chart = {
        'labels': [item['geo_location__district'] for item in staff_by_district if item['geo_location__district']],
        'data': [float(item['avg_staff'] or 0) for item in staff_by_district if item['geo_location__district']]
    }

    # Топ предприятий
    top_enterprises = (
        Enterprise.objects.filter(id__in=enterprise_ids)
        .annotate(
            total_revenue=Sum('financial_kpis__revenue'),
            total_staff=Avg('financial_kpis__staff_total')
        )
        .filter(total_revenue__isnull=False)
        .order_by('-total_revenue')[:10]
    )

    # Уникальные значения для фильтров
    industries = Enterprise.objects.values_list('main_industry', flat=True).distinct()
    districts = Enterprise.objects.exclude(geo_location__district='').values_list('geo_location__district',
                                                                                  flat=True).distinct()

    context = {
        'enterprises_count': enterprises_count,
        'total_revenue': float(total_revenue) / 1e6 if total_revenue else 0,
        'total_staff': int(total_staff) if total_staff else 0,
        'export_volume': float(export_volume) / 1e6 if export_volume else 0,
        'revenue_by_industry': json.dumps(revenue_chart),
        'staff_by_district': json.dumps(staff_chart),
        'top_enterprises': top_enterprises,
        'industries': [i for i in industries if i],
        'districts': [d for d in districts if d],
        'selected_industry': industry,
        'selected_district': district,
        'selected_year': year,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contacts(request):
    return render(request, 'contacts.html')

def login_modal(request):
    return render(request, 'login_modal.html')


@login_required
def admin_dashboard(request):
    # Общая статистика
    enterprises_count = Enterprise.objects.count()
    financial_kpis_count = FinancialKPI.objects.count()

    # Дата последнего обновления (берём из FinancialKPI.updated_at, если есть)
    last_update = FinancialKPI.objects.aggregate(
        last=Max('enterprise__updated_at')
    )['last']

    # Список предприятий с аннотациями
    enterprises = Enterprise.objects.prefetch_related('financial_kpis', 'geo_location').all()

    # Фильтрация по отрасли
    industry_filter = request.GET.get('industry')
    if industry_filter:
        enterprises = enterprises.filter(main_industry=industry_filter)

    # Фильтрация по району
    district_filter = request.GET.get('district')
    if district_filter:
        enterprises = enterprises.filter(geo_location__district=district_filter)

    # Уникальные значения для фильтров
    industries = Enterprise.objects.values_list('main_industry', flat=True).distinct()
    districts = Enterprise.objects.exclude(geo_location__district='').values_list('geo_location__district',
                                                                                  flat=True).distinct()

    context = {
        'enterprises_count': enterprises_count,
        'financial_kpis_count': financial_kpis_count,
        'last_update': last_update,
        'enterprises': enterprises,
        'industries': [i for i in industries if i],
        'districts': [d for d in districts if d],
        'selected_industry': industry_filter,
        'selected_district': district_filter,
    }
    return render(request, 'admin/dashboard.html', context)