# multi_iot.py  — Simulates 10 IoT devices sending traffic at once
import socket
import time
import random
import json
import threading

# -----------------------------------------------------------
# CONFIG
# -----------------------------------------------------------

GATEWAY_IP = "192.168.118.23"   # <-- MUST CHANGE to your laptop IP
GATEWAY_PORT = 5000             # Same port your capturer listens to
SEND_INTERVAL = 2             # Seconds between packets per device

# Your dataset-valid device types mapped to virtual IPs
DEVICES = {
    "192.168.10.2":  "camera",
    "192.168.10.3":  "thermostat",
    "192.168.10.4":  "smart_bulb",
    "192.168.10.5":  "door_lock",
    "192.168.10.6":  "smoke_sensor",
    "192.168.10.7":  "fan_controller",
    "192.168.10.8":  "smart_plug",
    "192.168.10.9":  "weather_station",
    "192.168.10.10": "water_meter",
    "192.168.10.11": "energy_meter"
}

# -----------------------------------------------------------
# DEVICE PAYLOAD PROFILE (MATCHES YOUR TRAINING SET)
# -----------------------------------------------------------

def generate_payload(device):
    if device == "camera":
        return {"frame_id": random.randint(1000, 9999), "quality": random.randint(60, 100)}
    if device == "thermostat":
        return {"temperature": random.uniform(20, 30), "humidity": random.randint(30, 70)}
    if device == "smart_bulb":
        return {"brightness": random.randint(0, 100), "color": random.choice(["warm", "cool"])}
    if device == "door_lock":
        return {"state": random.choice(["locked", "unlocked"]), "battery": random.randint(40, 100)}
    if device == "smoke_sensor":
        return {"smoke_level": random.randint(0, 10), "battery": random.randint(40, 100)}
    if device == "fan_controller":
        return {"speed": random.randint(1, 5), "power": random.choice([True, False])}
    if device == "smart_plug":
        return {"usage_watts": random.randint(10, 200), "state": random.choice([True, False])}
    if device == "weather_station":
        return {"temp": random.uniform(10, 35), "humidity": random.randint(20, 80)}
    if device == "water_meter":
        return {"flow_rate": random.uniform(1, 50)}
    if device == "energy_meter":
        return {"power_kw": random.uniform(0.1, 3.0)}
    return {"value": random.random()}

# -----------------------------------------------------------
# SEND LOOP FOR ONE DEVICE
# -----------------------------------------------------------

def device_thread(ip, device_type):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[STARTED] {device_type.upper()} ({ip}) sending traffic → {GATEWAY_IP}:{GATEWAY_PORT}")

    while True:
        payload = {
            "device_type": device_type,
            "timestamp": time.time(),
            "src_ip": ip,                      # virtual identity
            "data": generate_payload(device_type)
        }

        data = json.dumps(payload).encode()
        sock.sendto(data, (GATEWAY_IP, GATEWAY_PORT))

        print(f"Sent [{device_type}] from {ip} → {GATEWAY_IP}:{GATEWAY_PORT}")

        time.sleep(SEND_INTERVAL)

# -----------------------------------------------------------
# START ALL DEVICES
# -----------------------------------------------------------

if __name__ == "__main__":
    print("=== MULTI-IOT TRAFFIC GENERATOR STARTED ===")

    for ip, dtype in DEVICES.items():
        threading.Thread(target=device_thread, args=(ip, dtype), daemon=True).start()

    while True:
        time.sleep(1)
