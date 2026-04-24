"""
demo.py
---------------
Standalone, no-SUMO-required demonstration that the security layer
actually blocks the six attack vectors claimed in the project.

Run this to:
    - Include a screenshot in your report / patent filing
    - Show in an interview
    - Validate the security layer on a machine without SUMO installed

Usage:
    python demo.py
"""

from security.crypto_utils import generate_rsa_keypair
from security.pki import CertificateAuthority
from security.emergency_auth import EmergencyDispatchAuthority
from security.secure_agent import SecureAgent
from security.attack_simulator import run_all_attacks


def main():
    print("=" * 65)
    print("  MARL Traffic Management -- Security Layer Attack Demo")
    print("=" * 65)
    print()

    # Set up PKI as we would for a live run
    ca = CertificateAuthority()
    priv, pub = generate_rsa_keypair()
    cert = ca.issue_certificate("J1", pub)

    eda_priv, eda_pub = generate_rsa_keypair()
    eda = EmergencyDispatchAuthority(eda_priv, eda_pub)

    agent = SecureAgent(
        base_agent=None,
        agent_id="J1",
        private_key=priv,
        certificate=cert,
        ca_cert=ca.certificate,
        peer_public_keys={"agent_A": pub, "J1": pub},
        eda_public_key=eda.public_key,
    )

    print("Running 6 adversarial scenarios...")
    print()

    results = run_all_attacks(agent, priv, pub)

    print(f"{'#':<3}  {'Attack':<28}  {'Result':<12}  {'Detail'}")
    print("-" * 65)
    for i, (name, blocked, detail) in enumerate(results, 1):
        status = "BLOCKED" if blocked else "FAILED"
        marker = "+" if blocked else "!"
        print(f"{marker} {i}  {name:<28}  {status:<12}  {detail}")

    n_blocked = sum(1 for _, b, _ in results if b)
    print()
    print("-" * 65)
    print(f"Summary: {n_blocked}/{len(results)} attacks blocked.")
    if n_blocked == len(results):
        print("All defenses operational.")
    else:
        print("WARNING: at least one defense failed. Investigate immediately.")
    print("=" * 65)


if __name__ == "__main__":
    main()

