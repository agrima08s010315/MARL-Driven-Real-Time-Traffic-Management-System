"""
generate_keys.py
----------------
One-time bootstrap script.

Run this ONCE before starting the secure simulation. It will:

    1. Create a Certificate Authority (CA) for the traffic network.
    2. Generate an RSA keypair and CA-signed certificate for each
       traffic light / intersection agent.
    3. Generate keys for the Emergency Dispatch Authority (EDA).
    4. Write everything to `keys/` as PEM files.

Usage:
    python generate_keys.py --agents J1 J2 J3 J4
"""

import argparse
import os
from cryptography.hazmat.primitives import serialization

from security.crypto_utils import (
    generate_rsa_keypair, serialize_private_key, serialize_public_key,
)
from security.pki import CertificateAuthority


KEYS_DIR = "keys"


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def write_bytes(path: str, data: bytes, mode: int = 0o644):
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, mode)


def main():
    parser = argparse.ArgumentParser(description="Bootstrap PKI for TrafficNet.")
    parser.add_argument(
        "--agents", nargs="+", required=True,
        help="Space-separated list of agent IDs (e.g. J1 J2 J3)."
    )
    args = parser.parse_args()

    ensure_dir(KEYS_DIR)
    ensure_dir(os.path.join(KEYS_DIR, "agents"))

    # ---------------- Certificate Authority ----------------
    print("[1/3] Generating Root CA ...")
    ca = CertificateAuthority()
    write_bytes(
        os.path.join(KEYS_DIR, "ca_cert.pem"),
        ca.certificate.public_bytes(serialization.Encoding.PEM),
    )
    write_bytes(
        os.path.join(KEYS_DIR, "ca_key.pem"),
        serialize_private_key(ca.private_key),
        mode=0o600,
    )
    print(f"     -> keys/ca_cert.pem, keys/ca_key.pem")

    # ---------------- Per-agent keys ----------------
    print(f"[2/3] Issuing certificates for {len(args.agents)} agents ...")
    for agent_id in args.agents:
        priv, pub = generate_rsa_keypair()
        cert = ca.issue_certificate(agent_id, pub)

        agent_dir = os.path.join(KEYS_DIR, "agents", agent_id)
        ensure_dir(agent_dir)

        write_bytes(
            os.path.join(agent_dir, "private.pem"),
            serialize_private_key(priv),
            mode=0o600,
        )
        write_bytes(
            os.path.join(agent_dir, "public.pem"),
            serialize_public_key(pub),
        )
        write_bytes(
            os.path.join(agent_dir, "cert.pem"),
            cert.public_bytes(serialization.Encoding.PEM),
        )
        print(f"     -> keys/agents/{agent_id}/")

    # ---------------- Emergency Dispatch Authority ----------------
    print("[3/3] Generating Emergency Dispatch Authority keys ...")
    eda_priv, eda_pub = generate_rsa_keypair()
    ensure_dir(os.path.join(KEYS_DIR, "eda"))
    write_bytes(
        os.path.join(KEYS_DIR, "eda", "private.pem"),
        serialize_private_key(eda_priv),
        mode=0o600,
    )
    write_bytes(
        os.path.join(KEYS_DIR, "eda", "public.pem"),
        serialize_public_key(eda_pub),
    )
    print(f"     -> keys/eda/")

    print("\nPKI bootstrap complete.")
    print("Private keys are in keys/ with 0600 perms. These must never be committed to git.")


if __name__ == "__main__":
    main()