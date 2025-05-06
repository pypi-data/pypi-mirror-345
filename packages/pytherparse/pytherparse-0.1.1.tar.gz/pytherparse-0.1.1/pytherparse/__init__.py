from .pytherparse_native import (
    parse_packet,
    parse_pcap_file,
    ParsedPacket,
    PyIpv4Header,
    PyTcpHeader,
    PyEthernetHeader,
)

def parse(file_path_or_bytes):
    if isinstance(file_path_or_bytes, str):
        return parse_pcap_file(file_path_or_bytes)
    elif isinstance(file_path_or_bytes, (bytes, bytearray)):
        return parse_packet(file_path_or_bytes)
    else:
        raise TypeError("parse() only accepts a file path (str) or raw bytes (bytes/bytearray)")

__all__ = [
    "parse",
    "parse_packet",
    "parse_pcap_file",
    "ParsedPacket",
    "PyIpv4Header",
    "PyTcpHeader",
    "PyEthernetHeader",
]