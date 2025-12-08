import pyshark
import time

from flowBuilder import add_packet_to_flow, extract_completed_flows
from feature_extractor import extract_features
from send_to_backend import send_features_to_backend

# The IoT device IP you want to capture
DEVICE_IP = "192.168.10.2"


def start_capture(interface="wifi"):
    print(f"Capturing packets ONLY from/to IP: {DEVICE_IP}")

    capture = pyshark.LiveCapture(
        interface=interface,
        bpf_filter=f"host {DEVICE_IP}"
    )

    last_checgitk = time.time()

    for packet in capture.sniff_continuously():
        try:
            # Add packet to flow builder
            add_packet_to_flow(packet)

            # Check every 1 second for completed flows
            now = time.time()
            if now - last_check >= 1:
                completed = extract_completed_flows()

                for flow_id, pkts in completed:
                    print("\n===== FLOW COMPLETED =====")
                    print("FLOW ID:", flow_id)
                    print("PACKETS IN FLOW:", len(pkts))

                    # Extract features
                    features = extract_features(flow_id, pkts)

                    print("FEATURES:")
                    for k, v in features.items():
                        print(f"  {k}: {v}")

                    print("==========================\n")

                    result = send_features_to_backend(features)

                    print("PREDICTION:", result)


                last_check = now

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    start_capture()
