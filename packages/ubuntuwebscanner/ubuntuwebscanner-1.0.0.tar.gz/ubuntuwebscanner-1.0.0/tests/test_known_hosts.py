# test_known_hosts.py

# MIT License
# (c) 2025 Timothy Johnson II

import unittest
import sqlite3
from app import get_known_host_info

class TestKnownHosts(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE known_hosts (
                mac TEXT PRIMARY KEY,
                ip TEXT,
                hostname TEXT,
                vendor TEXT,
                os TEXT,
                notes TEXT
            )
        ''')
        self.cursor.execute('''
            INSERT INTO known_hosts (mac, ip, hostname, vendor, os, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'AA:BB:CC:DD:EE:FF',
            '192.168.1.100',
            'TestHost',
            'TestVendor',
            'TestOS',
            'This is a test entry'
        ))
        self.conn.commit()

        # Monkey patch the app's DB connection
        import app
        app.get_known_host_info.__globals__['sqlite3'].connect = lambda _: self.conn

    def tearDown(self):
        self.conn.close()

    def test_known_host_lookup(self):
        result = get_known_host_info('AA:BB:CC:DD:EE:FF')
        self.assertIsNotNone(result)
        self.assertEqual(result['hostname'], 'TestHost')
        self.assertEqual(result['vendor'], 'TestVendor')
        self.assertEqual(result['os'], 'TestOS')
        self.assertEqual(result['notes'], 'This is a test entry')

    def test_unknown_host_lookup(self):
        result = get_known_host_info('00:11:22:33:44:55')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
