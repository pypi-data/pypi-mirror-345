from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .functions.views import FunctionMetadataView, FunctionAPIView
from .views import MyTokenObtainPairView, HelloWorldView, run_task
from .views import DynamicAPIView

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # دریافت توکن
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # تازه‌سازی توکن
    path('hello/', HelloWorldView.as_view(), name='hello_world'),  # مسیر API جدید
    path('run_task/<int:task_id>/', run_task, name='run_task'),  # مسیر API جدید

    # توابع API
    path('functions/', FunctionMetadataView.as_view(), name='functions-list'),
    path('functions/<str:function_name>/', FunctionAPIView.as_view(), name='call-function'),
    path('functions/<str:function_name>/meta/', FunctionMetadataView.as_view(), name='function-meta'),

    path('<str:model>/', DynamicAPIView.as_view(), name='dynamic-api-list'),
    path('<str:model>/<int:pk>/', DynamicAPIView.as_view(), name='dynamic-api-detail'),

]
