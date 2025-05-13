from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldViewSet, CourseWorkViewSet, UserCreateAPIView, UserRetrieveAPIView, UserBalanceUpdateAPIView, \
    UserCouponCreate, UserCouponDetail, UserCouponList

router = DefaultRouter()
router.register(r'fields', FieldViewSet)
router.register(r'courseworks', CourseWorkViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', UserCreateAPIView.as_view(), name='user-create'),
    path('get/<int:telegram_id>/', UserRetrieveAPIView.as_view(), name='user-retrieve'),
    path('update/<int:telegram_id>/', UserBalanceUpdateAPIView.as_view(), name='user-balance-update'),
    path('user-coupons/', UserCouponList.as_view(), name='user-coupon-list'),
    path('user-coupons/create/', UserCouponCreate.as_view(), name='user-coupon-create'),
    path('user-coupons/<int:pk>/', UserCouponDetail.as_view(), name='user-coupon-detail'),
]
