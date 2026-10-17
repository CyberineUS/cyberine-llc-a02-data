#!/usr/bin/env python3
"""
Verify declarations.json against its signature and the published public key.

PURPOSE: Exits 0 when declarations.json.sig verifies for the exact bytes of declarations.json
with keys/declarations-public.pem, and 1 otherwise. Also checks the file against the schema when
the jsonschema package is installed.

Copyright (c) 2026 CYBERINE LLC. All rights reserved.
"""
import base64
import json
import pathlib
import sys

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "declarations.json"
SIG = ROOT / "declarations.json.sig"
PUBLIC = ROOT / "keys" / "declarations-public.pem"
SCHEMA = ROOT / "schema" / "declarations.schema.json"


def main() -> int:
    key = serialization.load_pem_public_key(PUBLIC.read_bytes())
    signature = base64.b64decode(SIG.read_text().strip())
    try:
        key.verify(signature, DATA.read_bytes(), ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        print("signature does NOT verify", file=sys.stderr)
        return 1
    print("signature verifies")
    try:
        import jsonschema
    except ImportError:
        print("schema not checked (pip install jsonschema)")
        return 0
    jsonschema.validate(json.loads(DATA.read_text(encoding="utf-8")), json.loads(SCHEMA.read_text()))
    print("schema ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
