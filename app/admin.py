from django.contrib import admin

from .models import *


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ('id', 'user', 'amount', 'date')


admin.site.register(Transaction, TransactionAdmin)


class UserEntityAdmin(admin.ModelAdmin):
    model = UserEntity
    list_display = ('id', 'first_name', 'last_name', 'email',)


admin.site.register(UserEntity, UserEntityAdmin)
