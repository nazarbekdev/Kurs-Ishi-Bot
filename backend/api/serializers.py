from rest_framework import serializers
from .models import Field, CourseWork, BotUser, UserCoupon


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


class UserCouponSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(write_only=True)  # Faqat yozish uchun

    class Meta:
        model = UserCoupon
        fields = ['id', 'user', 'coupon_type', 'value', 'text', 'expiry', 'created_at', 'used', 'telegram_id']
        read_only_fields = ['user']  # user maydoni faqat o'qish uchun

    def validate_telegram_id(self, value):
        try:
            user = BotUser.objects.get(telegram_id=value)
            return user
        except BotUser.DoesNotExist:
            raise serializers.ValidationError("Bu telegram_id bilan foydalanuvchi topilmadi")

    def create(self, validated_data):
        user = validated_data.pop('telegram_id')  # validate_telegram_id natijasidan user olamiz
        return UserCoupon.objects.create(user=user, **validated_data)
