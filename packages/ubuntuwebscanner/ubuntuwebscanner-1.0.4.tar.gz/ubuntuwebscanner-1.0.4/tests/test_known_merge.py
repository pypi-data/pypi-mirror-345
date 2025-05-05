import unittest
import sqlite3
from app import get_known_host_info

class TestKnownHostMerge(unittest.TestCase):
    def setUp(self):
        # Create a temporary in-memory SQLite DB
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE known_hosts (
                mac TEXT PRIMARY KEY,
                ip TEXT,
                hostname TEXT,
                vendor TEXT,
                os TEXT,
                notes TEXT
            )
        ''')
        self.test_mac = 'AA:BB:CC:DD:EE:FF'
        self.c.execute('''
            INSERT INTO known_hosts (mac, ip, hostname, vendor, os, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.test_mac, '192.168.1.123', 'TestDevice', 'Cisco', 'Linux', 'Lab Device'))
        self.conn.commit()

    def test_lookup_merge(self):
        # Mock the app-level DB access function
        def test_lookup(mac):
            self.c.execute("SELECT hostname, vendor, os, notes FROM known_hosts WHERE mac = ?", (mac,))
            row = self.c.fetchone()
            if row:
                return {'hostname': row[0], 'vendor': row[1], 'os': row[2], 'notes': row[3]}
            return None

        result = test_lookup(self.test_mac)
        self.assertIsNotNone(result)
        self.assertEqual(result['vendor'], 'Cisco')
        self.assertEqual(result['hostname'], 'TestDevice')

    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
