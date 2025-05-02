"""Do reverse DNS query on networks."""

import argparse
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from socket import gethostbyaddr, herror

__version__ = "0.1"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "networks",
        nargs="+",
        help="""IP address and an optional mask, separated by a slash
        (/).  The IP address is the network address, and the mask can
        be either a single number, which means it’s a prefix, or a
        string representation of an IPv4 address.

        If it’s the latter, the mask is interpreted as a net mask if
        it starts with a non-zero field, or as a host mask if it
        starts with a zero field, with the single exception of an
        all-zero mask which is treated as a net mask.

        If no mask is provided, it’s considered to be /32.

        For example, the following address specifications are
        equivalent: 192.168.1.0/24, 192.168.1.0/255.255.255.0 and
        192.168.1.0/0.0.0.255.  """,
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "-w",
        "--workers",
        default=4,
        type=int,
        help="Number of threads used to execute the queries.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for network in args.networks:
            future_to_ip = {
                pool.submit(gethostbyaddr, str(ip)): ip
                for ip in ipaddress.ip_network(network, strict=False).hosts()
            }
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    print(ip, future.result()[0])
                except herror as err:
                    if args.verbose:
                        print(ip, err)


if __name__ == "__main__":
    main()
