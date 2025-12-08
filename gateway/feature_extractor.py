import time
import numpy as np
import math
from collections import Counter


def calculate_entropy(values):
    """Shannon entropy for destination ports."""
    if len(values) == 0:
        return 0.0
    counts = Counter(values)
    total = len(values)
    entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
    return entropy


def extract_features(flow_id, packets):
    """Convert a flow into your 21 ML features."""

    src_ip, dst_ip, src_port, dst_port, protocol = flow_id

    # Device type mapping
    DEVICE_IP_MAP = {
        "192.168.10.2": "camera",
        "192.168.10.3": "thermostat",
        "192.168.10.4": "door_lock",
        "192.168.10.5": "lightbulb",
        "192.168.10.6": "speaker",
        "192.168.10.7": "tv",
        "192.168.10.8": "router",
        "192.168.10.9": "sensor",
        "192.168.10.10": "printer",
    }

    device_type = DEVICE_IP_MAP.get(src_ip, "camera")  # default if unknown

    packet_sizes = []
    timestamps = []
    dest_ports = []

    syn_count = 0
    ack_count = 0
    rst_count = 0

    # Extract values from packets
    for pkt in packets:
        try:
            packet_sizes.append(int(pkt.length))
            timestamps.append(float(pkt.sniff_timestamp))

            # destination port
            try:
                dest_ports.append(int(pkt[pkt.transport_layer].dstport))
            except:
                pass

            # TCP flags
            if protocol == "TCP":
                flags = pkt.tcp.flags
                if "S" in flags: syn_count += 1
                if "A" in flags: ack_count += 1
                if "R" in flags: rst_count += 1

        except:
            pass

    # Feature calculations
    packet_count = len(packet_sizes)
    byte_count = sum(packet_sizes)

    avg_packet_size = np.mean(packet_sizes) if packet_count else 0

    # Inter-arrival times
    inter_arrival_times = np.diff(timestamps) if len(timestamps) > 1 else []

    avg_iat = np.mean(inter_arrival_times) if len(inter_arrival_times) > 0 else 0
    inter_arrival_time = inter_arrival_times[-1] if len(inter_arrival_times) > 0 else 0

    # Flow duration
    flow_duration = timestamps[-1] - timestamps[0] if len(timestamps) >= 2 else 0.0

    byte_rate = byte_count / flow_duration if flow_duration > 0 else 0
    packet_rate_1s = packet_count / flow_duration if flow_duration > 0 else 0
    packet_rate_60s = packet_rate_1s * 60
    packet_rate_z = (packet_rate_1s - 10) / 5

    unique_dest_ports = len(set(dest_ports))
    unique_dest_ips = 1

    dest_port_entropy = calculate_entropy(dest_ports)

    protocol_id_map = {"TCP": 1, "UDP": 2, "ICMP": 3}
    protocol_id = protocol_id_map.get(protocol, 0)

    # Port bucket
    if dst_port in [80, 443]:
        dest_port_bucket = "web"
    elif dst_port in [1883, 8883]:
        dest_port_bucket = "mqtt"
    else:
        dest_port_bucket = "iot_service"

    return {
        "device_type": device_type,
        "timestamp": timestamps[-1] if len(timestamps) > 0 else time.time(),
        "packet_size": packet_sizes[-1] if packet_count else 0,
        "avg_packet_size": avg_packet_size,
        "inter_arrival_time": inter_arrival_time,
        "avg_iat": avg_iat,
        "protocol_id": protocol_id,
        "dest_port_bucket": dest_port_bucket,
        "flow_duration": flow_duration,
        "packet_count": packet_count,
        "byte_rate": byte_rate,
        "packet_rate_1s": packet_rate_1s,
        "packet_rate_60s": packet_rate_60s,
        "packet_rate_z": packet_rate_z,
        "unique_dest_ports_count": unique_dest_ports,
        "unique_dest_ips_count": unique_dest_ips,
        "dest_port_entropy": dest_port_entropy,
        "syn_flag_count": syn_count,
        "ack_flag_count": ack_count,
        "rst_flag_count": rst_count
    }
