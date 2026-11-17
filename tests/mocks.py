# imports
from models import ConnectionResult, ConnectionStatus

# Testing class, Mock TCP Connector
class MockTCPConnector():
      def __init__(self):
            self.ports_checked = []
      def connect_tcp(self, target_ip, target_port, timeout=3):
            self.ports_checked.append(target_port)
            if target_port == 22:
                  return ConnectionResult(ConnectionStatus.CONNECTED, None)
            elif target_port == 443:
                  return ConnectionResult(ConnectionStatus.TIMEOUT, "Timeout")
            elif target_port == 80:
                  return ConnectionResult(ConnectionStatus.DECLINED, "Connection Declined")
            else:
                  return ConnectionResult(ConnectionStatus.ERROR, "Test Error")    