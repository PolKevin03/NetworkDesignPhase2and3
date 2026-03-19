from socket import *
import struct
import zlib
import random
import sys

DATA = 0
ACK = 1
END = 2

HEADER_FMT = "!BBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff

def make_packet(ptype, seq, payload=b""):
    length = len(payload)
    header = struct.pack(HEADER_FMT, ptype, seq, length, 0)
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
    calc = compute_checksum(header_zero + payload)
    return ptype, seq, payload, calc != checksum

def drop_data(pkt, rate):
    if len(pkt) < HEADER_LEN:
        return False
    if pkt[0] == DATA and rate > 0 and random.random() < rate:
        return True
    return False

if len(sys.argv) < 2:
    print("Usage: python server_rdt30updated.py [loss 0..1] [seed]")
    sys.exit()

loss = float(sys.argv[1])
seed = int(sys.argv[2]) if len(sys.argv) >= 3 else None

if seed is not None:
    random.seed(seed)

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", 13000))

print(f"Server Ready (loss={loss})")

out = open("received.bmp", "wb")
expected = 0

dropped = 0
accepted = 0
dupacks = 0

while True:
    pkt, addr = sock.recvfrom(2048)

    if drop_data(pkt, loss):
        dropped += 1
        continue

    t, s, payload, bad = parse_packet(pkt)

    if t == END:
        sock.sendto(make_packet(ACK, s), addr)
        break

    if not bad and t == DATA and s == expected:
        out.write(payload)
        sock.sendto(make_packet(ACK, s), addr)
        expected ^= 1
        accepted += 1
    else:
        sock.sendto(make_packet(ACK, 1 - expected), addr)
        dupacks += 1

out.close()
sock.close()

print("File saved.")
print(f"dropped_data_packets: {dropped}")
print(f"accepted_packets: {accepted}")
print(f"duplicate_acks_sent: {dupacks}")