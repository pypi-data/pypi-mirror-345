from typing import Dict
import asyncio
from typing import Any
import grpc


class ConnectionManager:
    def __init__(self,address: str,max_retries: int = 3,timeout: int = 30):
        self.address = address
        self.max_retries = max_retries
        self.timeout = timeout
        self._channel = None
        self._stubs: Dict[str, Any] = {}

    def connect(self):
        """Establish gRPC connection with retry logic"""
        if self._channel is not None:
            return
        """Do Connection"""
        retry_count = 0
        last_error = None
        while retry_count < self.max_retries:
            try:
                self._channel = grpc.insecure_channel(
                    target=self.address,
                    options=[
                        ("grpc.keepalive_time_ms", 10000),
                        ("grpc.keepalive_timeout_ms", 5000),
                    ],
                )
                # Verify connection is actually working
                grpc.channel_ready_future(self._channel).result(timeout=self.timeout)
                return
            except grpc.RpcError as e:
                last_error = e
                retry_count += 1
                import time
                time.sleep(1 * retry_count)

        raise ConnectionError(
            f"Failed to connect to {self.address} after {self.max_retries} attempts"
        ) from last_error

    def get_stub(self, service_name: str, stub_class):
        """Get or create a gRPC stub with lazy initialization"""
        if service_name not in self._stubs:
            if self._channel is None:
                self.connect()
            self._stubs[service_name] = stub_class(self._channel)
        return self._stubs[service_name]

    def close(self):
        """
        Cleanly close the connection
        """
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stubs.clear()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
