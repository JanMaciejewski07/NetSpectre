from enum import StrEnum
import socket
import ipaddress
import datetime
from types import MappingProxyType
import ast

class ConnectionStatus(StrEnum):
    CONNECTED = "Connected"
    DECLINED = "Declined"
    TIMEOUT = "Timeout"
    ERROR = "Error"

class ConnectionResult():
    def __init__(self, status, comment=None):
        super().__setattr__('_is_frozen', False)

        self._status = ConnectionStatus(status)
        self._comment = comment
        if self._status == ConnectionStatus.CONNECTED and self._comment is not None:
                    raise ValueError("When status is Connected comment is prohibited")
        super().__setattr__('_is_frozen', True)
    def __setattr__(self, name, value):
        if getattr(self, '_is_frozen', False):
              raise AttributeError("Object is frozen, you can't modify it")
        super().__setattr__(name, value)
    @property
    def read_status(self):
          return self._status
    @property
    def read_comment(self):
          return self._comment

class TCPConnector():
      def connect_tcp(self, target_ip, target_port, timeout=3):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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

class Target():
      def __init__(self, target_ip, port_range):
            self.target_ip = ipaddress.IPv4Address(target_ip)
            self.port_range = self.get_port_range(port_range)
      def get_port_range(self, port_range):
            if isinstance(port_range, str) and port_range.strip().startswith('[') and port_range.strip().endswith(']'):
                  try:
                        port_range = ast.literal_eval(port_range)
                  except (ValueError, SyntaxError) as e:
                        raise ValueError(f"Niepoprawny format listy w stringu: {port_range} Error: {e}")
            if isinstance(port_range, (list, tuple, set)):
                  port_range = ",".join(str(p) for p in port_range)
            port_range = str(port_range).strip()
            ports = set()
            for part in port_range.split(','):
                  part = part.strip()
                  if not part:
                        continue
                  if "-" in part:
                        try:
                              start_str, end_str = part.split('-')
                              start, end = int(start_str.strip()), int(end_str.strip())
                              if end <= start:
                                    raise ValueError(f"Port Range is incorrect. Please give the range from minimum to maximum e.g 80-500")
                              if 1 <= start <= 65535 and 1 <= end <= 65535:
                                    ports.update(range(start, end+1))
                              else:
                                    raise ValueError(f"Port in range {part} are not in the range of 1-65535.")
                        except Exception as e:
                              raise ValueError(f'Error Occured: {e}')
                  else:
                        try:
                              port_num = int(part)
                              if 1 <= port_num <= 65535:
                                    ports.add(port_num)
                              else:
                                    raise ValueError(f"Port: {port_num} goes beyond the scope of 1-65535.")
                        except Exception as e:
                              raise ValueError(f"Error Occured: {e}")
            if len(ports) > 0:
                  return sorted(list(ports))
            else:
                  raise ValueError(f"None of given ports in \"{port_range}\" was correct.")

class PortScanner():
      def __init__(self, tcpconnector):
            self.connector = tcpconnector

      def scan_target(self, target):
            target_scan = {}
            time_of_start = datetime.datetime.now()
            for port in target.port_range:
                  connection = self.connector.connect_tcp(str(target.target_ip), port)
                  target_scan[port] = connection
            time_of_end = datetime.datetime.now()
            return ScanResult(target=target, results=target_scan, time_start=time_of_start, time_end=time_of_end)

class ScanResult():
      def __init__(self, target, results, time_start, time_end):
            super().__setattr__('_is_frozen', False)
            self.target = target
            self.results = MappingProxyType(dict(results))
            self.time_start = time_start
            self.time_end = time_end
            self.duration = self.calculate_duration
            super().__setattr__('_is_frozen', True)
      def __setattr__(self, name, value):
              if getattr(self, '_is_frozen', False):
                    raise AttributeError("Object is frozen, you can't modify it")
              super().__setattr__(name, value)
      @property
      def calculate_duration(self):
            return self.time_end - self.time_start

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

if __name__ == "__main__":
      target = Target('4.2.2.2', [22, 80, 443, 8080, "50-55"])
      tcpcon = MockTCPConnector()
      scan = PortScanner(tcpconnector=tcpcon)
      scan_result = scan.scan_target(target=target)
      formatted_results = '\n '.join([f"Port: {port} Status: {res.read_status} comment: {res.read_comment}" for port, res in scan_result.results.items()])
      print(f"Target: {scan_result.target.target_ip}\n"
            f"Target Port Range: {scan_result.target.port_range}\n"
            f"Started Scanning: {scan_result.time_start}\n"
            f"Ended Scanning: {scan_result.time_end}\n"
            f"Duration: {scan_result.duration}\n"
            f"Results: \n {formatted_results}")