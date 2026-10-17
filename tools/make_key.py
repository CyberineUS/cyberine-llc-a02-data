#!/usr/bin/env python3
"""
Make the key pair that signs declarations.json.

PURPOSE: Writes a new ECDSA P-256 private key to the path given and the matching public key to
keys/declarations-public.pem. Run once, on the signing machine, by the key holder. The private
key never enters this repository.

Copyright (c) 2026 CYBERINE LLC. All rights reserved.
"""
import argparse
import pathlib
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "keys" / "declarations-public.pem"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", required=True, help="where to write the private key (outside the repository)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing public key")
    args = parser.parse_args()
    private_path = pathlib.Path(args.private)
    if private_path.exists():
        print(f"refusing to overwrite {private_path}", file=sys.stderr)
        return 1
    if PUBLIC.exists() and not args.force:
        print(f"{PUBLIC} exists; pass --force to replace it (the app must then ship the new key)", file=sys.stderr)
        return 1
    key = ec.generate_private_key(ec.SECP256R1())
    private_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    PUBLIC.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    print(f"private key: {private_path}\npublic key:  {PUBLIC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
