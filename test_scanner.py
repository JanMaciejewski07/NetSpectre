import classes

def test_scanner():
    tcpconnector = classes.MockTCPConnector()
    portscanner = classes.PortScanner(tcpconnector)
    target = classes.Target('127.0.0.1', [22, 80, 443, 8080])
    scan_result = portscanner.scan_target(target)
    assert scan_result.results[22].read_status == classes.ConnectionStatus.CONNECTED
    assert len(tcpconnector.ports_checked) == 4
    assert tcpconnector.ports_checked == [22, 80, 443, 8080]