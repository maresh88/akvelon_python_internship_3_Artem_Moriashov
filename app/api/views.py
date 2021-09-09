from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as drf_filter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Transaction, UserEntity

from .serializers import TransactionSerializer, UserEntitySerializer
from .utils import ParamsValidator, is_valid_date_format


class UserListAV(generics.ListAPIView):
    """List API view for UserEntity model"""
    serializer_class = UserEntitySerializer
    queryset = UserEntity.objects.all()


class UserCreateAV(generics.CreateAPIView):
    """Create API view for UserEntity model"""
    serializer_class = UserEntitySerializer


class UserDetailAV(generics.RetrieveUpdateDestroyAPIView):
    """This API view for retrieve, update and delete UserEntity object by its pk"""
    serializer_class = UserEntitySerializer
    queryset = UserEntity.objects.all()
    lookup_url_kwarg = 'pk'


class TransactionFilter(drf_filter.FilterSet):
    """Custom Filterset class for TransactionListAV view"""
    type_ta = drf_filter.CharFilter(method='filter_type_ta')
    date = drf_filter.CharFilter(field_name='date', lookup_expr='date')

    class Meta:
        model = Transaction
        fields = ['user', 'date']

    def filter_type_ta(self, queryset, name, value):
        if value == 'income':
            queryset = queryset.filter(amount__gt=0)
        elif value == 'outcome':
            queryset = queryset.filter(amount__lt=0)
        return queryset


class TransactionListAV(generics.ListAPIView):
    """List all transactions with filter methods by
        user, date, type of transaction and
        ordering by
        date or amount
    """
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    filter_backends = [filters.OrderingFilter, drf_filter.DjangoFilterBackend]
    ordering_fields = ['amount', 'date']
    filterset_class = TransactionFilter

    type_ta = openapi.Parameter('type_ta', in_=openapi.IN_QUERY, description='type of transaction: income/outcome',
                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[type_ta])
    def get(self, request, *args, **kwargs):
        date = 'date'
        params = ParamsValidator(request.query_params)
        if params.params.get(date):
            if not params.validate_values(is_valid_date_format, *(date,)):
                raise exceptions.ValidationError({'error': f'{date} parameter should be in format YYYY-MM-DD'})
        return super().get(request, *args, **kwargs)


class TransactionCreateAV(generics.CreateAPIView):
    """Create API view for Transaction model"""
    serializer_class = TransactionSerializer


class TransactionDetailAV(generics.RetrieveUpdateDestroyAPIView):
    """This API view for retrieve, update and delete Transaction object by its pk"""
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    lookup_url_kwarg = 'pk'


class UserTransactionsList(generics.ListAPIView):
    """Getting all transactions of a specific user"""
    serializer_class = TransactionSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            return UserEntity.objects.none()
        user = get_object_or_404(UserEntity, pk=self.kwargs.get('pk'))
        return Transaction.objects.filter(user=user)


class UserTransactionsByDateAV(APIView):
    """Get user transactions grouped by date field for API view.
    For filtering only date parameter is used, without time specified.
    If start and end dates are provided in query parameters, it is filtering with date range.
    """
    start = openapi.Parameter('start', in_=openapi.IN_QUERY, description='start date in format YYYY-MM-DD',
                              type=openapi.TYPE_STRING)
    end = openapi.Parameter('end', in_=openapi.IN_QUERY, description='end date in format YYYY-MM-DD',
                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[start, end])
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(UserEntity, pk=self.kwargs.get('pk'))
        query = Transaction.objects.filter(user=user)

        params = ParamsValidator(request.query_params)
        if params.params:
            start_date, end_date = ['start', 'end']
            if params.validate_values(is_valid_date_format, *[start_date, end_date]):
                query = Transaction.objects.filter(
                    user=user, date__date__range=(params.params.get(start_date), params.params.get(end_date))
                )
            else:
                return Response(
                    {
                        'error': f"\'{start_date}\' and \'{end_date}\' "
                                 "parameters should be passed both and have format YYYY-MM-DD"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        result = query.values(rdate=TruncDate('date')).annotate(sum=Sum('amount'))
        return Response(result)
