"""Independent educational PCAP; these packets are not board traffic."""
import json
import struct


def make_sample_pcap():
    packets = [(0, b"first"), (0, b"second-packet"), (2, b"third"), (4, b"fourth-data"), (6, b"outside")]
    data = bytearray(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for second, payload in packets:
        data.extend(struct.pack("<IIII", second, 0, len(payload), len(payload)))
        data.extend(payload)
    return bytes(data)


def summarize(pcap, seconds):
    if pcap[:4] != struct.pack("<I", 0xA1B2C3D4):
        raise ValueError("지원하지 않는 PCAP 형식")
    offset, selected = 24, []
    while offset < len(pcap):
        timestamp, _, size, _ = struct.unpack_from("<IIII", pcap, offset)
        offset += 16
        payload = pcap[offset:offset + size]
        if len(payload) != size:
            raise ValueError("잘린 패킷")
        offset += size
        if 0 <= timestamp < seconds:
            selected.append(size)
    return {"window_seconds": seconds, "packet_count": len(selected), "byte_sum": sum(selected)}


def main():
    sample = make_sample_pcap()
    print(json.dumps({"source": "교육용 자체 생성 PCAP", "first_5_seconds": summarize(sample, 5),
                      "first_1_second": summarize(sample, 1)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
