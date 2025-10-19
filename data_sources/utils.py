import pandas as pd
from enterprises.models import Enterprise, FinancialKPI, PropertyInfo, ProductInfo, GeoLocation
from  django.db import models

def parse_excel_file(file):
    """
    Парсит Excel-файл и возвращает отчёт об обработке.
    """
    report = {
        'success': [],
        'errors': [],
        'summary': {}
    }

    try:
        xls = pd.ExcelFile(file)
    except Exception as e:
        report['errors'].append(f"Невозможно открыть файл: {str(e)}")
        return report

    # Сопоставление названий листов с моделями
    sheet_model_map = {
        "Основная информация": ("enterprise", Enterprise),
        "Финансовые показатели": ("financial_kpi", FinancialKPI),
        "Имущество": ("property_info", PropertyInfo),
        "Продукция": ("product_info", ProductInfo),
        "Геоданные": ("geo_location", GeoLocation),
    }

    for sheet_name in xls.sheet_names:
        if sheet_name not in sheet_model_map:
            report['errors'].append(f"Пропущен неизвестный лист: {sheet_name}")
            continue

        model_type, model_class = sheet_model_map[sheet_name]
        df = pd.read_excel(xls, sheet_name=sheet_name)

        if df.empty:
            continue

        processed = 0
        errors_in_sheet = []

        for idx, row in df.iterrows():
            try:
                # Все листы должны содержать ИНН в первом столбце
                inn = str(row.iloc[0]).strip('.0').strip()
                if not inn or inn.lower() in ['nan', 'none', '']:
                    errors_in_sheet.append(f"Строка {idx+2}: отсутствует ИНН")
                    continue

                # Убедимся, что ИНН корректен (10 или 12 цифр)
                if not (inn.isdigit() and len(inn) in (10, 12)):
                    errors_in_sheet.append(f"Строка {idx+2}: некорректный ИНН '{inn}'")
                    continue

                # Обработка по типу модели
                if model_type == "enterprise":
                    # Создаём/обновляем предприятие
                    defaults = {}
                    field_names = [f.name for f in Enterprise._meta.fields if f.name != 'id']
                    for i, field_name in enumerate(field_names):
                        if i < len(row) - 1:  # row.iloc[0] — это ИНН
                            value = row.iloc[i + 1]
                            if pd.notna(value):
                                defaults[field_name] = str(value).strip() if isinstance(value, str) else value
                    enterprise, created = Enterprise.objects.update_or_create(
                        inn=inn,
                        defaults=defaults
                    )
                    action = "создано" if created else "обновлено"
                    processed += 1
                    report['success'].append(f"Предприятие {inn} — {action}")

                else:
                    # Найти предприятие по ИНН
                    try:
                        enterprise = Enterprise.objects.get(inn=inn)
                    except Enterprise.DoesNotExist:
                        errors_in_sheet.append(f"Строка {idx+2}: предприятие с ИНН {inn} не найдено в базе")
                        continue

                    # Подготовка данных для модели
                    defaults = {}
                    field_names = [f.name for f in model_class._meta.fields if f.name not in ('id', 'enterprise')]

                    for i, field_name in enumerate(field_names):
                        col_index = i + 1  # потому что 0 — ИНН
                        if col_index < len(row):
                            value = row.iloc[col_index]
                            if pd.notna(value):
                                field = model_class._meta.get_field(field_name)
                                # Преобразование типов
                                if isinstance(field, (models.DecimalField, models.FloatField)):
                                    try:
                                        defaults[field_name] = float(value)
                                    except (ValueError, TypeError):
                                        defaults[field_name] = None
                                elif isinstance(field, models.IntegerField):
                                    try:
                                        defaults[field_name] = int(float(value))
                                    except (ValueError, TypeError):
                                        defaults[field_name] = None
                                elif isinstance(field, models.BooleanField):
                                    defaults[field_name] = str(value).lower() in ('да', 'yes', 'true', '1')
                                else:
                                    defaults[field_name] = str(value).strip() if pd.notna(value) else ''

                    # Создание/обновление записи
                    if model_type == "financial_kpi":
                        year = defaults.get('year')
                        if year:
                            obj, created = FinancialKPI.objects.update_or_create(
                                enterprise=enterprise,
                                year=year,
                                defaults=defaults
                            )
                        else:
                            errors_in_sheet.append(f"Строка {idx+2}: отсутствует год")
                            continue
                    elif model_type == "geo_location":
                        obj, created = GeoLocation.objects.update_or_create(
                            enterprise=enterprise,
                            defaults=defaults
                        )
                    else:
                        # Для PropertyInfo и ProductInfo — одна запись на предприятие
                        obj, created = model_class.objects.update_or_create(
                            enterprise=enterprise,
                            defaults=defaults
                        )

                    action = "создана" if created else "обновлена"
                    processed += 1
                    report['success'].append(f"{sheet_name} для {inn} — {action}")

            except Exception as e:
                errors_in_sheet.append(f"Строка {idx+2}: ошибка — {str(e)}")

        # Итоги по листу
        report['summary'][sheet_name] = {
            'processed': processed,
            'errors': len(errors_in_sheet)
        }
        report['errors'].extend(errors_in_sheet)

    return report