from django.db import models


class UserEntity(models.Model):
    """User agent model"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = 'UserEntities'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Transaction(models.Model):
    """Income/Outcome transactions with reference to UserEntity model"""
    user = models.ForeignKey(UserEntity, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='sum of transaction')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.id} - {self.amount}'
