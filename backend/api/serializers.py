from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Estimate, EstimateLine, WorkCategory, WorkItem

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return value

    def validate_password(self, value):
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError('Пароль должен содержать хотя бы одну букву.')
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError('Пароль должен содержать хотя бы одну цифру.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TelegramAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False, default='')
    username = serializers.CharField(required=False, default='')
    photo_url = serializers.CharField(required=False, default='')
    auth_date = serializers.IntegerField()
    hash = serializers.CharField()


class WorkCategorySerializer(serializers.ModelSerializer):
    is_system = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkCategory
        fields = ['id', 'name', 'user', 'is_system']
        read_only_fields = ['user', 'is_system']


class WorkItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_system = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkItem
        fields = ['id', 'category', 'category_name', 'name', 'unit', 'avg_price', 'user', 'is_system']
        read_only_fields = ['user', 'is_system']


class EstimateLineSerializer(serializers.ModelSerializer):
    work_item_name = serializers.CharField(source='work_item.name', read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = EstimateLine
        fields = ['id', 'estimate', 'work_item', 'work_item_name', 'custom_name', 'unit', 'price', 'quantity', 'total']
        read_only_fields = ['estimate']  # estimate задаётся через serializer.save(estimate=...)


class EstimateListSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = Estimate
        fields = ['id', 'name', 'created_at', 'updated_at', 'total']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_total(self, obj):
        return sum(line.total for line in obj.lines.all())


class EstimateDetailSerializer(serializers.ModelSerializer):
    lines = EstimateLineSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Estimate
        fields = ['id', 'name', 'created_at', 'updated_at', 'lines', 'total']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_total(self, obj):
        return sum(line.total for line in obj.lines.all())
