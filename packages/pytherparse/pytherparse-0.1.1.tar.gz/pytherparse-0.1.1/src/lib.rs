use pyo3::prelude::*;
use pyo3::types::PyList;
use etherparse::{PacketHeaders, IpHeader, TransportHeader, InternetSlice};
use pcap::Capture;

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyIpv4Header {
    #[pyo3(get)]
    pub source: [u8; 4],
    #[pyo3(get)]
    pub destination: [u8; 4],
    #[pyo3(get)]
    pub ttl: u8,
}

impl From<etherparse::Ipv4Header> for PyIpv4Header {
    fn from(header: etherparse::Ipv4Header) -> Self {
        PyIpv4Header {
            source: header.source,
            destination: header.destination,
            ttl: header.time_to_live,
        }
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyTcpHeader {
    #[pyo3(get)]
    pub source_port: u16,
    #[pyo3(get)]
    pub destination_port: u16,
    #[pyo3(get)]
    pub syn: bool,
    #[pyo3(get)]
    pub ack: bool,
}

impl From<etherparse::TcpHeader> for PyTcpHeader {
    fn from(header: etherparse::TcpHeader) -> Self {
        PyTcpHeader {
            source_port: header.source_port,
            destination_port: header.destination_port,
            syn: header.syn,
            ack: header.ack,
        }
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyEthernetHeader {
    #[pyo3(get)]
    pub source: [u8; 6],
    #[pyo3(get)]
    pub destination: [u8; 6],
    #[pyo3(get)]
    pub ether_type: u16,
}

impl From<etherparse::Ethernet2Header> for PyEthernetHeader {
    fn from(header: etherparse::Ethernet2Header) -> Self {
        PyEthernetHeader {
            source: header.source,
            destination: header.destination,
            ether_type: header.ether_type,
        }
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct ParsedPacket {
    #[pyo3(get)]
    pub link: Option<PyEthernetHeader>,
    #[pyo3(get)]
    pub ip: Option<PyIpv4Header>,
    #[pyo3(get)]
    pub transport: Option<PyTcpHeader>,
}

#[pyfunction]
pub fn parse_packet(data: &[u8]) -> PyResult<ParsedPacket> {
    match PacketHeaders::from_ethernet_slice(data) {
        Ok(headers) => {
            let parsed = ParsedPacket {
                link: headers.link.map(PyEthernetHeader::from),
                ip: match headers.ip {
                    Some(IpHeader::Version4(ip, _)) => Some(PyIpv4Header::from(ip)),
                    _ => None,
                },
                transport: match headers.transport {
                    Some(TransportHeader::Tcp(tcp)) => Some(PyTcpHeader::from(tcp)),
                    _ => None,
                },
            };
            Ok(parsed)
        },
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("Parsing failed: {}", e))),
    }
}

#[pyfunction]
pub fn parse_pcap_file(py: Python<'_>, path: String) -> PyResult<Py<PyList>> {
    let mut packets = Vec::new();

    let mut cap = Capture::from_file(path).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to open pcap file: {}", e))
    })?;

    while let Ok(packet) = cap.next_packet() {
        if let Ok(headers) = PacketHeaders::from_ethernet_slice(&packet.data) {
            let parsed = ParsedPacket {
                link: headers.link.map(PyEthernetHeader::from),
                ip: match headers.ip {
                    Some(IpHeader::Version4(ip, _)) => Some(PyIpv4Header::from(ip)),
                    _ => None,
                },
                transport: match headers.transport {
                    Some(TransportHeader::Tcp(tcp)) => Some(PyTcpHeader::from(tcp)),
                    _ => None,
                },
            };
            packets.push(parsed);
        }
    }

    let py_packets: Vec<_> = packets
        .into_iter()
        .map(|pkt| Py::new(py, pkt).unwrap())
        .collect();

    let list = PyList::new(py, py_packets)?; // Bound<'_, PyList>
    Ok(list.into())                          // Py<PyList>
}

#[pymodule]
fn pytherparse_native(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_packet, m)?)?;
    m.add_function(wrap_pyfunction!(parse_pcap_file, m)?)?;
    m.add_class::<ParsedPacket>()?;
    m.add_class::<PyIpv4Header>()?;
    m.add_class::<PyTcpHeader>()?;
    m.add_class::<PyEthernetHeader>()?;
    Ok(())
}