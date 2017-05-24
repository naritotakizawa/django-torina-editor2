"""テストを行うモジュール."""
from django.test import TestCase
from django.urls import reverse


class TestViews(TestCase):
    """Viewのテストクラス."""

    def test_home_get(self):
        """ / アクセスのテスト"""
        response = self.client.get(reverse('dteditor2:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'django-torina-editor2')