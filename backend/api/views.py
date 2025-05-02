from rest_framework import viewsets, generics
from .models import Field, CourseWork, BotUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import FieldSerializer, CourseWorkSerializer, UserSerializer
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
