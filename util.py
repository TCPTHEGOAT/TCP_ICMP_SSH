import subprocess
import time
import ipaddress
import json
import os
import sys
import re

paping_path = r"C:\Users\REPLACE_WITH_YOUR_WINDOWS_USERNAME\paping.exe"

if not os.path.exists(paping_path):
    print(f"\033[91mError: 'paping.exe' not found at {paping_path}. Please check the path.\033[0m")
    sys.exit(1)

RESET = "\033[0m"
TEXT_COLOR = "\033[97m"
IP_COLOR = "\033[1;92m"
TIME_COLOR = "\033[1;93m"
PROTOCOL_COLOR = "\033[1;92m"
PORT_COLOR = "\033[1;92m"
ISP_COLOR = "\033[0;90m"
ERROR_COLOR = "\033[91m"

def get_isp(ip):
    try:
        response = subprocess.check_output(["curl", "-s", f"http://ip-api.com/json/{ip}"], encoding='utf-8')
        data = json.loads(response)
        return data.get('isp', 'Unknown')
    except Exception as e:
        print(f"{ERROR_COLOR}Error retrieving ISP: {e}{RESET}")
        return "Unknown"

def parse_paping_output(line, isp):
    match = re.search(r"Connected to ([\d\.]+): time=([\d\.]+)ms protocol=([A-Z]+) port=(\d+)", line)
    if match:
        ip_part, time_part, protocol_part, port_part = match.groups()
        print(f"Connected to {IP_COLOR}{ip_part}{TEXT_COLOR} : time={TIME_COLOR}{time_part}ms{TEXT_COLOR} protocol={PROTOCOL_COLOR}{protocol_part}{TEXT_COLOR} port={PORT_COLOR}{port_part}{TEXT_COLOR} [ISP: {ISP_COLOR}{isp}{TEXT_COLOR}]{RESET}")
    elif "Connection timed out" in line:
        print(f"{ERROR_COLOR}{line}{RESET}")
    else:
        print(f"{ERROR_COLOR}Please Wait: {line}{RESET}")

def custom_tcp_ping(ip, port=80):
    try:
        command = [paping_path, "-p", str(port), ip]
        isp = get_isp(ip)
        print(f"{TEXT_COLOR}Target: {IP_COLOR}{ip}{TEXT_COLOR} (ISP: {ISP_COLOR}{isp}{TEXT_COLOR}){RESET}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            try:
                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break  
                if output_line:
                    parse_paping_output(output_line.strip(), isp)
            except KeyboardInterrupt:
                print(f"\n{ERROR_COLOR}Ping stopped.{RESET}")
                process.terminate()
                break
            except Exception as e:
                print(f"{ERROR_COLOR}An error occurred: {e}{RESET}")
            time.sleep(1)
    except Exception as e:
        print(f"{ERROR_COLOR}An error occurred: {e}{RESET}")

def icmp_ping(ip):
    try:
        command = ["ping", "-t", ip]
        subprocess.run(command)
    except KeyboardInterrupt:
        print(f"\n{ERROR_COLOR}Ping stopped.{RESET}")

def ssh_connect(host, port, username):
    try:
        command = ["ssh", f"{username}@{host}", "-p", str(port)]
        subprocess.run(command)
    except Exception as e:
        print(f"{ERROR_COLOR}SSH connection failed: {e}{RESET}")

def main():
    try:
        print(f"{TEXT_COLOR}Network Utility Tool{RESET}")
        print("---------------------")
        ssh_choice = input("Do you want to connect via SSH? (y/n): ").strip().lower()
        if ssh_choice == 'y':
            host = input("Enter SSH host: ").strip()
            port = input("Enter SSH port (default 22): ").strip()
            port = int(port) if port.isdigit() else 22
            username = input("Enter SSH username: ").strip()
            ssh_connect(host, port, username)
            return
        
        print("Select an option:")
        print("1. ICMP Ping (-t)")
        print("2. TCP Ping (paping)")
        choice = input("Enter your choice (1/2): ").strip()
        
        while True:
            ip = input("Enter the IP address to ping: ")
            try:
                ipaddress.ip_address(ip)
                break
            except ValueError:
                print(f"{ERROR_COLOR}Invalid IP address. Please try again.{RESET}")
        
        if choice == '1':
            icmp_ping(ip)
        elif choice == '2':
            port = input("Enter the port number: ")
            while True:
                if port:
                    try:
                        port = int(port)
                        if port < 1 or port > 65535:
                            raise ValueError
                        break
                    except ValueError:
                        print(f"{ERROR_COLOR}Invalid port number. Please enter a value between 1 and 65535.{RESET}")
                else:
                    port = 80
                    break
            custom_tcp_ping(ip, port)
        else:
            print(f"{ERROR_COLOR}Invalid choice. Exiting.{RESET}")
            sys.exit(1)
    except Exception as e:
        print(f"{ERROR_COLOR}An error occurred: {e}{RESET}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{ERROR_COLOR}An error occurred: {e}{RESET}")
        input("Press Enter to exit...")
