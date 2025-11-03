import unittest

import sqlite3
import json


from process_emails_and_apply_actions import (
    filter_emails, query_builder_generator, process_action_and_form_body, batch_process
)

class TestProcessEmailsAndApplyActionsUnit(unittest.TestCase):
    """Simple unit tests for individual functions."""

    def test_query_builder_generator_basic(self):
        rules = {
            'rules': {
                'rules_array': [
                    {'field': 'from', 'predicate': 'contains', 'value': 'test@example.com'},
                    {'field': 'subject', 'predicate': 'contains', 'value': 'Newsletter'}
                ],
                'collection_rule': 'all'  # AND
            }
        }
        expected_query = """SELECT * FROM emails WHERE sender LIKE '%test@example.com%' AND subject LIKE '%Newsletter%'"""
        result = query_builder_generator(rules)
        self.assertEqual(result, expected_query)

    def test_query_builder_generator_or(self):
        rules = {
            'rules': {
                'rules_array': [
                    {'field': 'subject', 'predicate': 'contains', 'value': 'Promo'}
                ],
                'collection_rule': 'any'  # OR (but single rule, same as AND)
            }
        }
        expected_query = "SELECT * FROM emails WHERE subject LIKE '%Promo%'"
        result = query_builder_generator(rules)
        self.assertEqual(result, expected_query)

    def test_query_builder_generator_date(self):
        rules = {
            'rules': {
                'rules_array': [
                    {'field': 'date_received', 'predicate': 'less_than', 'value': '3 days'}
                ],
                'collection_rule': 'all'
            }
        }
        expected_query = "SELECT * FROM emails WHERE date_received >= datetime('now', '-3 days')"
        result = query_builder_generator(rules)
        self.assertEqual(result, expected_query)

    def test_process_action_and_form_body_read(self):
        body = {'ids': [], 'addLabelIds': [], 'removeLabelIds': []}
        action = {'action_name': 'mark_as_read'}
        process_action_and_form_body(action, body)
        self.assertIn('UNREAD', body['removeLabelIds'])

    def test_process_action_and_form_body_label(self):
        body = {'ids': [], 'addLabelIds': [], 'removeLabelIds': []}
        action = {'action_name': 'move_message', 'to_mailbox': 'Archive'}
        process_action_and_form_body(action, body)
        self.assertIn('Archive', body['addLabelIds'])

if __name__ == '__main__':
    unittest.main()
