import socket
import json
import hashlib
from diffiehellmanlib import wrapper
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Custom Exceptions
class HashesDontMatchError(Exception):
    pass

class InvalidRequestError(Exception):
    pass

class ConnectionTimeoutError(Exception):
    pass

# Utility Functions
def calculate_hash(value):
    return hashlib.sha256(str(value).encode()).hexdigest()

def validate_request_time(timeset, tolerance=2):
    current_time = int(time.time())
    if not (current_time - tolerance <= timeset <= current_time + tolerance):
        raise ConnectionTimeoutError("Request timestamp is invalid or expired.")

def validate_hashes(data, hash_values):
    for key, value in data.items():
        expected_hash = hash_values.get(key)
        calculated_hash = calculate_hash(value)
        if expected_hash != calculated_hash:
            raise HashesDontMatchError(f"Hash for {key} does not match.")

def sign_data(private_key, data):
    signature = private_key.sign(
        json.dumps(data).encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, data, signature):
    public_key.verify(
        signature,
        json.dumps(data).encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
# Exchange Functions
def exchange_server(ip, port, target_ip):
    print("Starting server...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip, port))
        server_socket.listen(1)
        print(f"Server listening on {ip}:{port}")

        while True:
            conn, addr = server_socket.accept()
            print(f"Incoming connection from {addr}")
            if addr[0] != target_ip:
                print(f"Rejected connection from {addr[0]}")
                conn.close()
                continue

            try:
                print("Connection accepted.")

                # Generate server's private and public keys
                server_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
                server_public_key = server_private_key.public_key()

                p, g = wrapper.generate_p_g(2048)
                a = wrapper.generate_a_or_b(p, g)
                A = wrapper.generate_A_or_B(p, g, a)

                timeset = int(time.time())
                response = {
                    "error": False,
                    "numbers": {"p": p, "g": g, "A": A},
                    "timeset": timeset,
                    "public_key": server_public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ).decode()
                }

                # Sign the response
                signature = sign_data(server_private_key, response)
                response["signature"] = signature.hex()

                conn.send(json.dumps(response).encode())

                data = conn.recv(4096)
                client_data = json.loads(data.decode())

                if client_data.get("error"):
                    raise InvalidRequestError(client_data.get("message", "Unknown error"))

                validate_request_time(client_data["timeset"])
                validate_hashes(client_data["numbers"], client_data["hashes"])

                # Verify client's signature
                client_public_key = serialization.load_pem_public_key(client_data["public_key"].encode(), backend=default_backend())
                verify_signature(client_public_key, client_data, bytes.fromhex(client_data["signature"]))

                B = client_data["numbers"]["B"]
                shared_key = wrapper.generate_shared_key(B, p, g, a)

                print("Shared key successfully generated: ", shared_key)
                conn.close()
                return shared_key

            except (HashesDontMatchError, ConnectionTimeoutError, InvalidRequestError) as e:
                error_response = {"error": True, "message": str(e)}
                conn.send(json.dumps(error_response).encode())
                conn.close()
                print(f"Error: {e}")

def exchange_client(target_ip, target_port):
    print("Starting client...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((target_ip, target_port))
        print(f"Connected to server at {target_ip}:{target_port}")

        try:
            data = client_socket.recv(4096)
            server_data = json.loads(data.decode())

            if server_data.get("error"):
                raise InvalidRequestError(server_data.get("message", "Unknown error"))

            validate_request_time(server_data["timeset"])
            validate_hashes(server_data["numbers"], server_data["hash"])

            p, g, A = (
                server_data["numbers"]["p"],
                server_data["numbers"]["g"],
                server_data["numbers"]["A"]
            )

            # Generate client's private and public keys
            client_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            client_public_key = client_private_key.public_key()

            b = wrapper.generate_a_or_b(p, g)
            B = wrapper.generate_A_or_B(p, g, b)

            timeset = int(time.time())
            response = {
                "error": False,
                "numbers": {"B": B},
                "hashes": {"B": calculate_hash(B)},
                "timeset": timeset,
                "public_key": client_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
            }

            # Sign the response
            signature = sign_data(client_private_key, response)
            response["signature"] = signature.hex()

            client_socket.send(json.dumps(response).encode())

            shared_key = wrapper.generate_shared_key(A, p, g, b)
            print("Shared key successfully generated: ", shared_key)
            client_socket.close()
            return shared_key

        except (HashesDontMatchError, ConnectionTimeoutError, InvalidRequestError) as e:
            print(f"Error: {e}")
            client_socket.close()
            raise

        finally:
            client_socket.close()
