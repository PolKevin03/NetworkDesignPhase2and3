from socket import *
import sys
import struct
import zlib

# packet types
DATA = 0
ACK = 1
END = 2

# header format
HEADER_FMT = "!BBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff

def make_packet(ptype, seq, payload=b""):
    length = len(payload)
    checksum = 0
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    checksum = compute_checksum(header + payload)
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    return header + payload

def parse_packet(packet_bytes):
    if len(packet_bytes) < HEADER_LEN:
        return None, None, b"", True

    header = packet_bytes[:HEADER_LEN]
    payload = packet_bytes[HEADER_LEN:]

    ptype, seq, length, checksum = struct.unpack(HEADER_FMT, header)

    header_zero = struct.pack(HEADER_FMT, ptype, seq, length, 0)
    calc_checksum = compute_checksum(header_zero + payload)

    corrupt = (calc_checksum != checksum)
    return ptype, seq, payload, corrupt


serverName = "localhost"
serverPort = 13000
CHUNK = 1024

if len(sys.argv) < 2:
    print("Usage: python client_rdt30.py file.bmp")
    sys.exit()

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)

seq = 0
retransmissions = 0
chunks_sent = 0

with open(sys.argv[1], "rb") as f:
    while True:
        data = f.read(CHUNK)
        if not data:
            break

        packet = make_packet(DATA, seq, data)
        chunks_sent += 1

        while True:
            clientSocket.sendto(packet, (serverName, serverPort))

            try:
                ack_packet, _ = clientSocket.recvfrom(2048)
                ptype, ack_seq, _, corrupt = parse_packet(ack_packet)

                if not corrupt and ptype == ACK and ack_seq == seq:
                    seq = 1 - seq
                    break
                else:
                    retransmissions += 1

            except timeout:
                retransmissions += 1
                continue

# END packet
endpkt = make_packet(END, seq, b"")

while True:
    clientSocket.sendto(endpkt, (serverName, serverPort))
    try:
        ack_packet, _ = clientSocket.recvfrom(2048)
        ptype, ack_seq, _, corrupt = parse_packet(ack_packet)

        if not corrupt and ptype == ACK and ack_seq == seq:
            break
        else:
            retransmissions += 1

    except timeout:
        retransmissions += 1
        continue

clientSocket.close()

print("Done sending.")
print(f"chunks_sent: {chunks_sent}")
print(f"retransmissions: {retransmissions}")