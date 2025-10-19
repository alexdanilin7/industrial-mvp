from django.db import models

# Create your models here.
class Enterprise(models.Model):
    """Основная информация о предприятии"""
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    name = models.CharField(max_length=500, verbose_name="Наименование организации")
    full_name = models.CharField(max_length=1000, blank=True, verbose_name="Полное наименование организации")
    status = models.CharField(max_length=200, blank=True, verbose_name="Статус")
    legal_address = models.TextField(blank=True, verbose_name="Юридический адрес")
    production_address = models.TextField(blank=True, verbose_name="Адрес производства")
    additional_site_address = models.TextField(blank=True, verbose_name="Адрес дополнительной площадки")

    main_industry = models.CharField(max_length=200, blank=True, verbose_name="Основная отрасль")
    main_subindustry = models.CharField(max_length=200, blank=True, verbose_name="Подотрасль (Основная)")
    main_okved = models.CharField(max_length=20, blank=True, verbose_name="Основной ОКВЭД")
    main_okved_desc = models.CharField(max_length=500, blank=True, verbose_name="Вид деятельности по основному ОКВЭД")
    production_okved = models.CharField(max_length=20, blank=True, verbose_name="Производственный ОКВЭД")

    registration_date = models.DateField(null=True, blank=True, verbose_name="Дата регистрации")
    head = models.CharField(max_length=300, blank=True, verbose_name="Руководитель")
    parent_company = models.CharField(max_length=500, blank=True, verbose_name="Головная организация")
    parent_inn = models.CharField(max_length=12, blank=True, verbose_name="ИНН головной организации")

    head_contacts = models.TextField(blank=True, verbose_name="Контактные данные руководства")
    staff_contact = models.TextField(blank=True, verbose_name="Контакт сотрудника организации")
    emergency_contact = models.TextField(blank=True, verbose_name="Контактные данные ответственного по ЧС")
    website = models.URLField(blank=True, verbose_name="Сайт")
    email = models.EmailField(blank=True, verbose_name="Электронная почта")

    support_measures = models.TextField(blank=True, verbose_name="Данные об оказанных мерах поддержки")
    special_status = models.CharField(max_length=200, blank=True, verbose_name="Наличие особого статуса")
    is_msp = models.BooleanField(default=False, verbose_name="Статус МСП")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.inn})"


class FinancialKPI(models.Model):
    """Финансово-экономические показатели по годам"""
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='financial_kpis')
    year = models.IntegerField(verbose_name="Год", choices=[(y, y) for y in range(2022, 2025)])

    # Выручка
    revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Выручка предприятия, тыс. руб.")
    # Прибыль/убыток
    net_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Чистая прибыль (убыток), тыс. руб.")

    # Численность персонала
    staff_total = models.IntegerField(null=True, blank=True, verbose_name="Среднесписочная численность персонала (всего по компании), чел")
    staff_moscow = models.IntegerField(null=True, blank=True, verbose_name="Среднесписочная численность персонала, работающего в Москве, чел")

    # Фонд оплаты труда
    payroll_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Фонд оплаты труда всех сотрудников организации, тыс. руб")
    payroll_moscow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Фонд оплаты труда сотрудников, работающих в Москве, тыс. руб")

    # Средняя зарплата
    avg_salary_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Средняя з.п. всех сотрудников организации, тыс.руб.")
    avg_salary_moscow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Средняя з.п. сотрудников, работающих в Москве, тыс.руб.")

    # Налоги в бюджет Москвы (без акцизов)
    taxes_moscow_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Налоги, уплаченные в бюджет Москвы (без акцизов), тыс.руб.")

    # Разбивка налогов
    tax_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Налог на прибыль, тыс.руб.")
    tax_property = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Налог на имущество, тыс.руб.")
    tax_land = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Налог на землю, тыс.руб.")
    tax_ndfl = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="НДФЛ, тыс.руб.")
    tax_transport = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Транспортный налог, тыс.руб.")
    tax_other = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Прочие налоги")
    tax_excise = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Акцизы, тыс. руб.")

    # Инвестиции
    investments_moscow = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Инвестиции в Мск, тыс. руб.")

    # Экспорт
    export_volume = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Объем экспорта, тыс. руб.")

    class Meta:
        unique_together = ('enterprise', 'year')
        verbose_name = "Финансовый показатель"
        verbose_name_plural = "Финансовые показатели"

    def __str__(self):
        return f"{self.enterprise.name} - {self.year}"


class PropertyInfo(models.Model):
    """Имущественно-земельный комплекс"""
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='property_info')

    # Земельный участок
    cadastral_number_zu = models.CharField(max_length=100, blank=True, verbose_name="Кадастровый номер ЗУ")
    area_zu = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Площадь ЗУ")
    permitted_use_zu = models.CharField(max_length=500, blank=True, verbose_name="Вид разрешенного использования ЗУ")
    ownership_type_zu = models.CharField(max_length=200, blank=True, verbose_name="Вид собственности ЗУ")
    owner_zu = models.CharField(max_length=500, blank=True, verbose_name="Собственник ЗУ")

    # Объект капитального строительства
    cadastral_number_oks = models.CharField(max_length=100, blank=True, verbose_name="Кадастровый номер ОКСа")
    area_oks = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Площадь ОКСов")
    permitted_use_oks = models.CharField(max_length=500, blank=True, verbose_name="Вид разрешенного использования ОКСов")
    construction_type_oks = models.CharField(max_length=500, blank=True, verbose_name="Тип строения и цель использования")
    ownership_type_oks = models.CharField(max_length=200, blank=True, verbose_name="Вид собственности ОКСов")
    owner_oks = models.CharField(max_length=500, blank=True, verbose_name="Собственник ОКСов")

    # Производственные помещения
    production_area_sqm = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Площадь производственных помещений, кв.м.")

    def __str__(self):
        return f"Имущество {self.enterprise.name}"


class ProductInfo(models.Model):
    """Информация о продукции и экспорте"""
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='product_info')

    # Продукция
    standardized_product = models.TextField(blank=True, verbose_name="Стандартизированная продукция")
    product_names = models.TextField(blank=True, verbose_name="Название (виды производимой продукции)")
    okpd2_codes = models.TextField(blank=True, verbose_name="Перечень производимой продукции по кодам ОКПД 2")
    product_types_segments = models.TextField(blank=True, verbose_name="Перечень производимой продукции по типам и сегментам")
    product_catalog = models.TextField(blank=True, verbose_name="Каталог продукции")

    # Госзаказ и экспорт
    has_gov_contract = models.BooleanField(default=False, verbose_name="Наличие госзаказа")
    capacity_utilization = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Уровень загрузки производственных мощностей")
    exports_available = models.BooleanField(default=False, verbose_name="Наличие поставок продукции на экспорт")
    export_volume_prev_year = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Объем экспорта (млн руб.) за предыдущий календарный год")
    export_countries = models.TextField(blank=True, verbose_name="Перечень государств-импортеров")

    def __str__(self):
        return f"Продукция {self.enterprise.name}"


class GeoLocation(models.Model):
    """Географические координаты и административное деление"""
    enterprise = models.OneToOneField(Enterprise, on_delete=models.CASCADE, related_name='geo_location')

    # Координаты
    lat_legal = models.FloatField(null=True, blank=True, verbose_name="Координаты юридического адреса (широта)")
    lon_legal = models.FloatField(null=True, blank=True, verbose_name="Координаты юридического адреса (долгота)")
    lat_production = models.FloatField(null=True, blank=True, verbose_name="Координаты адреса производства (широта)")
    lon_production = models.FloatField(null=True, blank=True, verbose_name="Координаты адреса производства (долгота)")
    lat_additional = models.FloatField(null=True, blank=True, verbose_name="Координаты адреса дополнительной площадки (широта)")
    lon_additional = models.FloatField(null=True, blank=True, verbose_name="Координаты адреса дополнительной площадки (долгота)")

    # Административное деление
    district = models.CharField(max_length=100, blank=True, verbose_name="Район")
    okrug = models.CharField(max_length=100, blank=True, verbose_name="Округ")

    def __str__(self):
        return f"Гео {self.enterprise.name}"