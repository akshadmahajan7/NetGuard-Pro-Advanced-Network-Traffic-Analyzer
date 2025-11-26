import threading
from scapy.all import sniff, IP, TCP, UDP
from src.database import DBManager

# Global flag to control the sniffer thread
stop_sniffer_flag = threading.Event()

def packet_callback(packet, db_instance):
    """Callback function processed for every packet captured."""
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        length = len(packet)
        proto = "Other"
        flags = "None"

        if TCP in packet:
            proto = "TCP"
            flags = packet[TCP].flags
        elif UDP in packet:
            proto = "UDP"
        
        # Log to Database
        db_instance.log_packet(src_ip, dst_ip, proto, length, flags)

def stop_check(x):
    """Scapy runs this check after every packet to see if it should stop."""
    return stop_sniffer_flag.is_set()

def start_sniffing_thread():
    """The function to run in the background thread."""
    # Each thread needs its own DB connection for thread safety
    db_conn = DBManager() 
    print("[Thread] Sniffer thread started.")
    
    stop_sniffer_flag.clear()

    try:
        # sniff runs until stop_check returns True
        sniff(prn=lambda pkt: packet_callback(pkt, db_conn), 
              store=0, 
              stop_filter=stop_check)
    except Exception as e:
        print(f"[Thread Error] {e}")
    finally:
        db_conn.close()
        print("[Thread] Sniffer thread stopped.")
