import mocks
import scanner
import models
import reporting
import pytest
import json
import socket
import threading
import connectors

@pytest.fixture
def local_tcp_server():
    """Uruchamia tymczasowy serwer TCP na losowym wolnym porcie 127.0.0.1."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))  # Port 0 pozwala OS wybrać wolny port
    server.listen(1)
    port = server.getsockname()[1]

    stop_event = threading.Event()

    def handle_connections():
        server.settimeout(0.2)
        while not stop_event.is_set():
            try:
                conn, _ = server.accept()
                conn.close()
            except socket.timeout:
                continue
            except OSError:
                break

    thread = threading.Thread(target=handle_connections, daemon=True)
    thread.start()

    yield port  # Przekazujemy numer przydzielonego portu do testu

    # Sprzątanie po zakończeniu testu
    stop_event.set()
    server.close()
    thread.join()

def test_real_tcp_connection_succeeds(local_tcp_server):
    """Test integracyjny sprawdzający rzeczywiste połączenie z lokalnym serwerem TCP."""
    open_port = local_tcp_server

    # Podmień na właściwą nazwę Twojego produkcyjnego konektora TCP (np. TCPConnector)
    real_connector = connectors.TCPConnector()
    port_scanner = scanner.PortScanner(real_connector)
    target = models.Target("127.0.0.1", [open_port])

    scan_result = port_scanner.scan_target(target)

    assert scan_result.results[open_port].read_status == models.ConnectionStatus.CONNECTED

def test_scanner():
    tcpconnector = mocks.MockTCPConnector()
    portscanner = scanner.PortScanner(tcpconnector)
    target = models.Target('127.0.0.1', [22, 80, 443, 8080])
    scan_result = portscanner.scan_target(target)
    assert scan_result.results[22].read_status == models.ConnectionStatus.CONNECTED
    assert len(tcpconnector.ports_checked) == 4
    assert tcpconnector.ports_checked == [22, 80, 443, 8080]


@pytest.fixture
def scan_json_file(tmp_path):
    """Start scanning and saves temporary report"""
    output_file = tmp_path / "scan_report.json"

    # configure scanner with Mock TCP Connector
    connector = mocks.MockTCPConnector()
    target = models.Target('127.0.0.1', [22, 80, 443, 8080])
    port_scanner = scanner.PortScanner(connector)
    scan_result = port_scanner.scan_target(target)

    # Save report
    writer = reporting.JSONReportWriter(scan_result=scan_result, file=output_file)
    writer.write_json()

    return output_file


def test_json_is_valid_and_port_22_is_connected(scan_json_file):
    """Check if json data is valid and is status 'Connected' available for port 22."""
    with open(scan_json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "Results" in data
    assert isinstance(data["Results"], list)

    port_22_entry = next((item for item in data["Results"] if item["port"] == 22), None)
    assert port_22_entry is not None
    assert port_22_entry["status"] == "Connected"


def test_json_contains_all_four_simulated_ports_and_statuses(scan_json_file):
    """Check if report has all four ports with their expected statuses."""
    with open(scan_json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    actual_statuses = {item["port"]: item["status"] for item in data["Results"]}

    expected_statuses = {
        22: "Connected",
        80: "Declined",
        443: "Timeout",    
        8080: "Error",  
    }

    assert actual_statuses == expected_statuses


