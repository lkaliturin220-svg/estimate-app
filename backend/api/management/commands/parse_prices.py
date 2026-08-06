from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import WorkItem

# Market prices (updated periodically from open sources)
# In production, replace with actual web scraping
MARKET_PRICES = {
    # Отделочные работы
    'Штукатурка стен': 380,
    'Шпаклёвка стен': 220,
    'Покраска стен': 200,
    'Поклейка обоев': 280,
    'Укладка плитки (пол)': 850,
    'Укладка плитки (стены)': 950,
    'Грунтовка стен': 110,
    'Монтаж гипсокартона': 400,
    'Финишная шпаклёвка': 180,
    'Декоративная штукатурка': 650,
    # Электромонтажные работы
    'Прокладка кабеля': 130,
    'Установка розетки': 320,
    'Установка выключателя': 270,
    'Сборка электрощита': 3800,
    'Замена проводки': 280,
    'Монтаж светильника': 450,
    'Установка тёплого пола': 550,
    # Сантехнические работы
    'Прокладка трубы (вода)': 420,
    'Установка смесителя': 850,
    'Установка унитаза': 2600,
    'Установка раковины': 1600,
    'Монтаж радиатора': 2200,
    'Установка душевой кабины': 4500,
    'Установка бойлера': 3000,
    # Общестроительные работы
    'Кирпичная кладка': 1200,
    'Бетонные работы (опалубка)': 900,
    'Монтаж кровли': 750,
    'Утепление фасада': 600,
    'Гидроизоляция': 350,
    # Окна/двери
    'Установка окна ПВХ': 2500,
    'Установка двери входной': 3500,
    'Установка двери межкомнатной': 1800,
    'Монтаж откосов': 400,
    'Установка москитной сетки': 200,
    # Демонтаж
    'Демонтаж перегородок': 250,
    'Демонтаж плитки': 200,
    'Демонтаж сантехники': 500,
    'Демонтаж напольных покрытий': 150,
    'Вывоз мусора': 600,
}


class Command(BaseCommand):
    help = 'Обновляет avg_price из справочника рыночных цен'

    def handle(self, *args, **options):
        updated = 0
        skipped = 0
        
        for name, price in MARKET_PRICES.items():
            try:
                item = WorkItem.objects.get(name=name)
                old_price = item.avg_price
                item.avg_price = price
                item.save(update_fields=['avg_price'])
                self.stdout.write(f'  {name}: {old_price} → {price} ₽')
                updated += 1
            except WorkItem.DoesNotExist:
                self.stdout.write(f'  ⚠ {name}: не найден в БД')
                skipped += 1
            except WorkItem.MultipleObjectsReturned:
                items = WorkItem.objects.filter(name=name)
                for item in items:
                    item.avg_price = price
                    item.save(update_fields=['avg_price'])
                self.stdout.write(f'  {name}: обновлено {items.count()} записей → {price} ₽')
                updated += items.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'Готово. Обновлено: {updated}, пропущено: {skipped}'
        ))
