# imports
import json

# Write results of scanning to json file
class JSONReportWriter():
      def __init__(self, scan_result, file):
            self.scan_result = scan_result
            self.file = file
      def write_json(self): # Write scan result to JSON file
            formatted_results = [
                  {"port": port, "status": res.read_status, "comment": res.read_comment}
                  for port, res in self.scan_result.results.items()
            ]
            data = {
                  "TargetIp": str(self.scan_result.target.target_ip),
                  "Target Port Range": self.scan_result.target.port_range,
                  "Started Scanning": str(self.scan_result.time_start),
                  "Ended Scanning": str(self.scan_result.time_end),
                  "Duration": str(self.scan_result.duration),
                  "Results": formatted_results

            }
            with open(f'{self.file}', 'w', encoding='utf-8') as f:
                  json.dump(data, f, ensure_ascii=False, indent=4)
