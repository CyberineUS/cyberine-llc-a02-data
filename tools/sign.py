#!/usr/bin/env python3
"""
Sign declarations.json.

PURPOSE: Writes declarations.json.sig, the base64 ECDSA P-256 / SHA-256 signature over the exact
bytes of declarations.json, using the private key at the path given.

Copyright (c) 2026 CYBERINE LLC. All rights reserved.
"""
import argparse
import base64
import pathlib
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "declarations.json"
SIG = ROOT / "declarations.json.sig"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True, help="path to the private key")
    args = parser.parse_args()
    key = serialization.load_pem_private_key(pathlib.Path(args.key).read_bytes(), password=None)
    signature = key.sign(DATA.read_bytes(), ec.ECDSA(hashes.SHA256()))
    SIG.write_text(base64.b64encode(signature).decode("ascii") + "\n")
    print(f"signed {DATA.name} ({DATA.stat().st_size} bytes) -> {SIG.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
