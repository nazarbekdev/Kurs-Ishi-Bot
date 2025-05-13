import datetime
from django.utils import timezone
from rest_framework import viewsets, generics
from .models import Field, CourseWork, BotUser, UserCoupon
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .serializers import FieldSerializer, CourseWorkSerializer, UserSerializer, UserCouponSerializer
from config.openai_client import generate_coursework
from config.docx_generator import create_coursework_docx


class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


class CourseWorkViewSet(viewsets.ModelViewSet):
    queryset = CourseWork.objects.all()
    serializer_class = CourseWorkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Kurs ishini generatsiya qilish
            field_id = serializer.validated_data["field"].id
            field_name = Field.objects.get(id=field_id).name
            topic = serializer.validated_data["topic"]
            university = serializer.validated_data["university"]
            pages = serializer.validated_data["pages"]
            language = serializer.validated_data["language"]

            # OpenAI orqali matn generatsiyasi
            content = generate_coursework(field_name, topic, university, pages, language)

            # DOCX fayl yaratish
            file_path = create_coursework_docx(content, topic)

            # Modelni saqlash
            coursework = serializer.save(file=file_path)
            return Response(self.get_serializer(coursework).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateAPIView(generics.CreateAPIView):
    queryset = BotUser.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = BotUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'telegram_id'


class UserBalanceUpdateAPIView(generics.UpdateAPIView):
    queryset = BotUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'telegram_id'
    permission_classes = []

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # telegram_id bo‘yicha foydalanuvchini topamiz
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "new_balance": serializer.data['balance']}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Kuponlarni ro'yxatlash va olish (GET)
class UserCouponList(generics.ListAPIView):
    serializer_class = UserCouponSerializer
    permission_classes = []

    def get_queryset(self):
        telegram_id = self.request.query_params.get('telegram_id', None)
        if telegram_id:
            try:
                user = BotUser.objects.get(telegram_id=telegram_id)
                return UserCoupon.objects.filter(user=user)
            except BotUser.DoesNotExist:
                return UserCoupon.objects.none()
        return UserCoupon.objects.none()


# Kupon yaratish (POST)
class UserCouponCreate(generics.CreateAPIView):
    serializer_class = UserCouponSerializer
    permission_classes = []

    def perform_create(self, serializer):
        telegram_id = self.request.data.get('telegram_id')
        try:
            user = BotUser.objects.get(telegram_id=telegram_id)
        except BotUser.DoesNotExist:
            raise serializers.ValidationError({"telegram_id": "Foydalanuvchi topilmadi"})

        # Bugungi kunda kuponlar sonini tekshirish
        today = timezone.now().date()
        coupon_count_today = UserCoupon.objects.filter(
            user=user,
            created_at__date=today
        ).count()

        if coupon_count_today > 0:
            existing_coupon = UserCoupon.objects.filter(
                user=user,
                created_at__date=today
            ).order_by('-created_at').first()
            # Expiry vaqtini Asia/Tashkent ga moslashtiramiz
            expiry_local = timezone.localtime(existing_coupon.expiry)  # Asia/Tashkent ga o'tkazamiz
            expiry_time = expiry_local.strftime('%H:%M:%S %Y-%m-%d')
            raise serializers.ValidationError({
                "error": "Siz bugun allaqachon kupon oldingiz!",
                "existing_coupon": {
                    "text": existing_coupon.text,
                    "expiry": expiry_time
                }
            })

        serializer.save()


# Kuponni ko'rish, yangilash yoki o'chirish (GET, PUT, DELETE)
class UserCouponDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserCouponSerializer
    permission_classes = []

    def get_queryset(self):
        telegram_id = self.request.query_params.get('telegram_id', None)
        if telegram_id:
            try:
                user = BotUser.objects.get(telegram_id=telegram_id)
                return UserCoupon.objects.filter(user=user)
            except BotUser.DoesNotExist:
                return UserCoupon.objects.none()
        return UserCoupon.objects.none()
