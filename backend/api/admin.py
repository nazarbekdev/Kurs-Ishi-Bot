from django.contrib import admin

from api.models import Field, CourseWork, BotUser


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(CourseWork)
class CourseWorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'field', 'topic', 'university', 'pages', 'language')


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'telegram_id', 'balance')
