# iot.py (FINAL TRAFFIC GENERATOR)
import socket
import time
import random
import json

# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------

MODE = "UDP"   # Change to "TCP" if you want TCP traffic

GATEWAY_IP = "192.168.10.2"    # Your IDS machine or capture target
GATEWAY_PORT = 5000            # Must match packetCaptuerer BPF filter

DEVICE_IP = "192.168.10.3"     # Logical identity (used only inside payload)
DEVICE_TYPE = "thermostat"     # Must match your dataset device list

SEND_INTERVAL = 0.5            # seconds between packets

# Dataset-valid device types:
VALID_DEVICES = [
    "camera", "thermostat", "smart_bulb", "door_lock",
    "smoke_sensor", "fan_controller", "smart_plug",
    "weather_station", "water_meter", "energy_meter"
]

if DEVICE_TYPE not in VALID_DEVICES:
    print("❌ ERROR: Invalid DEVICE_TYPE for your dataset!")
    exit()

# -----------------------------------------------------------
# SOCKET SETUP
# -----------------------------------------------------------
if MODE == "UDP":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[MODE] Using UDP socket.")
else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((GATEWAY_IP, GATEWAY_PORT))
    print("[MODE] Using TCP socket (connected).")

print("\n[ IoT Traffic Simulator Started ]")
print("Device Type :", DEVICE_TYPE)
print("Source IP   :", DEVICE_IP)
print(f"Sending {MODE} packets → {GATEWAY_IP}:{GATEWAY_PORT}")
print("-------------------------------------------------\n")

# -----------------------------------------------------------
# DEVICE PROFILES (dataset-matching)
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
# TRAFFIC SENDING LOOP
# -----------------------------------------------------------
while True:
    try:
        payload = {
            "device_type": DEVICE_TYPE,
            "timestamp": time.time(),
            "src_ip": DEVICE_IP,
            "data": generate_payload(DEVICE_TYPE)
        }

        data = json.dumps(payload).encode()

        if MODE == "UDP":
            sock.sendto(data, (GATEWAY_IP, GATEWAY_PORT))
        else:
            sock.sendall(data)

        print("Sent:", payload)

        time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\n[Stopped by user]")
        break

    except Exception as e:
        print("⚠ Error:", e)
        time.sleep(1)
