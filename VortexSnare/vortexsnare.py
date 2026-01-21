#!/usr/bin/env python3
"""
VortexSnare - CLI-Based SSH & FTP Honeypot
A sophisticated decoy system to trap, log, and analyze brute-force attacks.
"""

import socket
import threading
import datetime
import json
import csv
import os
import sys
import argparse
import time
from typing import Dict, List, Tuple
from collections import defaultdict

# Fix agar warna ANSI muncul di Terminal Windows/VS Code
os.system('')

# ANSI Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class VortexSnare:
    """Main honeypot class for SSH and FTP services"""
    
    def __init__(self, ssh_port=2222, ftp_port=2121, log_dir="intelligence_logs"):
        self.ssh_port = ssh_port
        self.ftp_port = ftp_port
        self.log_dir = log_dir
        self.running = False
        self.attack_stats = defaultdict(lambda: {"ssh": 0, "ftp": 0})
        self.total_attempts = {"ssh": 0, "ftp": 0}
        self.start_time = None
        
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Initialize log files
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_log = os.path.join(log_dir, f"vortex_intel_{timestamp}.json")
        self.csv_log = os.path.join(log_dir, f"vortex_intel_{timestamp}.csv")
        
        self._init_csv_log()
        
        with open(self.json_log, 'w') as f:
            json.dump({"session_start": datetime.datetime.now().isoformat(), "attacks": []}, f)
    
    def _init_csv_log(self):
        """Initialize CSV log file with headers"""
        with open(self.csv_log, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Protocol", "Source_IP", "Source_Port", 
                "Username", "Password", "Success", "Additional_Info"
            ])
    
    def log_attack(self, protocol: str, ip: str, port: int, username: str, 
                   password: str, success: bool = False, info: str = ""):
        """Log an attack attempt to both JSON and CSV files"""
        timestamp = datetime.datetime.now().isoformat()
        
        attack_data = {
            "timestamp": timestamp, "protocol": protocol, "source_ip": ip,
            "source_port": port, "username": username, "password": password,
            "success": success, "additional_info": info
        }
        
        # Log to JSON
        try:
            with open(self.json_log, 'r+') as f:
                data = json.load(f)
                data["attacks"].append(attack_data)
                f.seek(0)
                json.dump(data, f, indent=2)
        except: pass
        
        # Log to CSV
        with open(self.csv_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, protocol, ip, port, username, password, success, info])
        
        self.attack_stats[ip][protocol.lower()] += 1
        self.total_attempts[protocol.lower()] += 1
        self._display_attack(protocol, ip, port, username, password)
    
    def _display_attack(self, protocol: str, ip: str, port: int, 
                       username: str, password: str):
        """Display attack attempt in real-time"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = Colors.FAIL if protocol.upper() == "SSH" else Colors.WARNING
        icon = "🔐" if protocol.upper() == "SSH" else "📁"
        
        print(f"{color}{icon} [{timestamp}] {protocol.upper()} INTRUSION DETECTED!{Colors.ENDC}")
        print(f"  {Colors.BOLD}Origin IP :{Colors.ENDC} {ip}")
        print(f"  {Colors.BOLD}Identity  :{Colors.ENDC} {username}:{password}")
        print(f"  {Colors.BOLD}Stats     :{Colors.ENDC} Attack #{self.attack_stats[ip][protocol.lower()]} from this source")
        print(f"{Colors.OKCYAN}{'━' * 60}{Colors.ENDC}\n")
    
    def ssh_honeypot(self):
        """SSH honeypot service"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', self.ssh_port))
            sock.listen(5)
            print(f"{Colors.OKGREEN}[+] VortexSnare: SSH Listener active on port {self.ssh_port}{Colors.ENDC}")
            while self.running:
                sock.settimeout(1.0)
                try:
                    client, addr = sock.accept()
                    threading.Thread(target=self._handle_ssh_client, args=(client, addr), daemon=True).start()
                except socket.timeout: continue
        finally: sock.close()
    
    def _handle_ssh_client(self, client: socket.socket, addr: Tuple[str, int]):
        ip, port = addr
        try:
            client.send(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n")
            time.sleep(0.5)
            client.send(b"login as: ")
            username = client.recv(1024).decode('utf-8', errors='ignore').strip()
            if username:
                client.send(f"{username}@vortex-server's password: ".encode())
                password = client.recv(1024).decode('utf-8', errors='ignore').strip()
                if password:
                    self.log_attack("SSH", ip, port, username, password, False, "Brute-force")
                    time.sleep(1)
                    client.send(b"Access denied\r\n")
        except: pass
        finally: client.close()

    def ftp_honeypot(self):
        """FTP honeypot service"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', self.ftp_port))
            sock.listen(5)
            print(f"{Colors.OKGREEN}[+] VortexSnare: FTP Listener active on port {self.ftp_port}{Colors.ENDC}")
            while self.running:
                sock.settimeout(1.0)
                try:
                    client, addr = sock.accept()
                    threading.Thread(target=self._handle_ftp_client, args=(client, addr), daemon=True).start()
                except socket.timeout: continue
        finally: sock.close()

    def _handle_ftp_client(self, client: socket.socket, addr: Tuple[str, int]):
        ip, port = addr
        username = ""
        try:
            client.send(b"220-Welcome to VortexVault FTP Service\r\n220 Please enter credentials.\r\n")
            while True:
                data = client.recv(1024).decode('utf-8', errors='ignore').strip()
                if not data: break
                if data.upper().startswith('USER'):
                    username = data.split(' ', 1)[1] if ' ' in data else 'anonymous'
                    client.send(b"331 Password required\r\n")
                elif data.upper().startswith('PASS'):
                    password = data.split(' ', 1)[1] if ' ' in data else ''
                    self.log_attack("FTP", ip, port, username, password, False, "Incursion")
                    client.send(b"530 Login incorrect\r\n")
                    break
        except: pass
        finally: client.close()

    def display_banner(self):
        """Display the original VortexSnare banner"""
        plain_name = "VORTEXSNARE v1.0.4 - THE ULTIMATE DECEPTION PROTOCOL"
        banner = f"""
{Colors.BOLD}{Colors.OKCYAN}
      ██╗   ██╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗
      ██║   ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝
      ██║   ██║██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝ 
      ╚██╗ ██╔╝██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗ 
       ╚████╔╝ ╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗
        ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                         
      ███████╗███╗   ██╗ █████╗ ██████╗ ███████╗
      ██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝
      ███████╗██╔██╗ ██║███████║██████╔╝█████╗  
      ╚════██║██║╚██╗██║██╔══██║██╔══██╗██╔══╝  
      ███████║██║ ╚████║██║  ██║██║  ██║███████╗
      ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
{Colors.ENDC}
{Colors.BOLD}{Colors.UNDERLINE}{plain_name}{Colors.ENDC}

{Colors.OKGREEN}[*] DEPLOYMENT : ACTIVE
[*] SSH PORT   : {self.ssh_port} | FTP PORT : {self.ftp_port}
[*] INTEL LOGS : {self.log_dir}/
[*] STATUS     : MONITORING ALL INBOUND TRAFFIC {Colors.ENDC}

{Colors.FAIL}[!] SYSTEM READY: UNAUTHORIZED ACCESS WILL BE LOGGED [!]{Colors.ENDC}
{Colors.WARNING}[!] PRESS CTRL+C TO TERMINATE AND VIEW FORENSIC DATA{Colors.ENDC}
{Colors.OKCYAN}{'━' * 80}{Colors.ENDC}
"""
        print(banner)

    def display_statistics(self):
        """Display analytics on shutdown"""
        runtime = datetime.datetime.now() - self.start_time if self.start_time else "N/A"
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'━' * 80}")
        print("                      VORTEXSNARE SESSION ANALYTICS")
        print(f"{'━' * 80}{Colors.ENDC}\n")
        print(f"{Colors.OKBLUE}Session Duration   :{Colors.ENDC} {runtime}")
        print(f"{Colors.OKBLUE}Unique Adversaries :{Colors.ENDC} {len(self.attack_stats)}")
        print(f"{Colors.OKBLUE}Total Interceptions:{Colors.ENDC} {self.total_attempts['ssh'] + self.total_attempts['ftp']}")
        
        if self.attack_stats:
            print(f"\n{Colors.BOLD}Targeted Intelligence (Top IPs):{Colors.ENDC}")
            sorted_ips = sorted(self.attack_stats.items(), key=lambda x: x[1]['ssh'] + x[1]['ftp'], reverse=True)[:5]
            for i, (ip, stats) in enumerate(sorted_ips, 1):
                print(f"  [{i}] {ip:15s} -> SSH: {stats['ssh']} | FTP: {stats['ftp']}")
        
        print(f"\n{Colors.OKGREEN}[+] Forensic data exported to {self.log_dir}/{Colors.ENDC}")

    def start(self):
        self.running = True
        self.start_time = datetime.datetime.now()
        self.display_banner()
        threading.Thread(target=self.ssh_honeypot, daemon=True).start()
        threading.Thread(target=self.ftp_honeypot, daemon=True).start()
        try:
            while self.running: time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        print(f"\n{Colors.WARNING}[!] COLLAPSING VORTEX... SYSTEM SHUTTING DOWN.{Colors.ENDC}")
        self.running = False
        time.sleep(1)
        self.display_statistics()

def main():
    parser = argparse.ArgumentParser(description='VortexSnare - Advanced Honeypot')
    parser.add_argument('-s', '--ssh-port', type=int, default=2222)
    parser.add_argument('-f', '--ftp-port', type=int, default=2121)
    args = parser.parse_args()
    
    # Menghapus pengecekan root yang bikin crash di Windows
    trap = VortexSnare(ssh_port=args.ssh_port, ftp_port=args.ftp_port)
    trap.start()

if __name__ == "__main__":
    main()