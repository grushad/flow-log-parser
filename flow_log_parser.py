"""
Program that can parse a file containing flow log data and 
maps each row to a tag based on a lookup table

Generates an output file with answer
"""
import socket
import csv
import argparse

def get_protocol_number(protocol_name: str):
    """Returns the protocol number corresponding to the given protocol name.
    Args:
        protocol_name (str): The protocol name (e.g., 'TCP', 'UDP').
    Returns:
        int: The protocol number corresponding to the protocol name.
    Raises:
        ValueError: If the protocol name is invalid.
    """
    try:
        protocol_num = socket.getprotobyname(protocol_name)
        return str(protocol_num)
    except OSError as err:
        raise ValueError(f"Invalid protocol name: {protocol_name}.") from err

def load_lookup_table(lookup_table_file_name: str):
    """Load the lookup table into a dictionary.
    Args: 
        name of the csv file which has the lookup table
    Returns:
        a dictionary with destination port and protocol number as key, mapped to the tag
    """
    lookup = {}
    try:
        with open(lookup_table_file_name, mode='r', newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    key = (row['dstport'], get_protocol_number(row['protocol']))
                    lookup[key] = row['tag'].lower()
                except ValueError as err:
                    print(f"Skipping invalid entry in lookup table: {err}")
    except Exception as e:
        raise IOError(f"Failed to read the lookup table file: {e}") from e
    return lookup

def load_dstport_protocol_flow_logs(flow_logs_file_name: str):
    """Parse the plain text flow log and map to tags using the lookup table.
        Args:
            filename of the lookup file: str
        Returns:
            destination port and protocol combination: list
    """
    dstport_proto = []
    try:
        with open(flow_logs_file_name, mode='r', encoding="utf-8") as f:
            for line in f:
                fields = line.split()
                if len(fields) >= 8:
                    dstport = fields[6]
                    protocol = fields[7]
                    dstport_proto.append((dstport, protocol))
                else:
                    print(f"Skipping incomplete line: {line.strip()}")
    except Exception as e:
        raise IOError(f"Failed to read the flow log file: {e}") from e
    return dstport_proto

def map_port_proto_tag(lookup: dict, dstport_proto: list):
    """
    Maps the destination port protocol combination to the tag based on lookup
    Args:
        lookup table dictionary, destination port and protocol combination from flow logs
    Returns:
        a dictionary with the tag and its count
    """
    tag_count_dict = {}
    for key in dstport_proto:
        if key in lookup:
            tag = lookup[key]
        else:
            tag = "untagged"
        if tag not in tag_count_dict:
            tag_count_dict[tag] = 0
        tag_count_dict[tag] += 1
    return tag_count_dict

def write_output_file(output_file_name: str, tag_dict: dict, port_proto_dict: dict):
    """
    writes to output csv file
    Args:
        output file name: str, tag counts: dict
    """
    try:
        with open(output_file_name, mode='w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['Tag','Count'])
            for key, value in tag_dict.items():
                writer.writerow([key, value])
            writer.writerow([])
            writer.writerow(['Port', 'Protocol', 'Count'])
            for key, value in port_proto_dict.items():
                writer.writerow([key[0], key[1], value])        
        print(f"Output written to file {output_file_name}")
    except Exception as e:
        raise IOError(f"Failed to write to output file: {e}") from e

def get_protocol_name(protocol_num: int):
    """
    maps protocol number to its name
    Args:
        protocol num: int
    """
    prefix = "IPPROTO_"
    table = {}
    for name, num in vars(socket).items():
        if name.startswith(prefix):
            table[num] = name[len(prefix):]
    return table.get(protocol_num, f"Unknown Protocol ({protocol_num})")

def get_port_protocol_counts(port_protocol: list):
    """
    gets count of matches for each port/protocol combination 
    Args:
        port protocol combination from flow logs file: list
    returns:
        a dictionary with counts of each port/protocol combination
    """
    port_proto_dict = {}
    for port, protocol in port_protocol:
        protocol_name = get_protocol_name(int(protocol))
        if (port, protocol_name) not in port_proto_dict:
            port_proto_dict[(port, protocol_name)] = 0
        port_proto_dict[(port, protocol_name)] += 1
    return port_proto_dict

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process flow log data and lookup table.")
    parser.add_argument('lookup_file', type=str, help="Path to the lookup table CSV file")
    parser.add_argument('flow_log_file', type=str, help="Path to the flow log file")

    parser.add_argument('--output', type=str, default="output.csv", help="Output CSV file (default: output.csv)")

    return parser.parse_args()

def main():
    """
    Main function that calls other functions to perform required tasks
    """
    args = parse_args()
    try:
        lookup_dict = load_lookup_table(args.lookup_file)
        flow_logs = load_dstport_protocol_flow_logs(args.flow_log_file)
        tag_mapping = map_port_proto_tag(lookup_dict, flow_logs)
        port_proto_count = get_port_protocol_counts(flow_logs)
        write_output_file(args.output, tag_mapping, port_proto_count)

    except FileNotFoundError as fnf_error:
        print(f"File error: {fnf_error}")
    except ValueError as ve:
        print(f"Value error: {ve}")
    except IOError as io_error:
        print(f"I/O error: {io_error}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
    