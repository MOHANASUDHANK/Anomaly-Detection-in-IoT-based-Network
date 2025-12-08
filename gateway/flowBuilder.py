import time

# flow_id → { start_time, packets }
flows = {}

FLOW_TIMEOUT = 1  # seconds


def get_flow_id(packet):
    """Create a unique ID for each flow."""
    src_ip = packet.ip.src
    dst_ip = packet.ip.dst

    # Extract ports if they exist (TCP/UDP)
    try:
        src_port = packet[packet.transport_layer].srcport
        dst_port = packet[packet.transport_layer].dstport
    except:
        src_port = None
        dst_port = None

    protocol = packet.transport_layer  # "TCP", "UDP", etc.

    return (src_ip, dst_ip, src_port, dst_port, protocol)


def add_packet_to_flow(packet):
    """Add packet to the appropriate flow."""
    flow_id = get_flow_id(packet)

    if flow_id not in flows:
        flows[flow_id] = {
            "start_time": time.time(),
            "packets": []
        }

    flows[flow_id]["packets"].append(packet)


def extract_completed_flows():
    """Return flows that have exceeded timeout."""
    completed = []
    now = time.time()

    for fid, data in list(flows.items()):
        if now - data["start_time"] >= FLOW_TIMEOUT:
            completed.append((fid, data["packets"]))
            del flows[fid]  # remove closed flow

    return completed
