import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import *


class TestUserEntity(APITestCase):

    def setUp(self):
        self.user = UserEntity.objects.create(first_name='test',
                                              last_name='test',
                                              email='test@test.com')

    def test_user_creation(self):
        data = {
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'email': 'test2@test.com',
        }
        response = self.client.post(reverse('user-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserEntity.objects.count(), 2)
        self.assertEqual(UserEntity.objects.get(email='test2@test.com').first_name, 'test_name')

    def test_user_list(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail(self):
        response = self.client.get(reverse('user-detail', args=(self.user.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTransactions(APITestCase):

    def setUp(self):
        self.date_today = datetime.date.today().strftime('%Y-%m-%d')
        self.user = UserEntity.objects.create(first_name='test',
                                              last_name='test',
                                              email='test@test.com')
        self.transaction = Transaction.objects.create(user=self.user,
                                                      amount='9.99',
                                                      date=datetime.datetime.now())

    def test_transaction_create(self):
        data = {
            'user': self.user.id,
            'amount': '9.99',
            'date': datetime.datetime.now()
        }
        response = self.client.post(reverse('transaction-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

    def test_transaction_detail(self):
        response = self.client.get(reverse('transaction-detail', args=(self.transaction.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_transactions(self):
        response = self.client.get(reverse('user-transactions', args=(self.user.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_transactions_by_date_no_params(self):
        Transaction.objects.create(user=self.user,
                                   amount='0.01',
                                   date=datetime.datetime.now())
        response = self.client.get(reverse('user-transactions-by-date', args=(self.user.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0], {'rdate': self.date_today, 'sum': 10.0})

    def test_user_transactions_by_date_with_params(self):
        end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('user-transactions-by-date', args=(self.user.id,)),
            **{'QUERY_STRING': f'start={self.date_today}&end={end_date}'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0], {'rdate': self.date_today, 'sum': 9.99})

    def test_user_transactions_by_date_with_invalid_date_params(self):
        """Passing invalid date 2021-14-01"""
        response = self.client.get(
            reverse('user-transactions-by-date', args=(self.user.id,)),
            **{'QUERY_STRING': f'start={self.date_today}&end=2021-14-01'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_of_transactions_with_params(self):
        Transaction.objects.create(user=self.user,
                                   amount='10.0',
                                   date=datetime.datetime.now())
        response = self.client.get(
            reverse('transaction-list'),
            **{'QUERY_STRING': f'user={self.user.id}&type_ta=income&date={self.date_today}&ordering=amount'}
        )
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_of_transactions_with_invalid_date_param(self):

        response = self.client.get(
            reverse('transaction-list'),
            **{'QUERY_STRING': f'date=2021-14-01'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_of_transactions_filtering_by_type(self):
        Transaction.objects.create(user=self.user,
                                   amount='-10.0',
                                   date=datetime.datetime.now())
        response = self.client.get(
            reverse('transaction-list'),
            **{'QUERY_STRING': f'user={self.user.id}&type_ta=outcome'}
        )
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['amount'], '-10.00')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
