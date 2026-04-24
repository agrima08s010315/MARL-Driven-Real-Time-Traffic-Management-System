"""
Smoke test: actual TLS 1.3 mTLS handshake between two sockets,
one acting as a traffic controller server, one as a peer agent client.
"""
import socket
import ssl
import threading

from security.crypto_utils import generate_rsa_keypair
from security.pki import CertificateAuthority
from security.secure_channel import SecureChannel


def main():
    ca = CertificateAuthority()

    # Two agents, each with their own keypair + CA-issued cert
    priv_a, pub_a = generate_rsa_keypair()
    priv_b, pub_b = generate_rsa_keypair()
    cert_a = ca.issue_certificate("localhost", pub_a)   # server cert uses hostname
    cert_b = ca.issue_certificate("agent_B", pub_b)

    server_chan = SecureChannel(cert_a, priv_a, ca.certificate, is_server=True)
    client_chan = SecureChannel(cert_b, priv_b, ca.certificate, is_server=False)

    port_holder = {}
    def run_server():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))
        port_holder["port"] = s.getsockname()[1]
        s.listen(1)
        port_holder["ready"].set()
        conn, _ = s.accept()
        with server_chan.wrap_server(conn) as ssock:
            data = ssock.recv(1024)
            port_holder["received"] = data
            port_holder["tls_version"] = ssock.version()
            ssock.sendall(b"ack")
        s.close()

    port_holder["ready"] = threading.Event()
    t = threading.Thread(target=run_server)
    t.start()
    port_holder["ready"].wait()

    # Client connects
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", port_holder["port"]))
    with client_chan.wrap_client(s, server_hostname="localhost") as ssock:
        print(f"TLS version negotiated: {ssock.version()}")
        print(f"Cipher: {ssock.cipher()}")
        ssock.sendall(b"hello from agent_B")
        ack = ssock.recv(1024)
        print(f"Server acknowledged: {ack!r}")

    t.join(timeout=5)
    print(f"Server received: {port_holder.get('received')!r}")
    print(f"Server-side TLS version: {port_holder.get('tls_version')}")

    server_chan.cleanup()
    client_chan.cleanup()


if __name__ == "__main__":
    main()