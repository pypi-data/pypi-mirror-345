import socket
import ipaddress
import time
import cv2
import threading
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Check if RTSP port is open
def is_rtsp_port_open(ip):
    try:
        with socket.socket() as sock:
            sock.settimeout(1)
            sock.connect((ip, 554))
            return True
    except:
        return False

# Safely test RTSP stream
def test_rtsp_stream_safe(ip, timeout=5):
    result = {'status': False, 'error': None}

    def try_open():
        try:
            rtsp_url = f"rtsp://{ip}:554"
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                result['error'] = "RTSP stream not opened"
                return
            start_time = time.time()
            while time.time() - start_time < 3:
                ret, _ = cap.read()
                if ret:
                    result['status'] = True
                    break
            cap.release()
        except Exception as e:
            result['error'] = str(e)

    thread = threading.Thread(target=try_open)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        result['error'] = "Timeout"
        return False, result['error']
    return result['status'], result['error']

# Scan one IP
def scan_ip(ip):
    ip = str(ip)
    if is_rtsp_port_open(ip):
        print(f"[+] Port 554 open on {ip} - checking RTSP...")
        success, error = test_rtsp_stream_safe(ip)
        if success:
            print(f"[✔] WORKING CAMERA: {ip}")
            return ip
        else:
            print(f"[!] {ip} - RTSP Error: {error}")
    else:
        print(f"[-] Port 554 closed on {ip}")
    return None

# Preview all cameras in PiP grid for 10 seconds
def show_all_cameras(cameras):
    streams = []
    for ip in cameras:
        url = f"rtsp://{ip}:554"
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            streams.append((ip, cap))
        else:
            print(f"[!] Failed to open stream for {ip}")

    if not streams:
        print("[X] No camera streams available for preview.")
        return

    print(f"[▶] Showing {len(streams)} streams in PiP for 10 seconds...")

    start_time = time.time()
    while time.time() - start_time < 10:
        frames = []
        for ip, cap in streams:
            ret, frame = cap.read()
            if not ret:
                frame = np.zeros((240, 320, 3), dtype=np.uint8)
                cv2.putText(frame, "No Signal", (70, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                frame = cv2.resize(frame, (320, 240))
                cv2.putText(frame, ip, (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            frames.append(frame)

        # Arrange in grid
        grid_rows = []
        row_size = 3  # 3 cameras per row
        for i in range(0, len(frames), row_size):
            row = np.hstack(frames[i:i+row_size])
            grid_rows.append(row)
        grid = np.vstack(grid_rows)

        cv2.imshow("RTSP Cameras PiP", grid)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for _, cap in streams:
        cap.release()
    cv2.destroyAllWindows()
    print("[✓] Preview finished.")

# Main
def main():
    ip_range = input("Enter IP range (e.g., 192.168.1.0/24): ")
    try:
        net = ipaddress.ip_network(ip_range, strict=False)
    except ValueError:
        print("[!] Invalid IP range format.")
        return

    print(f"\n[*] Scanning {ip_range} for RTSP (port 554)...\n")

    working_cameras = []

    try:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(scan_ip, ip) for ip in net.hosts()]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    working_cameras.append(result)
    except KeyboardInterrupt:
        print("\n[!] Scan manually stopped.")

    if working_cameras:
        with open("working_cameras.txt", "w") as f:
            for cam in working_cameras:
                f.write(f"{cam}\n")

    print("\n====== Working Cameras Found ======")
    if working_cameras:
        for cam in working_cameras:
            print(f"[✔] {cam}")
    else:
        print("No working RTSP cameras found.")
        return

    show_all_cameras(working_cameras)

if __name__ == "__main__":
    main()
