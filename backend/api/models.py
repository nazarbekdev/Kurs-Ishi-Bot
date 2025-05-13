from django.db import models


class Field(models.Model):
    name = models.CharField(max_length=100)  # Masalan, Informatika, Iqtisod

    def __str__(self):
        return self.name


class CourseWork(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    university = models.CharField(max_length=255, blank=True)
    pages = models.IntegerField()
    language = models.CharField(max_length=20, choices=[('uz', 'O‘zbek'), ('ru', 'Rus'), ('en', 'Ingliz')])
    file = models.FileField(upload_to='courseworks/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic


class BotUser(models.Model):
    full_name = models.CharField(max_length=255)
    telegram_id = models.BigIntegerField(unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.full_name


class UserCoupon(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='coupons')
    coupon_type = models.CharField(max_length=50, choices=[
        ('chegirma', 'Chegirma'),
        ('sovga', 'Sovga')
    ])
    value = models.CharField(max_length=50)  # Masalan, "5%", "bepul_konsultatsiya"
    text = models.CharField(max_length=100)  # Foydalanuvchiga ko‘rsatiladigan matn
    expiry = models.DateTimeField()  # Kuponning tugash vaqti
    created_at = models.DateTimeField(auto_now_add=True)  # Kupon yaratilgan vaqt
    used = models.BooleanField(default=False)  # Kupon ishlatilgan yoki yo‘q

    def __str__(self):
        return f"{self.user.full_name} - {self.text}"
