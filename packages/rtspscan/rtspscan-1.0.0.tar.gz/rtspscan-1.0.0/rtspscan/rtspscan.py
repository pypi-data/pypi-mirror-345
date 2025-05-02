import argparse
import socket
from ipaddress import ip_network
from concurrent.futures import ThreadPoolExecutor
import cv2

open_ips = []

def check_rtsp_port(ip):
    """Check if RTSP port 554 is open on the given IP."""
    port = 554
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)  # Set a timeout to avoid hanging
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                print(f"[OPEN] {ip}:{port}")
                open_ips.append(str(ip))
    except Exception as e:
        print(f"[ERROR] {ip} - {e}")

def scan_ip_range(ip_range):
    """Scan a range of IPs for open RTSP ports."""
    print(f"Scanning IP Range {ip_range} for open RTSP ports (554)...")
    network = ip_network(ip_range, strict=False)
    with ThreadPoolExecutor(max_workers=50) as executor:
        for ip in network.hosts():
            executor.submit(check_rtsp_port, ip)

def open_rtsp_stream(ip):
    """Attempt to open the RTSP stream on the given IP."""
    rtsp_url = f"rtsp://{ip}"
    cap = cv2.VideoCapture(r
