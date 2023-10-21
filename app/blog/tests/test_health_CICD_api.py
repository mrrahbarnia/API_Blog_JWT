"""
Test for checking whether the CICD
instruction works correctly or not.
"""
from django.test import SimpleTestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


HEALTH_CHECK_CICD_URL = reverse('CICD-healthy')


class Test(SimpleTestCase):
    """Test the healthy of the CICD
    instruction for the entire project."""
    def setUp(self):
        self.client = APIClient()

    def test_cicd_health_check(self):

        res = self.client.get(HEALTH_CHECK_CICD_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
