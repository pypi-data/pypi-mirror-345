# Grpc Orchestrator SDK
A gRPC-based implementation of the Saga pattern for distributed transactions.

## Features

- Transaction orchestration
- Automatic compensation
- gRPC interface
- gRPC Connection
- Memory storage backends

## Installation

```bash
pip install grpc_orchestrator
```

## Quick Start

```python
from grpc_orchestrator.core.client.client import GrpcOrchestratorClient

client = GrpcOrchestratorClient(orchestrator_host="localhost")
steps = [
    {
        "port": 50052,
        "rpc_method": "CleateOrder",
        "compensation_method": "RollbackOrder",
        "timeout_seconds": 5,
    },
    {
        "port": 50052,
        "rpc_method": "CheckoutOrder",
        "compensation_method": "CheckoutOrder",
        "timeout_seconds": 5,
    },
]
client.start_transaction(transaction_id="1234",steps=steps,payload={
    "id": "1",
    "name":"item1"
})

status = client.get_transaction_status(transaction_id="order_123")
print(status)
```