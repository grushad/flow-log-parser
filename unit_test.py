"""
Basic unit tests to test few functions from the flow log parser module
"""
import unittest
from unittest.mock import patch, mock_open
from flow_log_parser import (
    get_protocol_number,
    load_lookup_table,
    load_dstport_protocol_flow_logs,
    map_port_proto_tag,
    get_protocol_name,
    get_port_protocol_counts,
)

class TestFlowLogParser(unittest.TestCase):
    @patch("socket.getprotobyname")
    def test_get_protocol_number_valid(self, mock_getprotobyname):
        mock_getprotobyname.return_value = 6  # TCP protocol number
        result = get_protocol_number("TCP")
        self.assertEqual(result, "6")

    @patch("socket.getprotobyname")
    def test_get_protocol_number_invalid(self, mock_getprotobyname):
        mock_getprotobyname.side_effect = OSError("Protocol not found")
        with self.assertRaises(ValueError):
            get_protocol_number("INVALID_PROTOCOL")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="dstport,protocol,tag\n80,TCP,http\n443,TCP,https\n",
    )
    def test_load_lookup_table(self, mock_file):
        lookup_dict = load_lookup_table("lookup_table.csv")
        expected = {("80", "6"): "http", ("443", "6"): "https"}
        self.assertEqual(lookup_dict, expected)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK\n
        2 123456789012 eni-9k10l11m 192.168.1.5 51.15.99.115 49321 25 6 20 10000 1620140661 1620140721 ACCEPT OK\n""",
    )
    def test_load_dstport_protocol_flow_logs(self, mock_file):
        flow_logs = load_dstport_protocol_flow_logs("flow_logs.txt")
        expected = [("49153", "6"), ("25", "6")]
        self.assertEqual(flow_logs, expected)

    def test_map_port_proto_tag(self):
        lookup_dict = {("80", "6"): "http", ("443", "6"): "https"}
        flow_logs = [("80", "6"), ("443", "6"), ("8080", "6")]
        result = map_port_proto_tag(lookup_dict, flow_logs)
        expected = {"http": 1, "https": 1, "untagged": 1}
        self.assertEqual(result, expected)

    def test_get_protocol_name(self):        
        result = get_protocol_name(6)  # TCP
        self.assertEqual(result, "TCP")
        result_invalid = get_protocol_name(999)  # Invalid protocol number
        self.assertEqual(result_invalid, "Unknown Protocol (999)")

    def test_get_port_protocol_counts(self):        
        flow_logs = [("80", "6"), ("443", "6"), ("80", "6")]
        result = get_port_protocol_counts(flow_logs)
        expected = {("80", "TCP"): 2, ("443", "TCP"): 1}
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
