from sys import stderr, exit                                                                   # pylint: disable=W0622
from string import hexdigits
from argparse import ArgumentParser

from simulcrypt.SCS import SCSSimulator


def scs_simulator_cli():
    config = parse_args()
    try:
        process(config)
    except KeyboardInterrupt:
        print(" Aborted by user!", file=stderr)
        exit(1)

def access_criteria(ac: str) -> str:
    """Validate AC hex string, skip 0x prefix if present."""
    for num, char in enumerate(ac):
        if char not in hexdigits:
            if num != 1 and char not in ['x', 'X']:
                raise ValueError()
    return ac

def parse_args():
    parser = ArgumentParser(prog="scs", description="DVB Simulcrypt V3 SCS component simulator.")
    parser.add_argument("CAS_id", type=lambda x: int(x, 0), help="super_CAS_id value, 2 or 4 bytes", metavar='CAS_ID')
    parser.add_argument("-s", "--host", type=str, default="localhost", metavar="HOST",
        help="ECMG server address or hostname, default is localhost")
    parser.add_argument("-p", "--port", type=int, default=2000, help="TCP port number, default is 2000")
    parser.add_argument("-c", "--cp", type=int, default=0, choices=range(10,61), metavar="SEC",
                        help="crypto-period interval, default is min_CP_duration value received from ECMG")
    parser.add_argument("-a", "--ac", type=access_criteria, action="append", dest="AC", default=[],
                        help="Scrambling Group access criteria hex string, default is none")
    parser.add_argument("-128", "--csa3", action="store_true", default=False,
                        help="use 128-bit CW (DVB-CSA3/CISSA mode) instead of 64-bit default")
    return parser.parse_args()

def process(config):
    if config.CAS_id <= 0xFFFF:
        config.CAS_id = config.CAS_id << 16   # extend to 4 bytes

    ac_list = []
    for ac in config.AC:
        if ac.startswith("0x") or ac.startswith("0X"):
            ac = ac[2:]
        ac_list.append(ac)

    cw_len = 8 if not config.csa3 else 16
    sim = SCSSimulator(config.CAS_id,
                       host=config.host,
                       port=config.port,
                       cw_len=cw_len,
                       access_criteria=ac_list,
                       crypto_period=config.cp)
    sim.run()
