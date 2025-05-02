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
            sock.settimeout(1)
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
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print(f"[FAILED] Unable to open RTSP stream at {rtsp_url}")
        return

    print(f"[SUCCESS] Streaming from {rtsp_url}. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to retrieve frame.")
            break
        cv2.imshow("RTSP Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="RTSP Port Scanner and Streamer")
    parser.add_argument("ip_range", help="IP range to scan (e.g., 192.168.1.0/24)")

    args = parser.parse_args()
    scan_ip_range(args.ip_range)

    if open_ips:
        print("\nDevices with RTSP port open:")
        for i, ip in enumerate(open_ips):
            print(f"{i+1}. {ip}")

        choice = input("\nEnter the number of the IP to open RTSP stream (or press Enter to skip): ")
        if choice.isdigit() and 1 <= int(choice) <= len(open_ips):
            selected_ip = open_ips[int(choice) - 1]
            open_rtsp_stream(selected_ip)
        else:
            print("No valid choice made. Exiting.")
    else:
        print("No open RTSP ports found in the given IP range.")

# Required for PyPI CLI entry point
if __name__ == "__main__":
    main()
