import socket
from random import randint


def is_port_available(port: int, host: str) -> bool:
    """Check if a port is available on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) != 0


def find_available_port(
    start_port: int = 8501,
    max_port: int = 65535,
    host: str = "localhost",
) -> int:
    """Find an available port on the given host starting from start_port."""
    port = start_port
    while port <= max_port:
        if is_port_available(port, host):
            return port
        port += 1
    raise RuntimeError("Unable to find an available port.")


if __name__ == "__main__":
    print(find_available_port())
