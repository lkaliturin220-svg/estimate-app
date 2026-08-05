from django.core.management.base import BaseCommand

from api.models import WorkItem


class Command(BaseCommand):
    help = 'Парсит цены из внешних источников и обновляет avg_price для WorkItem (заглушка)'

    def handle(self, *args, **options):
        self.stdout.write('Парсинг цен запущен...')

        updated = 0
        for item in WorkItem.objects.all():
            pass

        self.stdout.write(self.style.SUCCESS(f'Готово. Обновлено записей: {updated}'))
