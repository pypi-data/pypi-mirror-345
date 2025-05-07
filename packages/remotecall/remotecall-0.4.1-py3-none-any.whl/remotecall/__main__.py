"""
Provides functionality to fetch API definition from a server and generate client code.

Usage:

    Fetch API from server:

        $ python -m remotecall fetch_api http://localhost:8000 --output api.json

    Generate client from JSON:

        $ python -m remotecall generate_client api.json --output client.py

    Generate client from URL:

        $ python -m remotecall generate_client http://localhost:8000 --output client.py
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import typing

from . import fetch_api
from . import generate_client


logger = logging.getLogger(__name__)


DEFAULT_INDENT = 4
DEFAULT_TIMEOUT = 5


def _handle_fetch_api(
        server_url: str,
        cert_file: typing.Optional[str] = None,
        output_file: typing.Optional[str] = None,
        indent: int = DEFAULT_INDENT,
        timeout: int = DEFAULT_TIMEOUT):
    """Handler for fetching API definition."""
    definition = fetch_api(url=server_url, cert_file=cert_file, timeout=timeout)

    # JSON library transforms data to valid ascii objects by default (ensure_ascii=True). Thus,
    # non-ASCII characters are ASCII encoded (e.g., 'Ä' is \u00c4).

    if not output_file:
        print(json.dumps(definition, indent=indent, ensure_ascii=False))
        return

    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(definition, fh, indent=indent, ensure_ascii=True)


def _handle_generate_client(source: str,
                            cert_file: typing.Optional[str] = None,
                            output_file: typing.Optional[str] = None,
                            class_name: typing.Optional[str] = None):
    """Handler for client generation."""
    if source.startswith("http"):
        definition = fetch_api(url=source, cert_file=cert_file)
    else:
        definition = _load_from_json(filename=source)

    source_code = generate_client(definition=definition, class_name=class_name)

    if not output_file:
        print(source_code)
        return

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(source_code)


def _load_from_json(filename: str) -> dict:
    """Load API definition from JSON file."""
    with open(filename, "rb", encoding="utf-8") as fh:
        return json.load(fh)


def main(cli_args):
    """Main"""
    parser = argparse.ArgumentParser(prog=__name__)
    parser.add_argument("command", choices=["fetch_api", "generate_client"])
    parser.add_argument("source")
    parser.add_argument("--output", help="output")
    parser.add_argument("--certificate", help="SLL certificate")
    parser.add_argument("--name", help="Client class name.")

    args = parser.parse_args(cli_args)

    cert_file = os.path.abspath(args.certificate) if args.certificate else None

    if args.command == "fetch_api":
        _handle_fetch_api(server_url=args.source,
                          cert_file=cert_file,
                          output_file=args.output)
    elif args.command == "generate_client":
        _handle_generate_client(source=args.source,
                                cert_file=cert_file,
                                output_file=args.output,
                                class_name=args.name)
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
