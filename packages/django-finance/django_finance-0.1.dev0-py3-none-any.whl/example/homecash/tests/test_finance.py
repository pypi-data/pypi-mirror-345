
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from finance.__version__ import __version__


class FinanceTest(TestCase):
    fixtures = [settings.BASE_DIR / 'fixtures/testdata']

    def setUp(self):
        self.admin = User.objects.get(username='admin')
        self.client.force_login(self.admin)
