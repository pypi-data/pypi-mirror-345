from sys import stderr, exit                                                                   # pylint: disable=W0622
from argparse import ArgumentParser

from simulcrypt.MUX import MUXSimulator


def mux_simulator_cli():
    config = parse_args()
    try:
        process(config)
    except KeyboardInterrupt:
        print(" Aborted by user!", file=stderr)
        exit(1)

def parse_args():
    parser = ArgumentParser(prog="mux", description="DVB Simulcrypt MUX component simulator.")
    parser.add_argument('client_id', help='super_CAS_id or client_id, 2 or 4 bytes', type=lambda x: int(x, 0),
                        metavar='CAS_ID')
    parser.add_argument('-p', '--port', help='TCP port number, default is 2100', type=int, dest='port', default=2100)
    parser.add_argument('-b', help='EMM bandwith, default is 100kbps', type=int, dest='bandwidth',
                        default=100, metavar='BW')
    parser.add_argument('-d', '--data', help='output DATA_PROVISION messages, default is not', action='store_true',
                        default=False, dest='data_provision')
    parser.add_argument('-v', help='protocol version 1-5, default is accept from peer', type=int,
                        default=0, dest='protocol_version', choices=range(1,6), metavar='NUM')
    parser.add_argument('--channel_id', help='data_channel_id value, default is 0', type=int, dest='channel_id',
                        default=0, metavar='ID')
    parser.add_argument('--stream_id', help='data_stream_id value, default is 0', type=int, dest='stream_id',
                        default=0, metavar='ID')
    parser.add_argument('--data_id', help='data_id value, default is 0', type=int, dest='data_id',
                        default=0, metavar='ID')

    return parser.parse_args()

def process(config):
    if config.client_id <= 0xFFFF:
        config.client_id = config.client_id << 16   # extend to 4 bytes

    sim = MUXSimulator(config.client_id,
                       port=config.port,
                       bandwidth=config.bandwidth,
                       data_channel_id=config.channel_id,
                       data_stream_id=config.stream_id,
                       data_id=config.data_id,
                       protocol_version=config.protocol_version,
                       output_data_provision=config.data_provision)
    sim.conn_loop()
