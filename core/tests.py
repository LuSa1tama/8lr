# core/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CreditProduct, CreditApplication
from .forms import CreditApplicationForm

class CreditBankTests(TestCase):
    def setUp(self):
        # Создаём пользователя и кредитный продукт для всех тестов
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.product = CreditProduct.objects.create(
            name='Потребительский',
            min_amount=10000,
            max_amount=1000000,
            rate=8.9
        )

    # === Тесты моделей ===
    def test_credit_application_created_with_status_new(self):
        app = CreditApplication.objects.create(
            user=self.user,
            product=self.product,
            amount=50000,
            phone='+79991234567'
        )
        self.assertEqual(app.status, 'new')
        self.assertIsNotNone(app.created_at)
        self.assertIsNotNone(app.updated_at)

    # === Тесты форм ===
    def test_valid_credit_application_form(self):
        form_data = {
            'product': self.product.id,
            'amount': 300000,
            'phone': '+79991234567'
        }
        form = CreditApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_amount_too_low(self):
        form_data = {
            'product': self.product.id,
            'amount': 5000,  # меньше min_amount
            'phone': '+79991234567'
        }
        form = CreditApplicationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    # === Тесты представлений ===
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_apply_credit_redirects_anonymous_user(self):
        response = self.client.get(reverse('apply_credit'))
        self.assertEqual(response.status_code, 302)  # редирект на логин

    def test_apply_credit_accessible_for_logged_in_user(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('apply_credit'))
        self.assertEqual(response.status_code, 200)

    def test_submit_credit_application(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('apply_credit'), {
            'product': self.product.id,
            'amount': 200000,
            'phone': '+79991234567'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(CreditApplication.objects.count(), 1)

    # === Тесты безопасности ===
    def test_password_is_hashed(self):
        user = User.objects.create_user(username='newuser', password='mypassword123')
        self.assertNotEqual(user.password, 'mypassword123')
        self.assertTrue(user.password.startswith('pbkdf2_'))