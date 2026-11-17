# imports
import socket
from models import ConnectionResult, ConnectionStatus

# Connect by TCP to target ip on certain port, return status with ConnectionResult class
class TCPConnector():
      def connect_tcp(self, target_ip, target_port, timeout=3):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # Connect by TCP
                  s.settimeout(timeout)
                  try:
                        s.connect((target_ip, target_port))
                        return ConnectionResult(ConnectionStatus.CONNECTED, None)
                  except TimeoutError as e:
                        return ConnectionResult(ConnectionStatus.TIMEOUT, str(e))
                  except ConnectionRefusedError as e:
                        return ConnectionResult(ConnectionStatus.DECLINED, str(e))
                  except OSError as e:
                        return ConnectionResult(ConnectionStatus.ERROR, str(e))     