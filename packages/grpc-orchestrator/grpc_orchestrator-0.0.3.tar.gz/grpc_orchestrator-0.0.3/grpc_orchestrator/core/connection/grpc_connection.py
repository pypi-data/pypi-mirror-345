
from typing import Any
from grpc_orchestrator.core.connection.manager import ConnectionManager


class GrpcConnection:
    def __init__(self, grpc_server_add: str):
        self.conn_manager = ConnectionManager(grpc_server_add)
    def __enter__(self):
        self.conn_manager.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn_manager.close()
    def get_stub(self,service_name: str,stub_class):
        return self.conn_manager.get_stub(service_name,stub_class)