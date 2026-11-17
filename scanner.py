# imports
import datetime
from models import ScanResult

# Scan all ports of target
class PortScanner():
      def __init__(self, tcpconnector):
            self.connector = tcpconnector

      def scan_target(self, target):
            target_scan = {} # Set result as a dict
            time_of_start = datetime.datetime.now() # Get starting time of scanning
            for port in target.port_range:
                  connection = self.connector.connect_tcp(str(target.target_ip), port)
                  target_scan[port] = connection # Write result of scanning the port into dict in format {port:result} e.g 80:ConnectionResult Class (You can read status and comment from there)
            time_of_end = datetime.datetime.now()
            return ScanResult(target=target, results=target_scan, time_start=time_of_start, time_end=time_of_end) # Return result of scanning all ports

