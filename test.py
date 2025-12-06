import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import math

# --------------------------------------------
# CONFIGURATION
# --------------------------------------------
DEVICE_TYPES = [
    "camera", "thermostat", "smart_bulb", "door_lock", "smoke_sensor",
    "fan_controller", "smart_plug", "weather_station",
    "water_meter", "energy_meter"
]

ATTACK_TYPES = [
    "normal",
    "ddos_flood",
    "slowloris",
    "port_scan",
    "syn_flood",
    "udp_flood",
    "data_exfiltration",
    "botnet_beacon",
    "icmp_flood",
    "mqtt_misuse"
]

# Total rows generated will be devices * rows_per_device
ROWS_PER_DEVICE = 16000  # 160,000 total rows
START_TIME = datetime(2025, 1, 1)

# --------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------

def random_time_increase(base_time):
    """Increments time by 1ms to 2000ms."""
    return base_time + timedelta(milliseconds=random.randint(1, 2000))

def choose_protocol():
    """0=TCP, 1=UDP, 2=MQTT"""
    return random.choice([0, 1, 2])

def port_bucket():
    return random.choice(["well_known", "registered", "ephemeral", "iot_service"])

def safe_byte_rate(packet_size, pkt_count, duration):
    return round((packet_size * pkt_count) / max(duration, 0.0001), 3)

def compute_entropy(n_items):
    """Simulates entropy value based on diversity."""
    return round(random.uniform(0.1, 3.5), 3)

# --------------------------------------------
# FEATURE GENERATOR
# --------------------------------------------

def generate_features(device, attack, timestamp):
    
    # 1. Device-Specific Normal Behavior Profiles
    base_packet_range = {
        "camera": (800, 1500),
        "thermostat": (40, 80),
        "smart_bulb": (50, 120),
        "door_lock": (60, 150),
        "smoke_sensor": (40, 100),
        "fan_controller": (80, 200),
        "smart_plug": (60, 150),
        "weather_station": (80, 200),
        "water_meter": (50, 120),
        "energy_meter": (70, 180)
    }[device]

    # Defaults
    packet_size = random.randint(*base_packet_range)
    iat = round(random.uniform(0.5, 5.0), 4)
    protocol = choose_protocol()
    duration = round(random.uniform(0.2, 2.0), 3)
    pkt_count = random.randint(1, 8)
    syn = ack = rst = 0
    bucket = port_bucket()

    # --------------------------------------------
    # LOGIC BY ATTACK TYPE
    # --------------------------------------------

    if attack == "normal":
        # FIX: Device Personality Logic
        if device in ["thermostat", "smart_bulb", "smoke_sensor", "water_meter"]:
            protocol = 2 # Prefer MQTT for sensors
            bucket = "iot_service"
        elif device == "camera":
            protocol = random.choice([0, 1]) # TCP or UDP for cameras
        
        # FIX: TCP Flags for Normal Traffic (Critical for ML)
        if protocol == 0: # TCP
            ack = random.randint(1, pkt_count) # Normal traffic has ACKs!
            syn = 1 if random.random() < 0.1 else 0 # Occasional SYN

    elif attack == "ddos_flood":
        packet_size = random.randint(60, 120)
        iat = round(random.uniform(0.00001, 0.005), 6)
        protocol = 1 # UDP
        duration = random.uniform(0.01, 0.2)
        pkt_count = random.randint(50, 300)
        rst = random.randint(0, 3)

    elif attack == "slowloris":
        packet_size = random.randint(10, 40)
        iat = round(random.uniform(10, 30), 3)
        protocol = 0 # TCP
        duration = random.uniform(60, 200)
        pkt_count = random.randint(1, 3)
        syn = random.randint(1, 3)

    elif attack == "port_scan":
        packet_size = random.randint(40, 80)
        iat = round(random.uniform(0.01, 0.5), 3)
        protocol = 0 # TCP
        duration = random.uniform(0.1, 1.0)
        pkt_count = random.randint(1, 5)
        syn = random.randint(5, 20)

    elif attack == "syn_flood":
        packet_size = random.randint(40, 60)
        iat = round(random.uniform(0.0001, 0.003), 5)
        protocol = 0 # TCP
        duration = random.uniform(0.01, 0.1)
        pkt_count = random.randint(30, 200)
        syn = random.randint(100, 500)

    elif attack == "udp_flood":
        packet_size = random.randint(500, 1200)
        iat = round(random.uniform(0.0001, 0.003), 5)
        protocol = 1 # UDP
        duration = random.uniform(0.01, 0.1)
        pkt_count = random.randint(50, 250)

    elif attack == "data_exfiltration":
        packet_size = random.randint(800, 1500)
        iat = round(random.uniform(0.1, 1.0), 3)
        protocol = 0 # TCP
        duration = random.uniform(5, 20)
        pkt_count = random.randint(100, 500)
        # FIX: Exfiltration uses established connections, so High ACKs
        ack = random.randint(pkt_count // 2, pkt_count)

    elif attack == "botnet_beacon":
        packet_size = random.randint(40, 60)
        iat = round(random.uniform(20, 60), 3)
        protocol = 2 # MQTT or similar
        duration = random.uniform(1, 3)
        pkt_count = random.randint(1, 2)
        bucket = "iot_service"

    elif attack == "icmp_flood":
        packet_size = random.randint(60, 120)
        iat = round(random.uniform(0.0005, 0.01), 5)
        protocol = 1 # UDP/ICMP approximation
        duration = random.uniform(0.05, 0.2)
        pkt_count = random.randint(50, 200)

    elif attack == "mqtt_misuse":
        packet_size = random.randint(200, 600)
        iat = round(random.uniform(0.01, 0.5), 3)
        protocol = 2 # MQTT
        duration = random.uniform(1, 3)
        pkt_count = random.randint(5, 20)
        bucket = "iot_service"

    # --------------------------------------------
    # CALCULATE DERIVED FEATURES
    # --------------------------------------------
    avg_packet = packet_size # Simplified for single flow row
    avg_iat = iat
    byte_rate = safe_byte_rate(packet_size, pkt_count, duration)

    # Simulate Rates
    pr1 = pkt_count
    pr60 = pkt_count * random.randint(5, 40)
    
    # Context Features
    port_div = random.randint(1, 10)
    ip_div = random.randint(1, 8)
    entropy_val = compute_entropy(port_div)
    pr_z = round((pr1 - 10) / 5, 3)

    return [
        device, timestamp, packet_size, avg_packet,
        iat, avg_iat, protocol, bucket, duration,
        pkt_count, byte_rate, pr1, pr60, pr_z, port_div,
        ip_div, entropy_val, syn, ack, rst,
        0 if attack == "normal" else 1
    ]

# ----------------------------------------------------
# MAIN GENERATOR LOOP
# ----------------------------------------------------
def generate_dataset():
    rows = []
    time_counter = START_TIME
    
    print(f"Generating dataset ({len(DEVICE_TYPES) * ROWS_PER_DEVICE} rows)...")

    for device in DEVICE_TYPES:
        print(f"Processing {device}...")
        for _ in range(ROWS_PER_DEVICE):
            
            # Weighted choice: 70% Normal, 30% Attacks
            attack = random.choices(
                ATTACK_TYPES,
                weights=[70, 5, 2, 3, 3, 3, 4, 4, 3, 3],
                k=1
            )[0]

            time_counter = random_time_increase(time_counter)
            
            # FIX: Convert Timestamp to FLOAT (Epoch) for ML
            ts_epoch = time_counter.timestamp()

            row = generate_features(device, attack, ts_epoch)
            rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows, columns=[
        "device_type", "timestamp", "packet_size", "avg_packet_size",
        "inter_arrival_time", "avg_iat", "protocol_id", "dest_port_bucket",
        "flow_duration", "packet_count", "byte_rate", "packet_rate_1s",
        "packet_rate_60s", "packet_rate_z", "unique_dest_ports_count",
        "unique_dest_ips_count", "dest_port_entropy", "syn_flag_count",
        "ack_flag_count", "rst_flag_count", "window_label"
    ])

    # Save to CSV
    filename = "iot_anomaly_dataset.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Success! Dataset saved as: {filename}")
    print(df.head())

if __name__ == "__main__":
    generate_dataset()