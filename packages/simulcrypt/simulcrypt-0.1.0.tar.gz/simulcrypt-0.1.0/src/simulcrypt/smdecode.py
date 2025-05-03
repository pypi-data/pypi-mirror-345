from sys import stderr, exit                                                                   # pylint: disable=W0622
from argparse import ArgumentParser

from simulcrypt import SimulcryptMessage


def smdecode_cli():
    config = parse_args()
    try:
        process(config)
    except KeyboardInterrupt:
        print(" Aborted by user!", file=stderr)
        exit(1)

def parse_args():
    parser = ArgumentParser(prog="smdecode", description="Decode hex stream of DVB Simulcrypt message.")
    parser.add_argument("hex_stream", help="raw data hex stream (020201...)", metavar="HEXSTREAM")
    parser.add_argument("-j", "--json", help="dump message(s) as JSON object", action="store_true", default=False)
    return parser.parse_args()

def process(config):
    data = config.hex_stream.replace(":", "")
    try:
        data = bytes.fromhex(data)
    except ValueError:
        if config.json:
            print('{"error":"invalid stream of hexadecimal numbers"}')
        else:
            print("error: invalid stream of hexadecimal numbers", file=stderr)
        exit(1)

    while True:
        scm = SimulcryptMessage(data)
        if not scm.is_simulcrypt:
            if config.json:
                print(f'{{"error":"{scm.error_message}"}}')
            else:
                print('error:', scm.error_message, file=stderr)
            exit(1)
        if config.json:
            print(scm.dump_json())
        else:
            print(scm.dump())
        if scm.leftover:
            data = scm.leftover
        else:
            break
