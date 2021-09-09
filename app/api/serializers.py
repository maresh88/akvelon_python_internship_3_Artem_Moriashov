from rest_framework import serializers

from ..models import Transaction, UserEntity


class UserEntitySerializer(serializers.ModelSerializer):
    """Serializer for UserEntity model"""

    class Meta:
        model = UserEntity
        fields = ('id', 'first_name', 'last_name', 'email',)


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""

    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'date', 'user',)
