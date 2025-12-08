import socket
import time
import random
import json

# ----------------------------
# CONFIGURATION
# ----------------------------
GATEWAY_IP = "192.168.10.2"     # Gateway (packetCaptuerer.py) is capturing this IP
GATEWAY_PORT = 5000             # Any port for sending traffic

DEVICE_IP = "192.168.10.3"      # This machine's IP (make sure it matches DEVICE_IP_MAP)
DEVICE_TYPE = "thermostat"      # Options: camera, thermostat, door_lock, etc.

SEND_INTERVAL = 0.5             # Seconds between packets (modify per device)

# ----------------------------
# Setup UDP socket
# ----------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[ IoT Simulator Started ]")
print(f"Device Type : {DEVICE_TYPE}")
print(f"Source IP   : {DEVICE_IP}")
print(f"Sending packets → {GATEWAY_IP}:{GATEWAY_PORT}")
print("----------------------------------------------")

# ----------------------------
# IoT DEVICE BEHAVIOR PROFILES
# ----------------------------
def generate_payload(device_type):
    if device_type == "camera":
        return {
            "frame_id": random.randint(1000, 9999),
            "size": random.randint(800, 1500)
        }

    if device_type == "thermostat":
        return {
            "temperature": round(random.uniform(20.0, 30.0), 2),
            "humidity": round(random.uniform(30, 70), 2)
        }

    if device_type == "sensor":
        return {
            "motion": bool(random.getrandbits(1)),
            "battery": random.randint(60, 100)
        }

    if device_type == "door_lock":
        return {
            "state": random.choice(["locked", "unlocked"]),
            "battery": random.randint(40, 100)
        }

    # default profile
    return {
        "value": random.random()
    }

# ----------------------------
# Traffic Sending Loop
# ----------------------------
while True:
    try:
        payload = {
            "device_type": DEVICE_TYPE,
            "timestamp": time.time(),
            "data": generate_payload(DEVICE_TYPE),
            "packet_size": random.randint(200, 1400)
        }

        data = json.dumps(payload).encode()

        sock.sendto(data, (GATEWAY_IP, GATEWAY_PORT))

        print("Sent:", payload)

        time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("Stopping IoT Simulator...")
        break

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
