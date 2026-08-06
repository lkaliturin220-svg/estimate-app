import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Estimate, EstimateLine, WorkCategory, WorkItem
from .serializers import (
    EstimateDetailSerializer,
    EstimateLineSerializer,
    EstimateListSerializer,
    LoginSerializer,
    RegisterSerializer,
    TelegramAuthSerializer,
    WorkCategorySerializer,
    WorkItemSerializer,
)

User = get_user_model()


def _user_response(user):
    return Response({
        'id': user.id,
        'username': user.username,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    login(request, user)
    request.session.save()  # принудительно сохраняем сессию
    return _user_response(user)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(
        request,
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    if user is None:
        return Response({'error': 'Неверное имя пользователя или пароль.'}, status=status.HTTP_401_UNAUTHORIZED)
    login(request, user)
    request.session.save()  # принудительно сохраняем сессию
    return _user_response(user)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'detail': 'Вы вышли из системы.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth_view(request):
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return Response({'error': 'Telegram бот не настроен.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = TelegramAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    received_hash = data.pop('hash')

    secret_key = hashlib.sha256(token.encode()).digest()
    sorted_items = sorted(data.items())
    check_string = '\n'.join(f'{k}={v}' for k, v in sorted_items)
    computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if computed_hash != received_hash:
        return Response({'error': 'Неверная подпись Telegram.'}, status=status.HTTP_403_FORBIDDEN)

    telegram_id = data['id']
    username = data.get('username', '') or f'tg_{telegram_id}'

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'first_name': data.get('first_name', ''), 'last_name': data.get('last_name', '')},
    )
    login(request, user)
    return _user_response(user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return _user_response(request.user)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def categories_view(request):
    if request.method == 'GET':
        categories = WorkCategory.objects.filter(
            models.Q(user__isnull=True) | models.Q(user=request.user)
        ).order_by('-user', 'name')
        serializer = WorkCategorySerializer(categories, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = WorkCategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def work_items_view(request):
    if request.method == 'GET':
        category_id = request.query_params.get('category')
        queryset = WorkItem.objects.filter(
            models.Q(user__isnull=True) | models.Q(user=request.user)
        ).order_by('-user', 'name')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        serializer = WorkItemSerializer(queryset, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = WorkItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def estimates_view(request):
    if request.method == 'GET':
        estimates = Estimate.objects.filter(user=request.user)
        serializer = EstimateListSerializer(estimates, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = EstimateListSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def estimate_detail_view(request, pk):
    try:
        estimate = Estimate.objects.prefetch_related('lines__work_item').get(pk=pk, user=request.user)
    except Estimate.DoesNotExist:
        return Response({'error': 'Смета не найдена.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        estimate.delete()
        return Response({'detail': 'Смета удалена.'})
    
    serializer = EstimateDetailSerializer(estimate)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def estimate_duplicate_view(request, pk):
    try:
        src = Estimate.objects.prefetch_related('lines__work_item').get(pk=pk, user=request.user)
    except Estimate.DoesNotExist:
        return Response({'error': 'Смета не найдена.'}, status=status.HTTP_404_NOT_FOUND)
    
    new_est = Estimate.objects.create(
        user=request.user,
        name=f'{src.name} (копия)'
    )
    for line in src.lines.all():
        EstimateLine.objects.create(
            estimate=new_est,
            work_item=line.work_item,
            custom_name=line.custom_name,
            unit=line.unit,
            price=line.price,
            quantity=line.quantity,
        )
    return Response(EstimateListSerializer(new_est).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def estimate_lines_view(request, estimate_pk):
    try:
        estimate = Estimate.objects.get(pk=estimate_pk, user=request.user)
    except Estimate.DoesNotExist:
        return Response({'error': 'Смета не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = EstimateLineSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save(estimate=estimate)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def estimate_line_detail_view(request, estimate_pk, line_pk):
    try:
        line = EstimateLine.objects.get(pk=line_pk, estimate__pk=estimate_pk, estimate__user=request.user)
    except EstimateLine.DoesNotExist:
        return Response({'error': 'Строка не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        line.delete()
        return Response({'detail': 'Строка удалена.'})

    if request.method == 'PATCH':
        serializer = EstimateLineSerializer(line, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def estimate_share_view(request, pk):
    from .models import SharedLink
    try:
        estimate = Estimate.objects.get(pk=pk, user=request.user)
    except Estimate.DoesNotExist:
        return Response({'error': 'Смета не найдена.'}, status=status.HTTP_404_NOT_FOUND)
    
    link, _ = SharedLink.objects.get_or_create(estimate=estimate)
    return Response({'url': f'https://estimate.kiwiai.ru/share/{link.token}/'})


@api_view(['GET'])
@permission_classes([AllowAny])
def shared_estimate_view(request, token):
    from .models import SharedLink
    from django.shortcuts import render
    try:
        link = SharedLink.objects.select_related('estimate').get(token=token)
    except SharedLink.DoesNotExist:
        return render(request, 'share_estimate.html', {'error': 'Ссылка недействительна.', 'estimate': None, 'lines': [], 'total': 0}, status=404)
    
    if link.expires_at and link.expires_at < timezone.now():
        return render(request, 'share_estimate.html', {'error': 'Срок действия ссылки истёк.', 'estimate': None, 'lines': [], 'total': 0}, status=410)
    
    lines = link.estimate.lines.select_related('work_item').all()
    lines_data = []
    total = 0
    for line in lines:
        line_total = line.total
        total += line_total
        lines_data.append({
            'display_name': line.custom_name or (line.work_item.name if line.work_item else f'Строка {line.id}'),
            'unit': line.unit,
            'price': line.price,
            'quantity': line.quantity,
            'total': line_total,
        })
    
    return render(request, 'share_estimate.html', {
        'estimate': link.estimate,
        'lines': lines_data,
        'total': total,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request):
    return Response({'detail': 'CSRF cookie set'})
