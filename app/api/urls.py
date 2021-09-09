from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import *

schema_view = get_schema_view(
   openapi.Info(
      title="APP",
      default_version='v1',
      description="the description",
      terms_of_service="https://www.myapp.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # UserEntity model endpoints
    path('users/create/', UserCreateAV.as_view(), name='user-create'),
    path('users/list/', UserListAV.as_view(), name='user-list'),
    path('users/detail/<int:pk>/', UserDetailAV.as_view(), name='user-detail'),
    # Transaction models endpoints
    path('transaction/create/', TransactionCreateAV.as_view(), name='transaction-create'),
    path('transaction/detail/<int:pk>/', TransactionDetailAV.as_view(), name='transaction-detail'),
    path('transaction/<int:pk>/list/', UserTransactionsList.as_view(), name='user-transactions'),
    path('transaction/<int:pk>/list-by-date/', UserTransactionsByDateAV.as_view(), name='user-transactions-by-date'),
    path('transaction/list/', TransactionListAV.as_view(), name='transaction-list'),
    # Swagger endpoints
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
