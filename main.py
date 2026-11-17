import argparse
import connectors
import scanner
import models 
import reporting

class NetSpectreCLI():
    def __init__(self):
        parser = argparse.ArgumentParser(prog='NetSpectre', description="NetSpectre is a program for testing ports connection of an ip.", epilog="Made by Jan Maciejewski | BrainR00T | https://bugcrowd.com/h/BrainR00T")
        parser.add_argument("-t", "--target", required=True)
        parser.add_argument('-p', '--ports', required=True, nargs="+")
        parser.add_argument("-o", "--output", required=False)
        self.given_arguments = parser.parse_args()

def main():
    argument_parser = NetSpectreCLI()
    tcp_connector = connectors.TCPConnector()
    port_scanner = scanner.PortScanner(tcp_connector)
    target_ip = argument_parser.given_arguments.target
    target_ports = argument_parser.given_arguments.ports
    output_file = argument_parser.given_arguments.output
    target = models.Target(target_ip=target_ip, port_range=target_ports)
    scan_result = port_scanner.scan_target(target=target)
    if output_file != None:
        reporting.JSONReportWriter(scan_result, output_file).write_json()
    formatted_results = '\n '.join([f"Port: {port} Status: {res.read_status} comment: {res.read_comment}" for port, res in scan_result.results.items()])
    print(f"Target: {scan_result.target.target_ip}\n"
        f"Target Port Range: {scan_result.target.port_range}\n"
        f"Started Scanning: {scan_result.time_start}\n"
        f"Ended Scanning: {scan_result.time_end}\n"
        f"Duration: {scan_result.duration}\n"
        f"Results: \n {formatted_results}")        

if __name__ == "__main__":
    main()