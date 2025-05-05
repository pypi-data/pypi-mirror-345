# TODO: Implement `Client` mixin class for `charz_core.Engine`

from socket import socket as Socket
from typing import Any

from charz_core import Self

from ._socket_setup import SocketSetup


class Client:  # Component (mixin class)
    socket_setup: SocketSetup
    _socket: Socket  # Read-only

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        instance._socket = Socket(
            instance.socket_setup.address_family,
            instance.socket_setup.socket_kind,
        )
        instance.socket.connect(instance.address)
        return instance

    @property
    def socket(self) -> Socket:
        return self._socket

    @property
    def address(self) -> tuple[str, int | str]:
        return (self.socket_setup.host, self.socket_setup.port)
