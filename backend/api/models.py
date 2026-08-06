import secrets
from django.conf import settings
from django.db import models


class WorkCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='work_categories',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Категория работ'
        verbose_name_plural = 'Категории работ'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_system(self):
        return self.user is None


class WorkItem(models.Model):
    category = models.ForeignKey(
        WorkCategory,
        on_delete=models.CASCADE,
        related_name='work_items',
        verbose_name='Категория',
    )
    name = models.CharField(max_length=255, verbose_name='Название')
    unit = models.CharField(max_length=50, verbose_name='Единица измерения')
    avg_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='Средняя цена'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='work_items',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Вид работ'
        verbose_name_plural = 'Виды работ'
        ordering = ['category', 'name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name

    @property
    def is_system(self):
        return self.user is None


class Estimate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='estimates',
        verbose_name='Пользователь',
    )
    name = models.CharField(max_length=255, verbose_name='Название сметы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        verbose_name = 'Смета'
        verbose_name_plural = 'Сметы'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class EstimateLine(models.Model):
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Смета',
    )
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estimate_lines',
        verbose_name='Вид работ',
    )
    custom_name = models.CharField(
        max_length=255, blank=True, default='', verbose_name='Название'
    )
    unit = models.CharField(max_length=50, verbose_name='Единица измерения')
    price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Цена за единицу'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=1, verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Строка сметы'
        verbose_name_plural = 'Строки сметы'
        ordering = ['id']

    def __str__(self):
        return self.custom_name or (self.work_item.name if self.work_item else f'Строка {self.id}')

    @property
    def total(self):
        return self.price * self.quantity


class SharedLink(models.Model):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name='shares')
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Публичная ссылка'
        verbose_name_plural = 'Публичные ссылки'
