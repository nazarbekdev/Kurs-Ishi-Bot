from rest_framework import serializers
from .models import Field, CourseWork, BotUser


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['id', 'name']


class CourseWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseWork
        fields = ['id', 'field', 'topic', 'university', 'pages', 'language', 'file']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = ['id', 'full_name', 'telegram_id', 'balance']
