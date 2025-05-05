from dataclasses import dataclass
from socket import AddressFamily, SocketKind


@dataclass(frozen=True, slots=True)
class SocketSetup:
    host: str
    port: int | str
    address_family: AddressFamily = AddressFamily.AF_INET
    socket_kind: SocketKind = SocketKind.SOCK_STREAM
