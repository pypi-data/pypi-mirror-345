from unittest.mock import MagicMock, patch
import app  # Make sure `app.py` is accessible from your test path

@patch('app.nmap.PortScanner')
def test_scan_mocked(scanner_mock):
    # Configure the mock behavior
    scanner_instance = scanner_mock.return_value
    scanner_instance.scan.return_value = None
    scanner_instance.all_hosts.return_value = ['192.168.1.10']
    scanner_instance.__getitem__.return_value = {
        'addresses': {'mac': 'AA:BB:CC:DD:EE:FF'},
        'hostname': lambda: 'MockHost'
    }

    results = app.scan_network(test_mode=True)
    assert isinstance(results, list)
    assert results[0]['ip'] == '192.168.1.10'
    assert results[0]['mac'] == 'AA:BB:CC:DD:EE:FF'
