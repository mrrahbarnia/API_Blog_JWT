"""
Tests for custom django commands.
"""
from unittest.mock import patch

from django.test import SimpleTestCase
from django.core.management import call_command
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2Error


@patch('core.management.commands.wait_for_db.Command.check')
class WaitForDbCommandTests(SimpleTestCase):
    """Test Commands for wait for db command."""

    def test_wait_for_db_when_db_ready(self, patched_check):
        """Test waiting for db if db is ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting OperationalError."""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
