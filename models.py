# imports
from enum import StrEnum
import ipaddress
import ast
from types import MappingProxyType


# Connection Statuses that can be used in ConnectionResult class, no other statuses are allowed
class ConnectionStatus(StrEnum):
    CONNECTED = "Connected"
    DECLINED = "Declined"
    TIMEOUT = "Timeout"
    ERROR = "Error"

# Results of connection to certain port, cannot be modified
class ConnectionResult():
    def __init__(self, status, comment=None):
        super().__setattr__('_is_frozen', False) # Set attribute is_frozen as false on start, if is_frozen is set to true modifying variables is forbidden

        self._status = ConnectionStatus(status) # Store status of connection
        self._comment = comment # Store comment 
        if self._status == ConnectionStatus.CONNECTED and self._comment is not None: 
                    raise ValueError("When status is Connected comment is prohibited")
        super().__setattr__('_is_frozen', True) # Set attribute is_frozen to true, modifying forbidden
    def __setattr__(self, name, value):
        if getattr(self, '_is_frozen', False): # Check if modifying is enabled
              raise AttributeError("Object is frozen, you can't modify it")
        super().__setattr__(name, value)
    @property
    def read_status(self):
          return self._status
    @property
    def read_comment(self):
          return self._comment

# Store target ip and get port range
class Target():
      def __init__(self, target_ip, port_range):
            self.target_ip = ipaddress.IPv4Address(target_ip)
            self.port_range = self.get_port_range(port_range)
      def get_port_range(self, port_range):
            if isinstance(port_range, str) and port_range.strip().startswith('[') and port_range.strip().endswith(']'): # Check if ports were given as a list looking string
                  try:
                        port_range = ast.literal_eval(port_range)
                  except (ValueError, SyntaxError) as e:
                        raise ValueError(f"Niepoprawny format listy w stringu: {port_range} Error: {e}")
            if isinstance(port_range, (list, tuple, set)): # Check if ports were given as a list, tuple or set
                  port_range = ",".join(str(p) for p in port_range)
            port_range = str(port_range).strip()
            ports = set() # Store ports as a set for auto-deleting duplicates
            for part in port_range.split(','):
                  part = part.strip()
                  if not part:
                        continue
                  if "-" in part: # Check if given ports are range e.g 80-120 ports from 80 to 120
                        try:
                              start_str, end_str = part.split('-') 
                              start, end = int(start_str.strip()), int(end_str.strip())
                              if end <= start: # Check if given range is valid
                                    raise ValueError(f"Port Range is incorrect. Please give the range from minimum to maximum e.g 80-500")
                              if 1 <= start <= 65535 and 1 <= end <= 65535: # Check if given range is within the ports number limit
                                    ports.update(range(start, end+1))
                              else:
                                    raise ValueError(f"Port in range {part} are not in the range of 1-65535.")
                        except (ValueError, TypeError, SyntaxError) as e:
                              raise ValueError(f'Error Occured: {e}')
                  else:
                        try:
                              port_num = int(part)
                              if 1 <= port_num <= 65535: # Check if port is within the ports number limit
                                    ports.add(port_num)
                              else:
                                    raise ValueError(f"Port: {port_num} goes beyond the scope of 1-65535.")
                        except (ValueError, TypeError, SyntaxError) as e:
                              raise ValueError(f"Error Occured: {e}")
            if len(ports) > 0:
                  return sorted(list(ports)) # Sort ports list
            else:
                  raise ValueError(f"None of given ports in \"{port_range}\" was correct.")

# Store results of a port scanner, cannot modify
class ScanResult():
      def __init__(self, target, results, time_start, time_end):
            super().__setattr__('_is_frozen', False) # Set attribute is_frozen as false on start, if is_frozen is set to true modifying variables is forbidden
            self.target = target
            self.results = MappingProxyType(dict(results))
            self.time_start = time_start
            self.time_end = time_end
            self.duration = self.calculate_duration
            super().__setattr__('_is_frozen', True) # Set attribute is_frozen to true, modifying forbidden
      def __setattr__(self, name, value):
              if getattr(self, '_is_frozen', False): # Check if modifying is enabled
                    raise AttributeError("Object is frozen, you can't modify it")
              super().__setattr__(name, value)
      @property
      def calculate_duration(self): # Calculate duration of scanning return in format HH:MM:SS
            return self.time_end - self.time_start