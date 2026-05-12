from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .console import console
from .inwx_api import DnssecApiInwx
from .isp_dnssec import ISPDnssec


VERSION = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dnssec-sync",
        description="A helper tool to sync DNSSEC information from ISPConfig to INWX domain registry",
    )
    parser.add_argument("--version", action="store_true", help="print version")

    subparsers = parser.add_subparsers(dest="command")

    isp = subparsers.add_parser("isp", help="Load DNSSEC keys from ISPConfig API")
    isp.add_argument("-e", "--export", action="store_true", dest="export_keys", help="Export DNSSEC keys from ISPConfig DNS Zones")

    inwx = subparsers.add_parser("inwx", help="Perform requests on INWX API. Specify at least one option.")
    inwx.add_argument("-s", "--summary", action="store_true", help="Print summary of published keys")
    inwx.add_argument("-r", "--report", action="store_true", help="Print detailed report of published keys")
    inwx.add_argument("-l", "--list", action="store_true", help="Print list of domains known in ISPConfig and INWX")
    inwx.add_argument("-k", "--keylist", metavar="origin", help="Print key data of a specific origin domain")
    inwx.add_argument("-p", "--publish", action="store_true", help="Push all keys from ISPConfig that are not yet published to INWX")
    inwx.add_argument("-c", "--clean", metavar="origin", help="Clean corrupted and orphaned keys for a specific domain")
    inwx.add_argument("--cleanorphans", action="store_true", help="Delete INWX keys that are not known in ISPConfig")
    inwx.add_argument("--cleancorrupt", action="store_true", help="Delete INWX keys that are known in ISPConfig but differ in record details")
    inwx.add_argument("origin", nargs="?", help="Origin Domain of DNS Zone (e.g. domain.tld.)")

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(VERSION)
        return

    if args.command == "isp":
        dnssec_api = ISPDnssec.instance()
        dnssec_api.load_keys()
        if args.export_keys:
            dnssec_api.export_keys()
        return

    if args.command == "inwx":
        selected = [args.summary, args.report, args.list, bool(args.keylist), args.publish, bool(args.clean), args.cleanorphans, args.cleancorrupt]
        if not any(selected):
            console.warning("Please pass options to perform INWX actions")
            print(parser.format_help())
            return
        api = DnssecApiInwx()
        try:
            if args.summary:
                api.print_summary()
            if args.report:
                api.print_report()
            if args.list:
                api.print_domain_list()
            if args.publish:
                api.publish_unpublished_keys()
            if args.clean:
                api.clean_corrupted_keys(args.clean)
                api.clean_orphaned_keys(args.clean)
            if args.cleanorphans:
                api.clean_orphaned_keys()
            if args.cleancorrupt:
                api.clean_corrupted_keys()
            if args.keylist:
                api.print_zone_keys(args.keylist)
        finally:
            api.close()
        return

    print(parser.format_help())
